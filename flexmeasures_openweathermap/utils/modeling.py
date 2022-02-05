from flask import current_app
from flexmeasures.data.config import db
from flexmeasures.data.models.generic_assets import GenericAssetType, GenericAsset
from flexmeasures.data.models.data_sources import DataSource

from flexmeasures_openweathermap import DEFAULT_DATA_SOURCE_NAME
from flexmeasures_openweathermap import WEATHER_STATION_TYPE_NAME
from flexmeasures_openweathermap import DEFAULT_WEATHER_STATION_NAME


def get_data_source() -> DataSource:
    """Make sure we have a data source"""
    source_name = current_app.config.get("DATA_SOURCE_NAME", DEFAULT_DATA_SOURCE_NAME)
    data_source = DataSource.query.filter_by(
        name=source_name, type="forecasting script"
    ).one_or_none()
    if data_source is None:
        data_source = DataSource(name=source_name, type="forecasting script")
        db.session.add(data_source)
    return data_source


def get_weather_station_type() -> GenericAssetType:
    """Make sure a weather station type exists"""
    weather_station_type = GenericAssetType.query.filter(
        GenericAssetType.name == WEATHER_STATION_TYPE_NAME,
    ).one_or_none()
    if weather_station_type is None:
        weather_station_type = GenericAssetType(
            name=WEATHER_STATION_TYPE_NAME,
            description="Weather Stations with various sensors",
        )
        db.session.add(weather_station_type)
    return weather_station_type


def get_weather_station(latitude: float, longitude: float) -> GenericAsset:
    """Make sure a weather station exists at this location."""
    station_name = current_app.config.get(
        "WEATHER_STATION_NAME", DEFAULT_WEATHER_STATION_NAME
    )
    weather_station = GenericAsset.query.filter(
        GenericAsset.latitude == latitude, GenericAsset.longitude == longitude
    ).one_or_none()
    if weather_station is None:
        weather_station_type = get_weather_station_type()
        weather_station = GenericAsset(
            name=station_name,
            generic_asset_type=weather_station_type,
            latitude=latitude,
            longitude=longitude,
        )
        db.session.add(weather_station)
    return weather_station
