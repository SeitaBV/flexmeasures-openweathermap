#!/bin/bash
set -e
pip install mypy
pip install types-pytz types-requests types-Flask types-click types-redis types-tzlocal types-python-dateutil types-setuptools
files=$(find . -name \*.py -not -path "./venv/*" -not -path ".eggs/*" -not -path "./build/*" -not -path "./dist/*" -not -path "./scripts/*")
mypy --follow-imports skip --ignore-missing-imports $files 
