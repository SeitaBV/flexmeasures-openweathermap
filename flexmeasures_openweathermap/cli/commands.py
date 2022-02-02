from datetime import timedelta

from flask.cli import with_appcontext
import click
from flexmeasures.data.models.time_series import Sensor

# from flexmeasures.data.transactional import task_with_status_report
from flexmeasures.data.config import db

from .. import flexmeasures_openweathermap_bp
from .schemas.weather_sensor import WeatherSensorSchema


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

    args["event_resolution"] = timedelta(minutes=60)
    # TODO: make sure we have a weather station
    sensor = Sensor(**args)  # TODO: without location and seasonality

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
    "--region",
    type=str,
    default="",
    help="Name of the region (will create sub-folder if you store json files, should later probably tag the forecast in the DB).",
)
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
    "--store-in-db/--store-as-json-files",
    default=False,
    help="Store forecasts in the database, or simply save as json files. (defaults to json files)",
)
def collect_weather_data(region, location, num_cells, method, store_in_db):
    """
    Collect weather forecasts from the OpenWeatherMap API

    This function can get weather data for one location or for several locations within
    a geometrical grid (See the --location parameter).

    This should move to a FlexMeasures plugin for OWM integration.
    """
    from flexmeasures.data.scripts.grid_weather import get_weather_forecasts

    get_weather_forecasts(app, region, location, num_cells, method, store_in_db)
'''
