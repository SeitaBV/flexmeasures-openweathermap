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
