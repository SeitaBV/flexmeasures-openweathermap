# Note: use tabs
# actions which are virtual, i.e. not a script
.PHONY: install install-for-dev install-deps install-flexmeasures-weather test freeze-deps upgrade-deps


# ---- Development ---

test:
	make install-for-dev
	pytest

# ---- Installation ---

install: install-deps install-flexmeasures-weather

install-for-dev:
	make freeze-deps
	pip-sync requirements/app.txt requirements/dev.txt requirements/test.txt
	make install-flexmeasures-weather
	pre-commit install

install-deps:
	make install-pip-tools
	make freeze-deps
	pip-sync requirements/app.txt

install-flexmeasures-weather:
	python setup.py develop

install-pip-tools:
	pip3 install -q "pip-tools>=6.2"

freeze-deps:
	make install-pip-tools
	pip-compile -o requirements/app.txt requirements/app.in
	pip-compile -o requirements/test.txt requirements/test.in
	pip-compile -o requirements/dev.txt requirements/dev.in

upgrade-deps:
	make install-pip-tools
	pip-compile --upgrade -o requirements/app.txt requirements/app.in
	pip-compile --upgrade -o requirements/test.txt requirements/test.in
	pip-compile --upgrade -o requirements/dev.txt requirements/dev.in
	make test

