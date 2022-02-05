# flexmeasures-openweathermap - a plugin for FlexMeasures to integrate OpenWeatherMap data

## Usage

To register a new weather sensor:

`flexmeasures owm register-weather-sensor --name wind-speed --latitude 30 --longitude 40 --unit m/s`

Notes about weather sensor setup: 

- Weather sensors are public. They are accessible by all accounts on a FlexMeasures server. TODO: maybe limit this to a list of account roles.
- The resolution is one hour. OWM also supports minutely data within the upcoming hour(s), but that is not supported here.

To collect weather forecasts:

TODO: add weather forecasts to the database

TODO: alternative usage: save raw results in JSON files (for later processing)

    
Note that 1000 free calls per day can be made to the OpenWeatherMap API,
so we can make a call every 15 minutes for up to 10 assets or every hour for up to 40 assets (or get a paid account).


## Installation

1. Add "/path/to/flexmeasures-openweathermap/flexmeasures_openweathermap" to your FlexMeasures (>v0.7.0dev8) config file,
   using the FLEXMEASURES_PLUGINS setting (a list).
   Alternatively, if you installed this plugin as a package (e.g. via `python setup.py install`, `pip install -e` or `pip install flexmeasures_openweathermap` after this project is on Pypi), then "flexmeasures_openweathermap" suffices.

2.  


## Development

We use pre-commit to keep code quality up.

Install necessary tools with:

    pip install pre-commit black flake8 mypy
    pre-commit install

or:

    make install-for-dev

Try it:

    pre-commit run --all-files --show-diff-on-failure
