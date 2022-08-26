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
    games_to_return = []
    for game in games:
        time_stamp = {"year": game.game_info.time_stamp.year,
                      "month": game.game_info.time_stamp.month,
                      "day": game.game_info.time_stamp.day,
                      "hour": game.game_info.time_stamp.hour,
                      "minute": game.game_info.time_stamp.minute,
                      "second": game.game_info.time_stamp.second}
        player_name = await user_service.get_index_name_by_user_id(game.game_info.next_player_id)
        this_game = {"game_name": game.game_name, "player_name": player_name,
                     "average_turn_time": game.game_info.average_turn_time,
                     "winner": game.game_info.winner,
                     "turn_number": game.game_info.turn_number,
                     "time_stamp": time_stamp}
        games_to_return.append(this_game)
    return games_to_return


async def get_games_for_index() -> (list, list):
    current_games_raw = await game_service.get_current_games()
    if current_games_raw:
        current_games = await db_models_to_dictionary(current_games_raw)
    else:
        current_games = []
    completed_games_raw = await game_service.get_completed_games()
    completed_games = await db_models_to_dictionary(completed_games_raw)
    return completed_games, current_games


@router.get('/')
async def index(request: Request):
    completed_games, current_games = await get_games_for_index()
    potential_winners = await get_potential_winners_list()
    return templates.TemplateResponse('index.html', {'request': request,
                                                     "current_games": current_games,
                                                     "completed_games": completed_games,
                                                     "potential_winners": potential_winners})


@router.get('/favicon.ico')
def favicon():
    return fastapi.responses.RedirectResponse(url="/static/favicon.ico")


@router.get('/current_games_table')
async def get_current_games_table(request: Request):
    completed_games, current_games = await get_games_for_index()
    potential_winners = await get_potential_winners_list()
    return templates.TemplateResponse('partials/current_games_table.html', {'request': request,
                                                                            "current_games": current_games,
                                                                            "completed_games": completed_games,
                                                                            "potential_winners": potential_winners})


@router.get('/completed_games_table')
async def get_completed_games_table(request: Request):
    completed_games, current_games = await get_games_for_index()
    potential_winners = await get_potential_winners_list()
    return templates.TemplateResponse('partials/completed_games_table.html', {'request': request,
                                                                              "current_games": current_games,
                                                                              "completed_games": completed_games,
                                                                              "potential_winners": potential_winners})
