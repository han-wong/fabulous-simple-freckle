from flask import Blueprint, render_template, session

from pokemon import game_logic

bp = Blueprint("pages", __name__)


@bp.route("/")
def home():
    active_game_id = session.get("game_id")
    active_game = None
    if active_game_id:
        game = game_logic.get_game(active_game_id)
        if game and game["lives"] > 0:
            active_game = game
    return render_template("pages/home.html", active_game=active_game)


@bp.route("/about")
def about():
    return render_template("pages/about.html")