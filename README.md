# flexmeasures-openweathermap - a plugin for FlexMeasures to integrate OpenWeatherMap data

## Usage

To register a new weather sensor:

`flexmeasures owm register-weather-sensor --name wind-speed --latitude 30 --longitude 40`

Currently supported: wind_speed, temperature & radiation.

Notes about weather sensor setup: 

- Weather sensors are public. They are accessible by all accounts on a FlexMeasures server. TODO: maybe limit this to a list of account roles.
- The resolution is one hour. OWM also supports minutely data within the upcoming hour(s), but that is not supported here.

To collect weather forecasts:

`flexmeasures owm get-weather-forecasts --location 30,40`

This saves forecasts for your registered sensors in the database.

Use the `--help`` option for more options, e.g. for specifying two locations and ask for a few weather stations to cover the region between them.

An alternative usage is to save raw results in JSON files (for later processing), like this:

`flexmeasures owm get-weather-forecasts --location 30,40 --store-as-json-files --region somewhere`

This saves the complete response from OpenWeatherMap in a local folder (i.e. no sensor registration needed, this is a direct way to use OWM, without FlexMeasures integration). `region` will become a subfolder.
 
Finally, note that currently 1000 free calls per day can be made to the OpenWeatherMap API,
so you can make a call every 15 minutes for up to 10 assets or every hour for up to 40 assets (or get a paid account).


## Installation

Add "/path/to/flexmeasures-openweathermap/flexmeasures_openweathermap" to your FlexMeasures (>v0.7.0dev8) config file,
using the FLEXMEASURES_PLUGINS setting (a list).

Alternatively, if you installed this plugin as a package (e.g. via `python setup.py install`, `pip install -e` or `pip install flexmeasures_openweathermap` after this project is on Pypi), then "flexmeasures_openweathermap" suffices.


## Development

We use pre-commit to keep code quality up.

Install necessary tools with:

    pip install pre-commit black flake8 mypy
    pre-commit install

or:

    make install-for-dev

Try it:

    pre-commit run --all-files --show-diff-on-failure
