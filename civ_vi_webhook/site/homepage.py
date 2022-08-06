from fastapi import APIRouter
from starlette.requests import Request

from ..dependencies import templates, sort_games

router = APIRouter(tags=['index'])


def format_year_to_number(time_stamp: dict) -> int:
    """Take in a dict with time stamp and convert to a number"""
    return int(
        f"{time_stamp['year']}{time_stamp['month']:0>2d}{time_stamp['day']:0>2d}{time_stamp['hour']:0>2d}{time_stamp['minute']:0>2d}{time_stamp['second']:0>2d}")


@router.get('/')
def index(request: Request):
    completed_games, current_games = sort_games()
    return templates.TemplateResponse('index.html', {'request': request,
                                                     "current_games": current_games,
                                                     "completed_games": completed_games})


@router.get('/current_games_table')
def get_current_games_table(request: Request):
    completed_games, current_games = sort_games()
    return templates.TemplateResponse('partials/current_games_table.html', {'request': request,
                                                                            "current_games": current_games,
                                                                            "completed_games": completed_games})


@router.get('/completed_games_table')
def get_completed_games_table(request: Request):
    completed_games, current_games = sort_games()
    return templates.TemplateResponse('partials/completed_games_table.html', {'request': request,
                                                                              "current_games": current_games,
                                                                              "completed_games": completed_games})
