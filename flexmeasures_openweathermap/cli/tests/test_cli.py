from typing import List

import pytest
from flexmeasures.data.models.time_series import Sensor

from ..commands import add_weather_sensor


"""
Useful resource: https://flask.palletsprojects.com/en/2.0.x/testing/#testing-cli-commands
"""

sensor_params = {"name": "wind_speed", "latitude": 30, "longitude": 40, "unit": "m/s"}


def cli_params_from_dict(d) -> List[str]:
    cli_params = []
    for k, v in d.items():
        cli_params.append(f"--{k}")
        cli_params.append(v)
    return cli_params


@pytest.mark.parametrize(
    "invalid_param, invalid_value, expected_msg",
    [
        ("timezone", "Erope/Amsterdam", "is unknown"),
        ("latitude", 93, "less than or equal to 90"),
        ("unit", "not-a-valid-unit", "cannot be handled"),
        ("unit", "kWh", "not supported"),  # not in combinaton with wind_speed
    ],
)
def test_register_weather_sensor_invalid_data(
    app, db, invalid_param, invalid_value, expected_msg
):
    test_sensor_params = sensor_params.copy()
    test_sensor_params[invalid_param] = invalid_value
    runner = app.test_cli_runner()
    result = runner.invoke(add_weather_sensor, cli_params_from_dict(test_sensor_params))
    assert "Aborted" in result.output
    assert expected_msg in result.output


def test_register_weather_sensor(app, fresh_db):
    runner = app.test_cli_runner()
    result = runner.invoke(add_weather_sensor, cli_params_from_dict(sensor_params))
    assert "Successfully created weather sensor with ID" in result.output
    sensor = Sensor.query.filter(Sensor.name == sensor_params["name"]).one_or_none()
    assert sensor is not None


def test_register_weather_sensor_twice(app, fresh_db):
    runner = app.test_cli_runner()
    result = runner.invoke(add_weather_sensor, cli_params_from_dict(sensor_params))
    assert "Successfully created weather sensor with ID" in result.output
    result = runner.invoke(add_weather_sensor, cli_params_from_dict(sensor_params))
    assert "already exists" in result.output
