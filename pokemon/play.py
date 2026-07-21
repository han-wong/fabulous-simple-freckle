from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)

from pokemon import game_logic, repository

bp = Blueprint("play", __name__)


@bp.route("/hi_scores", methods=["GET"])
def hi_scores():
    games = repository.get_games_by_score()
    for x in games:
        current_app.logger.debug(f"games = {dict(x)}")
    return render_template("pages/hi-scores.html", games=games)


@bp.route("/new_game")
def new_game():
    return redirect(url_for("play.play", game_id=game_logic.start_new_game()))


@bp.route("/play", methods=["GET", "POST"])
def play():
    game_id = request.args.get("game_id")
    game = game_logic.get_game(game_id)
    if not game:
        return new_game()
 
    if request.method == "POST" and request.form:
        current_app.logger.debug(f"request.form = {request.form}")
        player = request.form.get("player-name") or ""
 
        if not game["player"] and 3 <= len(player) <= 10:
            game["player"] = player
            repository.save_game(game)
            return redirect(url_for("play.hi_scores"))
 
    (message, hi_score, image) = game_logic.get_game_state(game)
    return render_template(
        "pages/play.html",
        alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        masked_name=game["masked_name"],
        lives=game["lives"],
        guessed_letters=game["guessed_letters"],
        message=message,
        hi_score=hi_score,
        player=game["player"],
        pokemon=image,
        score=game["score"],
        streak=game["streak"],
    )