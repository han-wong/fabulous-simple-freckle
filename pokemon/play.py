from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from pokemon import game_logic, game_repository, user_repository, pokemon_repository
from pokemon.auth import get_current_user

bp = Blueprint("play", __name__)


@bp.route("/hi_scores", methods=["GET"])
def hi_scores():
    games = game_repository.get_games_by_score()
    for x in games:
        current_app.logger.debug(f"games = {dict(x)}")
    return render_template("pages/hi-scores.html", games=games)


@bp.route("/new_game")
def new_game():
    current_user = get_current_user()
    user_id = current_user["id"] if current_user else None
    return redirect(url_for("play.play", game_id=game_logic.start_new_game(user_id=user_id)))


@bp.route("/cash_out", methods=["POST"])
def cash_out():
    game_id = request.args.get("game_id")
    game = game_logic.load_game(game_id)

    if not game:
        return redirect(url_for("play.new_game"))

    current_user = get_current_user()
    user_id = current_user["id"] if current_user else None
    if not game_logic.is_game_owner(game, user_id):
        return redirect(url_for("play.new_game"))

    # Only allow cash out on active games with something to show for it
    if not game["lives"] or not game["score"]:
        return redirect(url_for("play.play", game_id=game_id))

    # Quitting counts as a fail for the current unsolved Pokémon
    pokemon_repository.record_failed(game["pokedex_number"])

    if current_user:
        profile = user_repository.get_user(current_user["id"])
        if profile:
            game["user_id"] = current_user["id"]
            game["player"] = profile["display_name"]
            game["lives"] = 0
            game_repository.save_game(game)
            session.pop("game_id", None)
            return redirect(url_for("play.hi_scores"))
        # Logged in but no display name — fall through to game over screen
        # so they can set a name via the profile prompt

    # Guest or logged-in without a display name: drain lives to trigger game-over
    game["lives"] = 0
    game_repository.save_game(game)
    return redirect(url_for("play.play", game_id=game_id))


@bp.route("/play", methods=["GET", "POST"])
def play():
    game_id = request.args.get("game_id")
    game = game_logic.load_game(game_id)

    if not game:
        return new_game()

    current_user = get_current_user()
    user_id = current_user["id"] if current_user else None
    if not game_logic.is_game_owner(game, user_id):
        return redirect(url_for("play.new_game"))

    session["game_id"] = game_id

    # Game over — try to finalise the score.
    if not game["lives"] and not game["player"]:
        current_user = get_current_user()
        if current_user:
            profile = user_repository.get_user(current_user["id"])
            if profile:
                # Logged-in user with a display name: persist user_id so the
                # leaderboard JOIN always shows their current name, then redirect.
                game["user_id"] = current_user["id"]
                game["player"] = profile["display_name"]
                game_repository.save_game(game)
                session.pop("game_id", None)
                return redirect(url_for("play.hi_scores"))
            # Logged in but no display name set yet — fall through to show the
            # profile prompt in the template.

    if request.method == "POST" and request.form:
        current_app.logger.debug(f"request.form = {request.form}")
        player = request.form.get("player-name") or ""

        if not game["player"] and 3 <= len(player) <= 20:
            game["player"] = player
            game_repository.save_game(game)
            session.pop("game_id", None)
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
