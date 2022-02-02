import pytest
from flexmeasures.data.models.time_series import Sensor

from ..commands import add_weather_sensor


"""
Useful resource: https://flask.palletsprojects.com/en/2.0.x/testing/#testing-cli-commands
"""

sensor_params = {"name": "wind_speed", "latitude": 30, "longitude": 40, "unit": "m/s"}


@pytest.mark.parametrize(
    "invalid_param, invalid_value, expected_msg",
    [
        ("timezone", "Erope/Amsterdam", "is unknown"),
        ("latitude", 93, "less than or equal to 90"),
        ("unit", "CC", "cannot be handled"),
    ],
)
def test_register_weather_sensor_invalid_data(
    app, db, invalid_param, invalid_value, expected_msg
):
    test_sensor_params = sensor_params.copy()
    test_sensor_params[invalid_param] = invalid_value
    cli_params = []
    for k, v in test_sensor_params.items():
        cli_params.append(f"--{k}")
        cli_params.append(v)
    runner = app.test_cli_runner()
    result = runner.invoke(add_weather_sensor, cli_params)
    assert "Aborted" in result.output
    assert expected_msg in result.output


def test_register_weather_sensor(app, db):
    cli_params = []
    for k, v in sensor_params.items():
        cli_params.append(f"--{k}")
        cli_params.append(v)
    runner = app.test_cli_runner()
    result = runner.invoke(add_weather_sensor, cli_params)
    assert "XYZ" in result.output
    sensor = Sensor.query.filter(Sensor.name == sensor_params["name"]).one_or_none()
    assert sensor is not None
