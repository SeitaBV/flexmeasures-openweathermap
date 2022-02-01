__version__ = "Unknown version"


"""
The __init__ for the flexmeasures-openweathermap FlexMeasures plugin.

FlexMeasures registers the BluePrint objects it finds in here.
"""


from importlib_metadata import version, PackageNotFoundError

from flask import Blueprint

from .utils import ensure_bp_routes_are_loaded_fresh

# Overwriting version (if possible) from the package metadata
# ― if this plugin has been installed as a package.
# This uses importlib.metadata behaviour added in Python 3.8.
# Note that we rely on git tags (via setuptools_scm) to define that version.
try:
    __version__ = version("flexmeasures_openweathermap")
except PackageNotFoundError:
    # package is not installed
    pass

# CLI
flexmeasures_openweathermap_cli_bp: Blueprint = Blueprint(
    "flexmeasures-openweathermap CLI",
    __name__,
    cli_group="flexmeasures-openweathermap"
)
flexmeasures_openweathermap_cli_bp.cli.help = "flexmeasures-openweathermap CLI commands"
ensure_bp_routes_are_loaded_fresh("cli.commands")
from flexmeasures_openweathermap.cli import commands  # noqa: E402,F401

