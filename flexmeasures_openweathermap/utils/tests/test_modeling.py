from flexmeasures.data.models.generic_assets import GenericAsset

from flexmeasures_openweathermap import DEFAULT_WEATHER_STATION_NAME
from flexmeasures_openweathermap.utils.modeling import get_or_create_weather_station


def test_creating_two_weather_stations(fresh_db):
    get_or_create_weather_station(50, 40)
    get_or_create_weather_station(40, 50)
    assert (
        GenericAsset.query.filter(
            GenericAsset.name == DEFAULT_WEATHER_STATION_NAME
        ).count()
        == 2
    )
