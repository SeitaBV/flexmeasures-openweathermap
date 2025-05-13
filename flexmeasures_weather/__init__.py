__version__ = "Unknown version"


"""
The __init__ for the flexmeasures-weather FlexMeasures plugin.

FlexMeasures registers the BluePrint objects it finds in here.
"""


from importlib_metadata import version, PackageNotFoundError

from flask import Blueprint

from .utils.blueprinting import ensure_bp_routes_are_loaded_fresh

# Overwriting version (if possible) from the package metadata
# ― if this plugin has been installed as a package.
# This uses importlib.metadata behaviour added in Python 3.8.
# Note that we rely on git tags (via setuptools_scm) to define that version.
try:
    __version__ = version("flexmeasures_weather")
except PackageNotFoundError:
    # package is not installed
    pass


DEFAULT_FILE_PATH_LOCATION = "weather-forecasts"
DEFAULT_DATA_SOURCE_NAME = "Weather"
DEFAULT_WEATHER_STATION_NAME = "weather station (created by FM-Weather)"
WEATHER_STATION_TYPE_NAME = "weather station"
DEFAULT_MAXIMAL_DEGREE_LOCATION_DISTANCE = 1

__version__ = "0.1"
__settings__ = {
    "WEATHER_FILE_PATH_LOCATION": dict(
        description="Location of JSON files (if you store weather data in this form). Absolute path.",
        level="debug",
    ),
    "WEATHER_DATA_SOURCE_NAME": dict(
        description=f"Name of the data source for Weather data, defaults to '{DEFAULT_DATA_SOURCE_NAME}'",
        level="debug",
    ),
    "WEATHER_STATION_NAME": dict(
        description=f"Name of the weather station asset, defaults to '{DEFAULT_WEATHER_STATION_NAME}'",
        level="debug",
    ),
    "WEATHER_MAXIMAL_DEGREE_LOCATION_DISTANCE": dict(
        descripion=f"Maximum distance (in degrees latitude & longitude) for weather stations from forecast location, defaults to {DEFAULT_MAXIMAL_DEGREE_LOCATION_DISTANCE}",
        level="debug",
    ),
    "WEATHER_PROVIDER": dict(
        description="Provider for weather data. Permissible options are 'OWM' (OpenWeatherMap) or 'WAPI' (WeatherAPI).",
        level="error",
    ),
    "WEATHERAPI_KEY": dict(
        description="API key for OWM or WAPI, whatever you have chosen.",
        level="error",
    ),
}

# CLI
flexmeasures_weather_bp: Blueprint = Blueprint(
    "flexmeasures-weather CLI", __name__, cli_group="weather"
)
flexmeasures_weather_bp.cli.help = "flexmeasures-weather CLI commands"
ensure_bp_routes_are_loaded_fresh("cli.commands")
from flexmeasures_weather.cli import commands  # noqa: E402,F401
