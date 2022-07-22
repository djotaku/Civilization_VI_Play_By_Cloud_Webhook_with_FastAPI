from fastapi import HTTPException, APIRouter, Query
from typing import Optional

from ..dependencies import load_most_recent_games
from ..models import information_models

router = APIRouter(tags=['Information Endpoints'])


def dict_to_game_model(dictionary: dict) -> information_models.Game:
    """Take in a dictionary of a game and turn it into a Game model.

    Example dict:

    {"Eric's Barbarian Clash Game": {'player_name': 'Eric', 'turn_number': 300,
    'time_stamp': {'year': 2022, 'month': 7, 'day': 21, 'hour': 20, 'minute': 33,
    'second': 28}}}

    """
    game_name = list(dictionary.keys())
    game_name = game_name[0]
    time_stamp = information_models.TimeStamp(year = dictionary[game_name]['time_stamp']['year'],
                                              month = dictionary[game_name]['time_stamp']['month'],
                                              day = dictionary[game_name]['time_stamp']['day'],
                                              hour = dictionary[game_name]['time_stamp']['hour'],
                                              minute = dictionary[game_name]['time_stamp']['minute'],
                                              second = dictionary[game_name]['time_stamp']['second'])
    game_info = information_models.GameInfo(player_name=dictionary[game_name]['player_name'],
                                            turn_number=dictionary[game_name]['turn_number'],
                                            time_stamp=time_stamp)
    game = information_models.Game(game_name=game_name, game_info=game_info)
    return game


@router.get('/current_games', response_model=information_models.CurrentGames)
def return_current_games(player_to_blame: Optional[str] = Query(None,
                                                                title="Player to Blame",
                                                                description="To see how many games outstanding.")):
    """Returns the dictionary containing the games awaiting a turn.

    If a player name is passed, it will return the games that player has outstanding.

    Otherwise, it will return a list of all the games outstanding.
    """
    current_games = load_most_recent_games()
    if player_to_blame:
        does_player_exist = any(
            player_to_blame in current_games[games].get('player_name')
            for games in current_games.keys())

        if does_player_exist:
            return {"games": [dict_to_game_model({game: game_attributes})
                              for (game, game_attributes) in current_games.items()
                    if current_games[game].get('player_name') == player_to_blame]}
        else:
            raise HTTPException(status_code=404, detail="Player not found")
    all_games = [dict_to_game_model({game: game_attributes}) for (game, game_attributes) in current_games.items()]
    return {"games": all_games}


@router.get('/total_number_of_games', response_model=information_models.GameCounts)
def return_total_number_of_games():
    """Returns the total number of games the API knows about."""
    current_games = load_most_recent_games()
    return {'total_games': len(current_games)}
