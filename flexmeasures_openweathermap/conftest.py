from typing import Dict
from datetime import timedelta

import pytest

from flexmeasures.app import create as create_flexmeasures_app
from flexmeasures.data.models.time_series import Sensor
from flexmeasures.data.models.generic_assets import GenericAsset, GenericAssetType
from flexmeasures.conftest import db, fresh_db  # noqa: F401

from . import WEATHER_STATION_TYPE_NAME


@pytest.fixture(scope="session")
def app():
    print("APP FIXTURE")

    # Adding this plugin, making sure the name is known (as last part of plugin path)
    test_app = create_flexmeasures_app(
        env="testing", plugins=["../flexmeasures_openweathermap"]
    )

    # Establish an application context before running the tests.
    ctx = test_app.app_context()
    ctx.push()

    yield test_app

    ctx.pop()

    print("DONE WITH APP FIXTURE")


@pytest.fixture(scope="module")
def register_weather_sensors(db):  # noqa: F811
    return create_weather_sensors(db)


@pytest.fixture(scope="module")
def register_weather_sensors_fresh_db(fresh_db):  # noqa: F811
    return create_weather_sensors(fresh_db)


def create_weather_sensors(the_db) -> Dict[str, Sensor]:
    """Create one weather station with two supported weather sensors."""
    weather_station_type = GenericAssetType(name=WEATHER_STATION_TYPE_NAME)
    the_db.session.add(weather_station_type)
    weather_station = GenericAsset(
        name="Test weather station",
        generic_asset_type=weather_station_type,
        latitude=33.4843866,
        longitude=126,
    )
    the_db.session.add(weather_station)

    wind_sensor = Sensor(
        name="wind_speed",
        generic_asset=weather_station,
        event_resolution=timedelta(minutes=60),
        unit="m/s",
    )
    the_db.session.add(wind_sensor)

    temp_sensor = Sensor(
        name="temperature",
        generic_asset=weather_station,
        event_resolution=timedelta(minutes=60),
        unit="°C",
    )
    the_db.session.add(temp_sensor)
    return {"wind_speed": wind_sensor, "temperature": temp_sensor}
