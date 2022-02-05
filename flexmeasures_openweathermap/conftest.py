import pytest

from flexmeasures.app import create as create_flexmeasures_app

from flexmeasures.conftest import db, fresh_db  # noqa: F401


@pytest.fixture(scope="session")
def app():
    print("APP FIXTURE")

    # Adding this plugin, making sure the name is known (as last part of plugin path)
    test_app = create_flexmeasures_app(
        env="testing", plugins=["../flexmeasures_openweathermap"]
    )

    # Establish an application context before running the tests.
    ctx = test_app.app_context()
    ctx.push()

    yield test_app

    ctx.pop()

    print("DONE WITH APP FIXTURE")
