from packaging import version

from flask import current_app
from flexmeasures.data.models.generic_assets import GenericAsset, GenericAssetType
from flexmeasures import Source, __version__ as flexmeasures_version
from flexmeasures.data import db
from flexmeasures.data.services.data_sources import get_or_create_source

from flexmeasures_weather import DEFAULT_DATA_SOURCE_NAME
from flexmeasures_weather import WEATHER_STATION_TYPE_NAME
from flexmeasures_weather import DEFAULT_WEATHER_STATION_NAME


if version.parse(flexmeasures_version) < version.parse("0.13"):
    SOURCE_TYPE = "forecasting script"
else:
    SOURCE_TYPE = "forecaster"


def get_or_create_owm_data_source() -> Source:
    """Make sure we have an data source"""
    return get_or_create_source(
        source=current_app.config.get(
            "WEATHER_DATA_SOURCE_NAME", DEFAULT_DATA_SOURCE_NAME
        ),
        source_type=SOURCE_TYPE,
        flush=False,
    )


def get_or_create_owm_data_source_for_derived_data() -> Source:
    owm_source_name = current_app.config.get(
        "WEATHER_DATA_SOURCE_NAME", DEFAULT_DATA_SOURCE_NAME
    )
    return get_or_create_source(
        source=f"FlexMeasures {owm_source_name}",
        source_type=SOURCE_TYPE,
        flush=False,
    )


def get_or_create_weather_station_type() -> GenericAssetType:
    """Make sure a weather station type exists"""
    weather_station_type = GenericAssetType.query.filter(
        GenericAssetType.name == WEATHER_STATION_TYPE_NAME,
    ).one_or_none()
    if weather_station_type is None:
        weather_station_type = GenericAssetType(
            name=WEATHER_STATION_TYPE_NAME,
            description="A weather station with various sensors.",
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


def get_weather_station_by_asset_id(asset_id: int) -> GenericAsset:
    weather_station = GenericAsset.query.filter(
        GenericAsset.generic_asset_type_id == asset_id
    ).one_or_none()
    if weather_station is None:
        raise Exception(
            f"[FLEXMEASURES-WEATHER] Weather station is not present for the given asset id '{asset_id}'."
        )

    if weather_station.latitude is None or weather_station.longitude is None:
        raise Exception(
            f"[FLEXMEASURES-WEATHER] Weather station {weather_station} is missing location information [Latitude, Longitude]."
        )

    return weather_station
