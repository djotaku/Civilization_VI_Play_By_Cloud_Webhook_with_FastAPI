import fastapi.responses
from fastapi import APIRouter
from starlette.requests import Request

from ..dependencies import load_player_names, sort_games, templates
from ..services.db import user_service, game_service
router = APIRouter(tags=['index'])


async def get_potential_winners_list() -> list:
    """Get a list of potential selections for winners"""
    winners = await user_service.get_all_index_names()
    winners.extend(("Other Player", "Computer Player"))
    return winners


async def get_games_for_index() -> (list, list):
    current_games = await game_service.get_current_games()


@router.get('/')
async def index(request: Request):
    completed_games, current_games = sort_games()
    current_games_from_db = await game_service.get_current_games()
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
    completed_games, current_games = sort_games()
    potential_winners = await get_potential_winners_list()
    return templates.TemplateResponse('partials/current_games_table.html', {'request': request,
                                                                            "current_games": current_games,
                                                                            "completed_games": completed_games,
                                                                            "potential_winners": potential_winners})


@router.get('/completed_games_table')
async def get_completed_games_table(request: Request):
    completed_games, current_games = sort_games()
    potential_winners = await get_potential_winners_list()
    return templates.TemplateResponse('partials/completed_games_table.html', {'request': request,
                                                                              "current_games": current_games,
                                                                              "completed_games": completed_games,
                                                                              "potential_winners": potential_winners})
