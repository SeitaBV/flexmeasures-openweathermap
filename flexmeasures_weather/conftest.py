from typing import Dict
from datetime import timedelta

import pytest
from flask_sqlalchemy import SQLAlchemy
from flexmeasures.app import create as create_flexmeasures_app
from flexmeasures.conftest import db, fresh_db  # noqa: F401
from flexmeasures.data.models.generic_assets import GenericAsset, GenericAssetType
from flexmeasures.data.models.time_series import Sensor

from flexmeasures_weather import WEATHER_STATION_TYPE_NAME


@pytest.fixture(scope="session")
def app():
    print("APP FIXTURE")

    # Adding this plugin, making sure the name is known (as last part of plugin path)
    test_app = create_flexmeasures_app(
        env="testing", plugins=["../flexmeasures_weather"]
    )

    # Establish an application context before running the tests.
    ctx = test_app.app_context()
    ctx.push()

    yield test_app

    ctx.pop()

    print("DONE WITH APP FIXTURE")


@pytest.fixture(scope="module")
def add_weather_sensors(db) -> Dict[str, Sensor]:  # noqa: F811
    return create_weather_sensors(db)


@pytest.fixture(scope="function")
def add_weather_sensors_fresh_db(fresh_db) -> Dict[str, Sensor]:  # noqa: F811
    return create_weather_sensors(fresh_db)


def create_weather_sensors(db: SQLAlchemy):  # noqa: F811
    """Add a weather station asset with two weather sensors."""
    weather_station_type = GenericAssetType(name=WEATHER_STATION_TYPE_NAME)
    db.session.add(weather_station_type)

    weather_station = GenericAsset(
        name="Test weather station",
        generic_asset_type=weather_station_type,
        latitude=33.4843866,
        longitude=126,
    )
    db.session.add(weather_station)

    wind_sensor = Sensor(
        name="wind speed",
        generic_asset=weather_station,
        event_resolution=timedelta(minutes=60),
        unit="m/s",
    )
    db.session.add(wind_sensor)

    temp_sensor = Sensor(
        name="temperature",
        generic_asset=weather_station,
        event_resolution=timedelta(minutes=60),
        unit="°C",
    )
    db.session.add(temp_sensor)
    return {"wind": wind_sensor, "temperature": temp_sensor}
