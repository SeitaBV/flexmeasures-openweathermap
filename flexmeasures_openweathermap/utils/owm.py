from typing import Tuple, List, Dict, Optional
import os
from datetime import datetime, timedelta
import json

import click
from flask import current_app
import requests
from humanize import naturaldelta
from timely_beliefs import BeliefsDataFrame
from flexmeasures.utils.time_utils import as_server_time, get_timezone, server_now
from flexmeasures.data.models.time_series import Sensor, TimedBelief
from flexmeasures.data.utils import save_to_db

from .locating import find_weather_sensor_by_location_or_fail
from ..sensor_specs import mapping
from .modeling import (
    get_or_create_owm_data_source,
    get_or_create_owm_data_source_for_derived_data,
)
from .radiating import compute_irradiance


def get_supported_sensor_spec(name: str) -> Optional[dict]:
    """
    Find the specs from a sensor by name.
    """
    for supported_sensor_spec in mapping:
        if supported_sensor_spec["fm_sensor_name"] == name:
            return supported_sensor_spec.copy()
    return None


def get_supported_sensors_str() -> str:
    """A string - list of supported sensors, also revealing their unit"""
    return ", ".join(
        [
            f"{sensor_specs['fm_sensor_name']} ({sensor_specs['unit']})"
            for sensor_specs in mapping
        ]
    )


def call_openweatherapi(
    api_key: str, location: Tuple[float, float]
) -> Tuple[datetime, List[Dict]]:
    """
    Make a single "one-call" to the Open Weather API and return the API timestamp as well as the 48 hourly forecasts.
    See https://openweathermap.org/api/one-call-api for docs.
    Note that the first forecast is about the current hour.
    """
    query_str = f"lat={location[0]}&lon={location[1]}&units=metric&exclude=minutely,daily,alerts&appid={api_key}"
    res = requests.get(f"http://api.openweathermap.org/data/2.5/onecall?{query_str}")
    assert (
        res.status_code == 200
    ), f"OpenWeatherMap returned status code {res.status_code}: {res.text}"
    data = res.json()
    time_of_api_call = as_server_time(
        datetime.fromtimestamp(data["current"]["dt"], tz=get_timezone())
    ).replace(second=0, microsecond=0)
    return time_of_api_call, data["hourly"]


def save_forecasts_in_db(
    api_key: str,
    locations: List[Tuple[float, float]],
    max_degree_difference_for_nearest_weather_sensor: int = 2,
):
    """Process the response from OpenWeatherMap API into timed beliefs.
    Collects all forecasts for all locations and all sensors at all locations, then bulk-saves them.
    """
    click.echo("[FLEXMEASURES-OWM] Getting weather forecasts:")
    click.echo("[FLEXMEASURES-OWM] Latitude, Longitude")
    click.echo("[FLEXMEASURES-OWM] -----------------------")

    for location in locations:
        click.echo("[FLEXMEASURES] %s, %s" % location)
        weather_sensors: Dict[
            str, Sensor
        ] = {}  # keep track of the sensors to save lookups
        db_forecasts: Dict[Sensor, List[TimedBelief]] = {}  # collect beliefs per sensor

        now = server_now()
        owm_time_of_api_call, forecasts = call_openweatherapi(api_key, location)
        diff_fm_owm = now - owm_time_of_api_call
        if abs(diff_fm_owm) > timedelta(minutes=10):
            click.echo(
                f"[FLEXMEASURES-OWM] Warning: difference between this server and OWM is {naturaldelta(diff_fm_owm)}"
            )
        click.echo(
            f"[FLEXMEASURES-OWM] Called OpenWeatherMap API successfully at {now}."
        )

        # loop through forecasts, including the one of current hour (horizon 0)
        for fc in forecasts:
            fc_datetime = as_server_time(
                datetime.fromtimestamp(fc["dt"], get_timezone())
            )
            click.echo(f"[FLEXMEASURES-OWM] Processing forecast for {fc_datetime} ...")
            for sensor_specs in mapping:
                data_source = get_or_create_owm_data_source()
                sensor_name = str(sensor_specs["fm_sensor_name"])
                owm_response_label = sensor_specs["owm_sensor_name"]
                if owm_response_label in fc:
                    weather_sensor = get_weather_sensor(
                        sensor_specs,
                        location,
                        weather_sensors,
                        max_degree_difference_for_nearest_weather_sensor,
                    )
                    if weather_sensor is not None:
                        if weather_sensor not in db_forecasts.keys():
                            db_forecasts[weather_sensor] = []

                        fc_value = fc[owm_response_label]

                        # the irradiance is not available in OWM -> we compute it ourselves
                        if sensor_name == "irradiance":
                            fc_value = compute_irradiance(
                                location[0],
                                location[1],
                                fc_datetime,
                                # OWM sends cloud cover in percent, we need a ratio
                                fc_value / 100.0,
                            )
                            data_source = (
                                get_or_create_owm_data_source_for_derived_data()
                            )

                        db_forecasts[weather_sensor].append(
                            TimedBelief(
                                event_start=fc_datetime,
                                belief_time=now,
                                event_value=fc_value,
                                sensor=weather_sensor,
                                source=data_source,
                            )
                        )
                else:
                    # we will not fail here, but issue a warning
                    msg = "No label '%s' in response data for time %s" % (
                        owm_response_label,
                        fc_datetime,
                    )
                    click.echo("[FLEXMEASURES-OWM] %s" % msg)
                    current_app.logger.warning(msg)
    for sensor in db_forecasts.keys():
        click.echo(f"[FLEXMEASURES-OWM] Saving {sensor.name} forecasts ...")
        if len(db_forecasts[sensor]) == 0:
            # This is probably a serious problem
            raise Exception(
                "Nothing to put in the database was produced. That does not seem right..."
            )
        status = save_to_db(BeliefsDataFrame(db_forecasts[sensor]))
        if status == "success_but_nothing_new":
            current_app.logger.info(
                "[FLEXMEASURES-OWM] Done. These beliefs had already been saved before."
            )
        elif status == "success_with_unchanged_beliefs_skipped":
            current_app.logger.info(
                "[FLEXMEASURES-OWM] Done. Some beliefs had already been saved before."
            )


