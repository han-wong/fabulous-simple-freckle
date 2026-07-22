from flask import abort

from flask_restful import Resource, fields, marshal_with, reqparse

from pokemon import game_logic, game_repository
from pokemon.auth import get_current_user

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
        raise ValueError("String must be at least %i characters long" % min_length)
    return validate


class Game(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('game_id', location="args", type=str)
        super(Game, self).__init__()

    @marshal_with(game_fields)
    def get(self):
        game_id = self.reqparse.parse_args()["game_id"]
        game = game_logic.load_game(game_id)
        if not game:
            raise abort(404, 'Game not found!')

        current_user = get_current_user()
        user_id = current_user["id"] if current_user else None
        if not game_logic.is_game_owner(game, user_id):
            raise abort(403, 'You do not have access to this game.')

        return game, 200

    @marshal_with(game_fields)
    def post(self):
        current_user = get_current_user()
        user_id = current_user["id"] if current_user else None
        game_id = game_logic.start_new_game(user_id=user_id)
        game = game_logic.load_game(game_id)
        return game, 201

    @marshal_with(game_fields)
    def put(self):
        game_id = self.reqparse.parse_args()["game_id"]
        game = game_logic.load_game(game_id)
        if not game:
            raise abort(404, 'Game not found!')

        current_user = get_current_user()
        user_id = current_user["id"] if current_user else None
        if not game_logic.is_game_owner(game, user_id):
            raise abort(403, 'You do not have access to this game.')

        if not game["lives"]:
            if game["player"]:
                raise abort(400, 'Game is over!')
            else:
                self.reqparse.add_argument('name', location='json', type=min_length(3))
                game["player"] = self.reqparse.parse_args()["name"]
                game_repository.save_game(game)
                return game, 201

        self.reqparse.add_argument('guessed_letters', location='json', type=str)
        guesses = self.reqparse.parse_args()["guessed_letters"].upper()
        if not guesses:
            raise abort(400, 'Invalid guess. Enter at least one letter!')

        new_letters = "".join(
            dict.fromkeys(c for c in guesses if c not in game["guessed_letters"])
        )
        if not new_letters:
            raise abort(400, 'You already tried that guess!')

        game = game_logic.handle_guess(game, new_letters)
        return game, 201
