from typing import Optional

import fastapi.responses
from fastapi import APIRouter
from starlette.requests import Request

from ..dependencies import templates
from ..services.db import game_service, user_service

router = APIRouter(tags=['index'], include_in_schema=False)


async def get_potential_winners_list() -> list:
    """Get a list of potential selections for winners"""
    winners = await user_service.get_all_index_names()
    winners.extend(("Other Player", "Computer Player"))
    return winners


async def db_models_to_dictionary(games) -> list[dict]:
    """Convert a game from a DB Model to a dictionary for use by Jinja2"""
    games_to_return = []
    for game in games:
        time_stamp = game.game_info.time_stamp_v2.strftime('%m-%d-%Y %H:%M:%S')
        player_name = await user_service.get_index_name_by_user_id(game.game_info.next_player_id)
        this_game = {"game_name": game.game_name, "player_name": player_name,
                     "average_turn_time": game.game_info.average_turn_time,
                     "winner": game.game_info.winner,
                     "turn_number": game.game_info.turn_number,
                     "time_stamp": time_stamp}
        games_to_return.append(this_game)
    return games_to_return


async def get_games_for_index() -> (list, list):
    """Get the completed and current games into a list for the Jinja2 templates."""
    current_games_raw = await game_service.get_current_games()
    if current_games_raw:
        current_games = await db_models_to_dictionary(current_games_raw)
    else:
        current_games = []
    completed_games_raw = await game_service.get_completed_games()
    if completed_games_raw:
        completed_games = await db_models_to_dictionary(completed_games_raw)
    else:
        completed_games = []
    return completed_games, current_games


@router.get('/')
async def index(request: Request):
    """Render the index page."""
    completed_games, current_games = await get_games_for_index()
    potential_winners = await get_potential_winners_list()
    return templates.TemplateResponse('index.html', {'request': request,
                                                     "current_games": current_games,
                                                     "completed_games": completed_games,
                                                     "potential_winners": potential_winners})


@router.get('/favicon.ico')
def favicon():
    """Return a favicon.

    Mostly just here to prevent 404s from not having one.
    """
    return fastapi.responses.RedirectResponse(url="/static/favicon.ico")


@router.put('/both_tables')
async def get_both_games_tables(request: Request, game_to_complete: Optional[str] = None):
    """Gets the games for both tables and also allows marking a game as completed.

    This is so that when a game is marked as completed, it re-renders both tables to make them seem interactive.
    """
    if game_to_complete is not None:
        await game_service.mark_game_completed(game_to_complete)
    completed_games, current_games = await get_games_for_index()
    potential_winners = await get_potential_winners_list()
    return templates.TemplateResponse('partials/both_tables.html', {'request': request,
                                                                    "current_games": current_games,
                                                                    "completed_games": completed_games,
                                                                    "potential_winners": potential_winners})


@router.get('/current_games_table')
async def get_current_games_table(request: Request):
    """Get the games for the current games table.

    This allows us to use HTMX to render changes only to the current games.
    """
    completed_games, current_games = await get_games_for_index()
    potential_winners = await get_potential_winners_list()
    return templates.TemplateResponse('partials/current_games_table.html', {'request': request,
                                                                            "current_games": current_games,
                                                                            "completed_games": completed_games,
                                                                            "potential_winners": potential_winners})


@router.put('/completed_games_table')
async def get_completed_games_table(request: Request, game: Optional[str]):
    """Get the games for the completed games table.

    This allows us to use HTMX to render changes only to the completed games table.
    """
    form_data = await request.form()
    if form_data:
        winner = form_data['Winner']
        await game_service.add_winner_to_game(game, winner)
    completed_games, current_games = await get_games_for_index()
    potential_winners = await get_potential_winners_list()
    return templates.TemplateResponse('partials/completed_games_table.html', {'request': request,
                                                                              "current_games": current_games,
                                                                              "completed_games": completed_games,
                                                                              "potential_winners": potential_winners})
