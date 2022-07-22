from typing import Optional
from fastapi import FastAPI, HTTPException, Query, status
import json

from . import api_logger
from .dependencies import load_most_recent_games

app = FastAPI(
    title="Eric's Civilization VI Play By Cloud and PYDT Webhook server",
    description="The server acts as an endpoint for PBC and PYDT JSON then sends it to the service you configure.",
    version="0.2.5"
)


# ##########
# Configs
# ##########

current_games = load_most_recent_games()

# #############
# end Configs #
# #############


@app.get('/current_games')
def return_current_games(player_to_blame: Optional[str] = Query(None,
                                                                title="Player to Blame",
                                                                description="To see how many games outstanding.")):
    """Returns the dictionary containing the games awaiting a turn.

    If a player name is passed, it will return the games that player has outstanding.

    Otherwise, it will return a list of all the games outstanding.
    """
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


@app.get('/total_number_of_games')
def return_total_number_of_games():
    """Returns the total number of games the API knows about."""
    return len(current_games)


@app.delete('/delete_game', status_code=status.HTTP_200_OK)
def delete_game(game_to_delete: str = Query(None,
                                            title="Game to Delete",
                                            description="The name of the game to delete")):
    """Delete the game passed to this endpoint."""
    if game_to_delete not in current_games.keys():
        raise HTTPException(status_code=404, detail="Item not found")
    deleted_game = current_games.pop(game_to_delete)
    with open('most_recent_games.json', 'w') as most_recent_games_file:
        json.dump(current_games, most_recent_games_file)
    api_logger.debug(f"Deleted {deleted_game}")
    return {"deleted_game": deleted_game}
