from flexmeasures import Asset

from flexmeasures_weather import DEFAULT_WEATHER_STATION_NAME
from flexmeasures_weather.utils.modeling import get_or_create_weather_station


def test_creating_two_weather_stations(fresh_db):
    get_or_create_weather_station(50, 40)
    get_or_create_weather_station(40, 50)
    assert Asset.query.filter(Asset.name == DEFAULT_WEATHER_STATION_NAME).count() == 2
