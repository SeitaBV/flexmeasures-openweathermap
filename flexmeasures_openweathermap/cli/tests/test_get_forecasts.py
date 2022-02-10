from datetime import datetime, timedelta

from flexmeasures.data.models.time_series import TimedBelief
from flexmeasures.utils.time_utils import as_server_time, get_timezone

from ..commands import collect_weather_data
from ...utils import owm


"""
Useful resource: https://flask.palletsprojects.com/en/2.0.x/testing/#testing-cli-commands
"""

sensor_params = {"name": "wind_speed", "latitude": 30, "longitude": 40}


def test_get_weather_forecasts_to_db(app, db, monkeypatch, register_weather_sensors):
    """ Test if we can process forecast and save them to the database."""
    db.session.flush()
    wind_sensor_id = register_weather_sensors["wind_speed"].id

    def mock_owm_response(api_key, location):
        mock_date = datetime.now()
        mock_date_tz_aware = as_server_time(
            datetime.fromtimestamp(mock_date.timestamp(), tz=get_timezone())
        ).replace(second=0, microsecond=0)
        return mock_date_tz_aware, [
            {"dt": mock_date.timestamp(), "temp": 40, "wind_speed": 100},
            {
                "dt": (mock_date + timedelta(hours=1)).timestamp(),
                "temp": 42,
                "wind_speed": 90,
            },
        ]

    monkeypatch.setenv("OPENWEATHERMAP_API_KEY", "dummy")
    monkeypatch.setattr(owm, "call_openweatherapi", mock_owm_response)

    runner = app.test_cli_runner()
    result = runner.invoke(collect_weather_data, ["--location", "33.484,126"])
    print(result.output)
    assert "Reported task get-openweathermap-forecasts status as True" in result.output

    beliefs = (
        db.session.query(TimedBelief)
        .filter(TimedBelief.sensor_id == wind_sensor_id)
        .all()
    )
    assert len(beliefs) == 2
    for wind_speed in (100, 90):
        assert wind_speed in [belief.event_value for belief in beliefs]
