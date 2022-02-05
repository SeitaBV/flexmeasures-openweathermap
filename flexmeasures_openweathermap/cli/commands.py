from datetime import timedelta

from flask.cli import with_appcontext
import click
from flexmeasures.data.models.time_series import Sensor

# from flexmeasures.data.transactional import task_with_status_report
from flexmeasures.data.config import db

from .. import flexmeasures_openweathermap_bp
from .schemas.weather_sensor import WeatherSensorSchema
from ..utils.modeling import get_weather_station

# from ..utils.filing import make_file_path
# from ..utils.owm import save_forecasts_in_db, save_forecasts_as_json


@flexmeasures_openweathermap_bp.cli.command("register-weather-sensor")
@with_appcontext
@click.option("--name", required=True)
@click.option("--unit", required=True, help="e.g. °C, m/s, kW/m²")
@click.option(
    "--latitude",
    required=True,
    type=float,
    help="Latitude of the sensor's location",
)
@click.option(
    "--longitude",
    required=True,
    type=float,
    help="Longitude of the sensor's location",
)
@click.option(
    "--timezone",
    default="UTC",
    help="timezone as string, e.g. 'UTC' (default) or 'Europe/Amsterdam'",
)
def add_weather_sensor(**args):
    """
    Add a weather sensor.
    This will first create a weather station asset if none exists at the location yet.

    TODO: allow to add seasonality (daily, yearly) and save as Sensor attributes.
    TODO: allow to also pass an asset ID for the weather station (instead of location)?
    """
    errors = WeatherSensorSchema().validate(args)
    if errors:
        print(
            f"Please correct the following errors:\n{errors}.\n Use the --help flag to learn more."
        )
        raise click.Abort

    weather_station = get_weather_station(args["latitude"], args["longitude"])
    args["generic_asset"] = weather_station
    del args["latitude"]
    del args["longitude"]

    args["event_resolution"] = timedelta(minutes=60)
    sensor = Sensor(**args)  # TODO: without seasonality

    # TODO: check name is unique in weather station
    # TODO: add seasonality attributes
    db.session.add(sensor)
    db.session.commit()
    print(f"Successfully created weather sensor with ID {sensor.id}")
    print(f" You can access it at its entity address {sensor.entity_address}")


'''
@flexmeasures_openweathermap_bp.cli.command("get-weather-forecasts")
@with_appcontext
@task_with_status_report("get-openweathermap-forecasts")
@click.option(
    "--location",
    type=str,
    required=True,
    help='Measurement location(s). "latitude,longitude" or "top-left-latitude,top-left-longitude:'
    'bottom-right-latitude,bottom-right-longitude." The first format defines one location to measure.'
    " The second format defines a region of interest with several (>=4) locations"
    ' (see also the "method" and "num_cells" parameters for this feature).',
)
@click.option(
    "--store-in-db/--store-as-json-files",
    default=True,
    help="Store forecasts in the database, or simply save as json files (defaults to database).",
)
@click.option(
    "--num_cells",
    type=int,
    default=1,
    help="Number of cells on the grid. Only used if a region of interest has been mapped in the location parameter. Defaults to 1.",
)
@click.option(
    "--method",
    default="hex",
    type=click.Choice(["hex", "square"]),
    help="Grid creation method. Only used if a region of interest has been mapped in the location parameter.",
)
@click.option(
    "--region",
    type=str,
    default="",
    help="Name of the region (will create sub-folder if you store json files, should later probably tag the forecast in the DB).",
)
def collect_weather_data(location, store_in_db, num_cells, method, region):
    """
    Collect weather forecasts from the OpenWeatherMap API

    This function can get weather data for one location or for several locations within
    a geometrical grid (See the --location parameter).
    """

    api_key = str(app.config.get("OPENWEATHERMAP_API_KEY"))
    if api_key is None:
        raise Exception("Setting OPENWEATHERMAP_API_KEY not available.")
    locations = get_locations(location, num_cells, method)

    # Save the results
    if store_in_db:
        save_forecasts_in_db(api_key, locations, data_source=get_data_source())
    else:
        save_forecasts_as_json(
            api_key, locations, data_path=make_file_path(app, region)
        )


'''
