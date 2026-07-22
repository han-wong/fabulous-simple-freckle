import pytest
from flask import Flask


@pytest.fixture
def app_context():
    """A bare Flask app context, just enough for current_app.logger to work
    inside game_logic. Deliberately does NOT use the real create_app(), since
    that connects to a real Postgres database on startup."""
    app = Flask(__name__)
    with app.app_context():
        yield app
