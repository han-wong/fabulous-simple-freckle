import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

from pokemon import (
    database,
    errors,
    # git,
    play,
    pages,
    # posts,
)


def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    app.logger.setLevel("INFO")

    database.init_app(app)

    # app.register_blueprint(git.bp)
    app.register_blueprint(pages.bp)
    app.register_blueprint(play.bp)
    # app.register_blueprint(posts.bp)
    app.register_error_handler(404, errors.page_not_found)
    app.config.update(POKEMON=os.environ.get("POKEMON"))
    app.logger.debug(f"Current Environment: {os.getenv('ENVIRONMENT')}")
    app.logger.debug(f"Using Database: {app.config.get('DATABASE')}")
    return app


if __name__ == "__main__":
    create_app()
