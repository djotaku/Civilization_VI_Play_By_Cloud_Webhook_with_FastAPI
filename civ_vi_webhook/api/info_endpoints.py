from fastapi import HTTPException, APIRouter, Query
from typing import Optional

from ..dependencies import load_most_recent_games

router = APIRouter(tags=['Information Endpoints'])


@router.get('/current_games')
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
            return {game: game_attributes for (game, game_attributes) in current_games.items()
                    if current_games[game].get('player_name') == player_to_blame}
        else:
            raise HTTPException(status_code=404, detail="Player not found")
    return current_games


@router.get('/total_number_of_games')
def return_total_number_of_games():
    """Returns the total number of games the API knows about."""
    current_games = load_most_recent_games()
    return len(current_games)
