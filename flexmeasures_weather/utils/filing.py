import os

import click
from flask import Flask, current_app

from flexmeasures_weather import DEFAULT_FILE_PATH_LOCATION


def make_file_path(app: Flask, region: str) -> str:
    """Ensure and return path for weather data"""
    file_path = current_app.config.get(
        "WEATHER_FILE_PATH_LOCATION", DEFAULT_FILE_PATH_LOCATION
    )
    data_path = os.path.join(app.root_path, file_path)
    if not os.path.exists(data_path):
        click.echo("[FLEXMEASURES-WEATHER] Creating %s ..." % data_path)
        os.mkdir(data_path)
    # optional: extend with subpath for region
    if region is not None and region != "":
        region_data_path = "%s/%s" % (data_path, region)
        if not os.path.exists(region_data_path):
            click.echo("[FLEXMEASURES-WEATHER] Creating %s ..." % region_data_path)
            os.mkdir(region_data_path)
        data_path = region_data_path
    return data_path
