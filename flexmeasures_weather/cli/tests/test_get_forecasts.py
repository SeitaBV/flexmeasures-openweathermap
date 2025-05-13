import logging

from flexmeasures.data.models.time_series import TimedBelief

from ..commands import collect_weather_data
from ...utils import weather
from .utils import mock_owm_response


"""
Useful resource: https://flask.palletsprojects.com/en/2.0.x/testing/#testing-cli-commands
"""


def test_get_weather_forecasts_to_db(
    app, fresh_db, monkeypatch, run_as_cli, add_weather_sensors_fresh_db
):
    """
    Test if we can process forecast and save them to the database.
    """
    wind_sensor = add_weather_sensors_fresh_db["wind"]
    fresh_db.session.flush()
    wind_sensor_id = wind_sensor.id
    weather_station = wind_sensor.generic_asset

    monkeypatch.setitem(app.config, "WEATHERAPI_KEY", "dummy")
    monkeypatch.setattr(weather, "call_openweatherapi", mock_owm_response)

    runner = app.test_cli_runner()
    result = runner.invoke(
        collect_weather_data,
        ["--location", f"{weather_station.latitude},{weather_station.longitude}"],
    )
    print(result.output)
    assert "Reported task get-weather-forecasts status as True" in result.output

    beliefs = (
        fresh_db.session.query(TimedBelief)
        .filter(TimedBelief.sensor_id == wind_sensor_id)
        .all()
    )
    assert len(beliefs) == 2
    for wind_speed in (100, 90):
        assert wind_speed in [belief.event_value for belief in beliefs]


def test_get_weather_forecasts_no_close_sensors(
    app, db, monkeypatch, run_as_cli, add_weather_sensors_fresh_db, caplog
):
    """
    Looking for a location too far away from existing weather station.
    Check we get a warning.
    """
    weather_station = add_weather_sensors_fresh_db["wind"].generic_asset

    monkeypatch.setitem(app.config, "WEATHERAPI_KEY", "dummy")
    monkeypatch.setattr(weather, "call_openweatherapi", mock_owm_response)

    runner = app.test_cli_runner()
    with caplog.at_level(logging.WARNING):
        result = runner.invoke(
            collect_weather_data,
            ["--location", f"{weather_station.latitude-5},{weather_station.longitude}"],
        )
        print(result.output)
        assert (
            "Reported task get-weather-forecasts status as True" in result.output
        )
        assert "no sufficiently close weather sensor found" in caplog.text
