from packaging import version

from flask import current_app
from flexmeasures import Asset, AssetType, Source, __version__ as flexmeasures_version
from flexmeasures.data import db
from flexmeasures.data.services.data_sources import get_or_create_source

from flexmeasures_openweathermap import DEFAULT_DATA_SOURCE_NAME
from flexmeasures_openweathermap import WEATHER_STATION_TYPE_NAME
from flexmeasures_openweathermap import DEFAULT_WEATHER_STATION_NAME


if version.parse(flexmeasures_version) < version.parse("0.13"):
    SOURCE_TYPE = "forecasting script"
else:
    SOURCE_TYPE = "forecaster"


def get_or_create_owm_data_source() -> Source:
    """Make sure we have an OWM data source"""
    return get_or_create_source(
        source=current_app.config.get(
            "OPENWEATHERMAP_DATA_SOURCE_NAME", DEFAULT_DATA_SOURCE_NAME
        ),
        source_type=SOURCE_TYPE,
        flush=False,
    )


def get_or_create_owm_data_source_for_derived_data() -> Source:
    owm_source_name = current_app.config.get(
        "OPENWEATHERMAP_DATA_SOURCE_NAME", DEFAULT_DATA_SOURCE_NAME
    )
    return get_or_create_source(
        source=f"FlexMeasures {owm_source_name}",
        source_type=SOURCE_TYPE,
        flush=False,
    )


def get_or_create_weather_station_type() -> AssetType:
    """Make sure a weather station type exists"""
    weather_station_type = AssetType.query.filter(
        AssetType.name == WEATHER_STATION_TYPE_NAME,
    ).one_or_none()
    if weather_station_type is None:
        weather_station_type = AssetType(
            name=WEATHER_STATION_TYPE_NAME,
            description="A weather station with various sensors.",
        )
        db.session.add(weather_station_type)
    return weather_station_type


def get_or_create_weather_station(latitude: float, longitude: float) -> Asset:
    """Make sure a weather station exists at this location."""
    station_name = current_app.config.get(
        "WEATHER_STATION_NAME", DEFAULT_WEATHER_STATION_NAME
    )
    weather_station = Asset.query.filter(
        Asset.latitude == latitude, Asset.longitude == longitude
    ).one_or_none()
    if weather_station is None:
        weather_station_type = get_or_create_weather_station_type()
        weather_station = Asset(
            name=station_name,
            generic_asset_type=weather_station_type,
            latitude=latitude,
            longitude=longitude,
        )
        db.session.add(weather_station)
    return weather_station
