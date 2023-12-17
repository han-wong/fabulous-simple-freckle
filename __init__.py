from flask import Flask

from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    print(config_class)
    # Initialize Flask extensions here

    # Register blueprints here
    from flask_hangman.main import bp as main_bp

    app.register_blueprint(main_bp)

    return app


if __name__ == "__main__":
    create_app()
