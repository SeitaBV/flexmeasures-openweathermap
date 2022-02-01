from flask import current_app
from flask.cli import with_appcontext
import click
from flexmeasures.data.transactional import task_with_status_report

from .. import flexmeasures_openweathermap_cli_bp


@flexmeasures_openweathermap_cli_bp.cli.command("hello-world")
@click.option(
    "--name",
)
@with_appcontext
@task_with_status_report
def hello_world(name: str):
    print(f"Hello, {name}!")
    current_app.logger.info(f"'Hello, {name}!' printed")



@fm_add_data.command("weather-sensor")
@with_appcontext
@click.option("--name", required=True)
@click.option("--unit", required=True, help="e.g. °C, m/s, kW/m²")
@click.option(
    "--event-resolution",
    required=True,
    type=int,
    help="Expected resolution of the data in minutes",
)
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
    This is legacy, after we moved to the new data model.
    Adding necessary GenericAsset and Sensor(s) should be done by the (to be built) OWM plugin.
    """
    check_timezone(args["timezone"])
    check_errors(WeatherSensorSchema().validate(args))
    args["event_resolution"] = timedelta(minutes=args["event_resolution"])
    sensor = WeatherSensor(**args)
    db.session.add(sensor)
    db.session.commit()
    print(f"Successfully created weather sensor with ID {sensor.id}")
    print(f" You can access it at its entity address {sensor.entity_address}")




@fm_add_data.command("external-weather-forecasts")
@with_appcontext
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

