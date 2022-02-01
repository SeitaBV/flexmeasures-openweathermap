from ..commands import hello_world

"""
Useful resource: https://flask.palletsprojects.com/en/2.0.x/testing/#testing-cli-commands
"""


def test_hello_world(app):
    runner = app.test_cli_runner()
    result = runner.invoke(hello_world, ["--name", "George"])
    assert "Hello, George!" in result.output
