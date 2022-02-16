from flexmeasures.data.models.time_series import TimedBelief

from ..commands import collect_weather_data
from ...utils import owm
from .utils import mock_owm_response


"""
Useful resource: https://flask.palletsprojects.com/en/2.0.x/testing/#testing-cli-commands
"""


def test_get_weather_forecasts_to_db(
    app, fresh_db, monkeypatch, add_weather_sensors_fresh_db
):
    """
    Test if we can process forecast and save them to the database.
    """
    fresh_db.session.flush()
    wind_sensor_id = add_weather_sensors_fresh_db["wind"].id
    wind_sensor_lat = add_weather_sensors_fresh_db["wind"].generic_asset.latitude
    wind_sensor_long = add_weather_sensors_fresh_db["wind"].generic_asset.longitude

    monkeypatch.setitem(app.config, "OPENWEATHERMAP_API_KEY", "dummy")
    monkeypatch.setattr(owm, "call_openweatherapi", mock_owm_response)

    runner = app.test_cli_runner()
    result = runner.invoke(
        collect_weather_data, ["--location", f"{wind_sensor_lat},{wind_sensor_long}"]
    )
    print(result.output)
    assert "Reported task get-openweathermap-forecasts status as True" in result.output

    beliefs = (
        fresh_db.session.query(TimedBelief)
        .filter(TimedBelief.sensor_id == wind_sensor_id)
        .all()
    )
    assert len(beliefs) == 2
    for wind_speed in (100, 90):
        assert wind_speed in [belief.event_value for belief in beliefs]


def test_get_weather_forecasts_no_close_sensors(
    app, db, monkeypatch, add_weather_sensors_fresh_db
):
    """
    Looking for a location too far away from existing weather stations means we fail.
    """
    wind_sensor_lat = add_weather_sensors_fresh_db["wind"].generic_asset.latitude
    wind_sensor_long = add_weather_sensors_fresh_db["wind"].generic_asset.longitude

    monkeypatch.setitem(app.config, "OPENWEATHERMAP_API_KEY", "dummy")
    monkeypatch.setattr(owm, "call_openweatherapi", mock_owm_response)

    runner = app.test_cli_runner()
    result = runner.invoke(
        collect_weather_data, ["--location", f"{wind_sensor_lat-5},{wind_sensor_long}"]
    )
    print(result.output)
    assert "Reported task get-openweathermap-forecasts status as False" in result.output
    assert "No sufficiently close weather sensor found" in result.output
