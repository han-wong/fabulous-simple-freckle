from flask import abort, current_app, request

from flask_restful import Resource, fields, marshal_with, reqparse

from pokemon import game_logic, repository

game_fields = dict(
    masked_name=fields.String,
    game_id=fields.String,
    guessed_letters=fields.String,
    lives=fields.Integer,
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

        super(Game, self).__init__()

    @marshal_with(game_fields)
    def get(self):
        game_id = self.reqparse.parse_args()["game_id"]
        game = game_logic.get_game(game_id)

        if game:
            if "_" in game["masked_name"]:
                return game, 200
            else:
                return game_logic.load_next_pokemon(game), 200

        raise abort(404, 'Game not found!')

    @marshal_with(game_fields)
    def post(self):
        game_id = game_logic.start_new_game()
        game = game_logic.get_game(game_id)
        return game, 201

    @marshal_with(game_fields)
    def put(self):
        game_id = self.reqparse.parse_args()["game_id"]
        game = game_logic.get_game(game_id)

        if not game:
            raise abort(404, 'Game not found!')
        if not game["lives"]:
            if game["player"] and len(game["player"]) >= 3:
                raise abort(400, 'Game is over!')
            else:
                self.reqparse.add_argument(
                    'name', location='json', type=min_length(3))
                game["player"] = self.reqparse.parse_args()["name"]
                repository.save_game(game)
                return game, 201

        self.reqparse.add_argument(
            'guessed_letters', location='json', type=str)
        guesses = self.reqparse.parse_args()["guessed_letters"].upper()
        if not guesses:
            raise abort(400, 'Invalid guess. Enter at least one letter!')

        new_letters = "".join(
            dict.fromkeys(
                c for c in guesses if c not in game["guessed_letters"])
        )
        if not new_letters:
            raise abort(400, 'You already tried that guess!')

        game = game_logic.handle_guess(game, new_letters)
        return game, 201
