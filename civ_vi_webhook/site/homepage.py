import logging

import fastapi
from fastapi import APIRouter
from starlette.requests import Request

from ..dependencies import templates, sort_games, load_player_names

router = APIRouter(tags=['index'])


def get_potential_winners_list() -> list:
    """Get a list of potential selections for winners"""
    players = load_player_names()
    winners = [f"{key} (aka {value})" for key, value in players['preferred_names'].items()]
    # logging.debug(winners)
    winners.extend(("Other Player", "Computer Player"))
    return winners


@router.get('/')
def index(request: Request):
    completed_games, current_games = sort_games()
    potential_winners = get_potential_winners_list()
    return templates.TemplateResponse('index.html', {'request': request,
                                                     "current_games": current_games,
                                                     "completed_games": completed_games,
                                                     "potential_winners": potential_winners})


@router.get('/favicon.ico')
def favicon():
    return fastapi.responses.RedirectResponse(url='static/favicon.ico')


@router.get('/current_games_table')
def get_current_games_table(request: Request):
    completed_games, current_games = sort_games()
    potential_winners = get_potential_winners_list()
    return templates.TemplateResponse('partials/current_games_table.html', {'request': request,
                                                                            "current_games": current_games,
                                                                            "completed_games": completed_games,
                                                                            "potential_winners": potential_winners})


@router.get('/completed_games_table')
def get_completed_games_table(request: Request):
    completed_games, current_games = sort_games()
    potential_winners = get_potential_winners_list()
    return templates.TemplateResponse('partials/completed_games_table.html', {'request': request,
                                                                              "current_games": current_games,
                                                                              "completed_games": completed_games,
                                                                              "potential_winners": potential_winners})
