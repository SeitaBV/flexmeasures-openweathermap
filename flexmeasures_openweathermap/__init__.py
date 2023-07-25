__version__ = "Unknown version"


"""
The __init__ for the flexmeasures-openweathermap FlexMeasures plugin.

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
    __version__ = version("flexmeasures_openweathermap")
except PackageNotFoundError:
    # package is not installed
    pass


DEFAULT_FILE_PATH_LOCATION = "weather-forecasts"
DEFAULT_DATA_SOURCE_NAME = "OpenWeatherMap"
DEFAULT_WEATHER_STATION_NAME = "weather station (created by FM-OWM)"
WEATHER_STATION_TYPE_NAME = "weather station"
DEFAULT_MINIMAL_WEATHER_STATIONS = 2

__version__ = "0.1"
__settings__ = {
    "OPENWEATHERMAP_API_KEY": dict(
        description="You can generate this token after you made an account at OpenWeatherMap.",
        level="error",
    ),
    "OPENWEATHERMAP_FILE_PATH_LOCATION": dict(
        description="Location of JSON files (if you store weather data in this form). Absolute path.",
        level="debug",
    ),
    "OPENWEATHERMAP_DATA_SOURCE_NAME": dict(
        description=f"Name of the data source for OWM data, defaults to '{DEFAULT_DATA_SOURCE_NAME}'",
        level="debug",
    ),
    "WEATHER_STATION_NAME": dict(
        description=f"Name of the weather station asset, defaults to '{DEFAULT_WEATHER_STATION_NAME}'",
        level="debug",
    ),
    "MINIMAL_WEATHER_STATIONS": dict(
        descripion=f"Number of the closest weather stations to the location, defaults to '{DEFAULT_MINIMAL_WEATHER_STATIONS}'",
        level="debug",
    ),
}

# CLI
flexmeasures_openweathermap_bp: Blueprint = Blueprint(
    "flexmeasures-openweathermap CLI", __name__, cli_group="owm"
)
flexmeasures_openweathermap_bp.cli.help = "flexmeasures-openweathermap CLI commands"
ensure_bp_routes_are_loaded_fresh("cli.commands")
from flexmeasures_openweathermap.cli import commands  # noqa: E402,F401
