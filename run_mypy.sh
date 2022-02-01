#!/bin/bash
set -e
pip install mypy
# We are checking python files which have type hints
files=$(find . -name \*.py -not -path "./venv/*")
mypy --follow-imports skip --ignore-missing-imports $files 