def get_weather_sensor(
    sensor_specs: dict,
    location: Tuple[float, float],
    weather_sensors: Dict[str, Sensor],
    max_degree_difference_for_nearest_weather_sensor: int,
) -> Sensor:
    """Get the weather sensor for this own response label and location, if we haven't retrieved it already."""
    sensor_name = str(sensor_specs["fm_sensor_name"])
    if sensor_name in weather_sensors:
        weather_sensor = weather_sensors[sensor_name]
    else:
        weather_sensor = find_weather_sensor_by_location_or_fail(
            location,
            max_degree_difference_for_nearest_weather_sensor,
            sensor_name=sensor_name,
        )
        weather_sensors[sensor_name] = weather_sensor
    if (
        weather_sensor is not None
        and weather_sensor.event_resolution != sensor_specs["event_resolution"]
    ):
        raise Exception(
            f"[FLEXMEASURES-OWM] The weather sensor found for {sensor_name} has an unfitting event resolution (should be {sensor_specs['event_resolution']}, but is {weather_sensor.event_resolution}."
        )
    return weather_sensor


def save_forecasts_as_json(
    api_key: str, locations: List[Tuple[float, float]], data_path: str
):
    """Get forecasts, then store each as a raw JSON file, for later processing."""
    click.echo("[FLEXMEASURES-OWM] Getting weather forecasts:")
    click.echo("[FLEXMEASURES-OWM] Latitude, Longitude")
    click.echo("[FLEXMEASURES-OWM] ----------------------")
    for location in locations:
        click.echo("[FLEXMEASURES-OWM] %s, %s" % location)
        now = server_now()
        owm_time_of_api_call, forecasts = call_openweatherapi(api_key, location)
        diff_fm_owm = now - owm_time_of_api_call
        if abs(diff_fm_owm) > timedelta(minutes=10):
            click.echo(
                f"[FLEXMEASURES-OWM] Warning: difference between this server and OWM is {naturaldelta(diff_fm_owm)}"
            )
        now_str = now.strftime("%Y-%m-%dT%H-%M-%S")
        path_to_files = os.path.join(data_path, now_str)
        if not os.path.exists(path_to_files):
            click.echo(f"[FLEXMEASURES-OWM] Making directory: {path_to_files} ...")
            os.mkdir(path_to_files)
        forecasts_file = "%s/forecast_lat_%s_lng_%s.json" % (
            path_to_files,
            str(location[0]),
            str(location[1]),
        )
        with open(forecasts_file, "w") as outfile:
            json.dump(forecasts, outfile)
