from flask import current_app
from flexmeasures.data.config import db
from flexmeasures.data.models.generic_assets import GenericAssetType, GenericAsset
from flexmeasures.data.models.data_sources import DataSource, get_or_create_source

from flexmeasures_openweathermap import DEFAULT_DATA_SOURCE_NAME
from flexmeasures_openweathermap import WEATHER_STATION_TYPE_NAME
from flexmeasures_openweathermap import DEFAULT_WEATHER_STATION_NAME


def get_or_create_owm_data_source() -> DataSource:
    """Make sure we have am OWM data source"""
    return get_or_create_source(
        source=current_app.config.get(
            "OPENWEATHERMAP_DATA_SOURCE_NAME", DEFAULT_DATA_SOURCE_NAME
        ),
        source_type="forecasting script",
        flush=False,
    )


def get_or_create_owm_data_source_for_derived_data() -> DataSource:
    owm_source_name = current_app.config.get(
        "OPENWEATHERMAP_DATA_SOURCE_NAME", DEFAULT_DATA_SOURCE_NAME
    )
    return get_or_create_source(
        source=f"FlexMeasures {owm_source_name}",
        source_type="forecasting script",
    )


def get_or_create_weather_station_type() -> GenericAssetType:
    """Make sure a weather station type exists"""
    weather_station_type = GenericAssetType.query.filter(
        GenericAssetType.name == WEATHER_STATION_TYPE_NAME,
    ).one_or_none()
    if weather_station_type is None:
        weather_station_type = GenericAssetType(
            name=WEATHER_STATION_TYPE_NAME,
            description="A weather station with various sensors",
        )
        db.session.add(weather_station_type)
    return weather_station_type


def get_or_create_weather_station(latitude: float, longitude: float) -> GenericAsset:
    """Make sure a weather station exists at this location."""
    station_name = current_app.config.get(
        "WEATHER_STATION_NAME", DEFAULT_WEATHER_STATION_NAME
    )
    weather_station = GenericAsset.query.filter(
        GenericAsset.latitude == latitude, GenericAsset.longitude == longitude
    ).one_or_none()
    if weather_station is None:
        weather_station_type = get_or_create_weather_station_type()
        weather_station = GenericAsset(
            name=station_name,
            generic_asset_type=weather_station_type,
            latitude=latitude,
            longitude=longitude,
        )
        db.session.add(weather_station)
    return weather_station
