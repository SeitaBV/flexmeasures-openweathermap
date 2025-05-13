#!/bin/bash
set -e
pip install --upgrade mypy > 1.4
pip install types-pytz types-requests types-Flask types-click types-redis types-tzlocal types-python-dateutil types-setuptools
files=$(find flexmeasures_weather -name \*.py)
mypy --follow-imports skip --ignore-missing-imports $files 
