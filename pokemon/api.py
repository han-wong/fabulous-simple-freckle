from flask import abort, current_app, request

from flask_restful import Resource, fields, marshal_with, reqparse

from pokemon.game import create_game, get_current_word, get_game, handle_guess, load_next_pokemon, save_game

game_fields = dict(
    current_word=fields.String,
    game_id=fields.String,
    guess=fields.String,
    life=fields.Integer,
    player=fields.String,
    score=fields.Integer,
    streak=fields.Integer,
)


def min_length(min_length):
    def validate(s):
        if len(s) >= min_length:
            return s
        raise ValueError(
            "String must be at least %i characters long" % min_length)
    return validate


class Game(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('game_id', location="args", type=str)
        self.reqparse.add_argument('guess', location='json', type=str)
        self.reqparse.add_argument('name', location='json', type=min_length(3))
        super(Game, self).__init__()

    @marshal_with(game_fields)
    def get(self):
        game_id = self.get_required_args("game_id")
        game = get_game(game_id)

        if game:
            game["current_word"] = get_current_word(game)
            if "_" in game["current_word"]:
                return game, 200
            else:
                return load_next_pokemon(game), 200

        raise abort(404, 'Game not found!')

    @marshal_with(game_fields)
    def post(self):
        args = request.args
        current_app.logger.debug(f"post, args = {args}")

        game_id = create_game()
        game = get_game(game_id)
        return game, 201

    @marshal_with(game_fields)
    def put(self):
        game_id = self.get_required_args("game_id")
        game = get_game(game_id)

        if not game:
            raise abort(404, 'Game not found!')
        if not game["life"]:
            if game["player"] and len(game["player"]) >= 3:
                raise abort(400, 'Game is over!')
            else:
                game["player"] = self.get_required_args("name")
                save_game(game)
            raise abort(400, 'Game is over!')

        guess = self.get_required_args("guess").upper()
        if len(guess) != 1:
            raise abort(400, 'Invalid guess. Enter a single letter!')
        if guess in game["guess"]:
            raise abort(400, 'You already tried that guess!')

        game = handle_guess(game, guess)
        return game, 201

    def get_required_args(self, field):
        self.reqparse.replace_argument(field, required=True)
        return self.reqparse.parse_args()[field]
