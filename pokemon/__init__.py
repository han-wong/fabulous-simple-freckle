import os
from dotenv import load_dotenv
from flask import Flask
from flask_restful import Api
from pokemon import (
    database,
    errors,
    git,
    play,
    pages,
)
from pokemon import api as api_module
from pokemon.api import Game

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config.from_prefixed_env()
    app.logger.setLevel(
        "DEBUG" if app.config.get("ENVIRONMENT") == "Development" else "INFO"
    )
    database.init_app(app)

    app.register_blueprint(git.bp)
    app.register_blueprint(pages.bp)
    app.register_blueprint(play.bp)
    app.register_error_handler(404, errors.page_not_found)
    app.config.update(POKEMON=os.getenv("FLASK_POKEMON"))
    app.logger.debug(f"Current Environment: {app.config.get('ENVIRONMENT')}")
    app.logger.debug(f"Using Database: {app.config.get('DATABASE')}")

    rest_api = Api(app)
    rest_api.add_resource(Game, '/game', endpoint='game')
    return app


if __name__ == "__main__":
    create_app()
