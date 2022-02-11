from typing import Tuple, List, Dict, Optional
import os
from datetime import datetime
import json

import click
from flask import current_app
import requests
from timely_beliefs import BeliefsDataFrame
from flexmeasures.utils.time_utils import as_server_time, get_timezone
from flexmeasures.utils.geo_utils import compute_irradiance
from flexmeasures.data.models.data_sources import DataSource
from flexmeasures.data.models.time_series import Sensor, TimedBelief
from flexmeasures.data.utils import save_to_db

from .locating import find_weather_sensor_by_location_or_fail


# This maps sensor name/unit pairs we can use in FlexMeasures to OWM labels.
# We also store seasonality attributes here.
# Of course, the sensor names we use in FM need to be unique.
owm_to_sensor_map = dict(
    temp={
        "name": "temperature",
        "unit": "°C",
        "seasonality": {
            "daily_seasonality": True,
            "weekly_seasonality": False,
            "yearly_seasonality": True,
        },
    },
    wind_speed={
        "name": "wind_speed",
        "unit": "m/s",
        "seasonality": {
            "daily_seasonality": True,
            "weekly_seasonality": False,
            "yearly_seasonality": True,
        },
    },
    clouds={
        "name": "radiation",
        "unit": "kW/m²",
        "seasonality": {
            "daily_seasonality": True,
            "weekly_seasonality": False,
            "yearly_seasonality": True,
        },
    },
)


def get_supported_sensor_spec(name: str) -> Optional[dict]:
    """
    Find the specs from a sensor by name.
    """
    for supported_sensor_spec in owm_to_sensor_map.values():
        if supported_sensor_spec["name"] == name:
            return supported_sensor_spec
    return None


def get_supported_sensors_str() -> str:
    """ A string - list of supported sensors, also revealing their unit"""
    return ", ".join([f"{o['name']} ({o['unit']})" for o in owm_to_sensor_map.values()])


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
    data_source: DataSource,
    max_degree_difference_for_nearest_weather_sensor: int = 2,
):
    """Process the response from OpenWeatherMap API into Weather timed values.
    Collects all forecasts for all locations and all sensors at all locations, then bulk-saves them.
    """
    click.echo("[FLEXMEASURES] Getting weather forecasts:")
    click.echo("[FLEXMEASURES]  Latitude, Longitude")
    click.echo("[FLEXMEASURES] -----------------------")

    for location in locations:
        click.echo("[FLEXMEASURES] %s, %s" % location)
        weather_sensors: Dict[
            str, Sensor
        ] = {}  # keep track of the sensors to save lookups
        db_forecasts: Dict[Sensor, List[TimedBelief]] = {}  # collect beliefs per sensor

        time_of_api_call, forecasts = call_openweatherapi(api_key, location)
        click.echo(
            "[FLEXMEASURES] Called OpenWeatherMap API successfully at %s."
            % time_of_api_call
        )

        # loop through forecasts, including the one of current hour (horizon 0)
        for fc in forecasts:
            fc_datetime = as_server_time(
                datetime.fromtimestamp(fc["dt"], get_timezone())
            ).replace(second=0, microsecond=0)
            fc_horizon = fc_datetime - time_of_api_call
            click.echo(
                "[FLEXMEASURES] Processing forecast for %s (horizon: %s) ..."
                % (fc_datetime, fc_horizon)
            )
            for owm_response_label in owm_to_sensor_map:
                sensor_name = str(owm_to_sensor_map[owm_response_label]["name"])
                if owm_response_label in fc:
                    if sensor_name in weather_sensors:
                        weather_sensor = weather_sensors[sensor_name]
                    else:
                        weather_sensor = find_weather_sensor_by_location_or_fail(
                            location,
                            max_degree_difference_for_nearest_weather_sensor,
                            sensor_name=sensor_name,
                        )
                        weather_sensors[sensor_name] = weather_sensor
                    if weather_sensor not in db_forecasts.keys():
                        db_forecasts[weather_sensor] = []

                    fc_value = fc[owm_response_label]
                    # the radiation is not available in OWM -> we compute it ourselves
                    if sensor_name == "radiation":
                        fc_value = compute_irradiance(
                            location[0],
                            location[1],
                            fc_datetime,
                            # OWM sends cloud coverage in percent, we need a ratio
                            fc_value / 100.0,
                        )

                    db_forecasts[weather_sensor].append(
                        TimedBelief(
                            event_start=fc_datetime,
                            belief_horizon=fc_horizon,
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
                    click.echo("[FLEXMEASURES] %s" % msg)
                    current_app.logger.warning(msg)
    for sensor in db_forecasts.keys():
        click.echo(f"Saving {sensor.name} forecasts ...")
        if len(db_forecasts[sensor]) == 0:
            # This is probably a serious problem
            raise Exception(
                "Nothing to put in the database was produced. That does not seem right..."
            )
        status = save_to_db(BeliefsDataFrame(db_forecasts[sensor]))
        if status == "success_but_nothing_new":
            current_app.logger.info(
                "Done. These beliefs had already been saved before."
            )
        elif status == "success_with_unchanged_beliefs_skipped":
            current_app.logger.info("Done. Some beliefs had already been saved before.")


def save_forecasts_as_json(
    api_key: str, locations: List[Tuple[float, float]], data_path: str
):
    """Get forecasts, then store each as a raw JSON file, for later processing."""
    click.echo("[FLEXMEASURES] Getting weather forecasts:")
    click.echo("[FLEXMEASURES]  Latitude, Longitude")
    click.echo("[FLEXMEASURES]  ----------------------")
    for location in locations:
        click.echo("[FLEXMEASURES] %s, %s" % location)
        time_of_api_call, forecasts = call_openweatherapi(api_key, location)
        now_str = time_of_api_call.strftime("%Y-%m-%dT%H-%M-%S")
        path_to_files = os.path.join(data_path, now_str)
        if not os.path.exists(path_to_files):
            click.echo(f"Making directory: {path_to_files} ...")
            os.mkdir(path_to_files)
        forecasts_file = "%s/forecast_lat_%s_lng_%s.json" % (
            path_to_files,
            str(location[0]),
            str(location[1]),
        )
        with open(forecasts_file, "w") as outfile:
            json.dump(forecasts, outfile)