import logging
from collections import OrderedDict
from fastapi import APIRouter
from starlette.requests import Request

from ..dependencies import templates, load_most_recent_games

router = APIRouter(tags=['index'])


def format_number(number: str) -> str:
    """Take in a number than can potentially have a tens place and add a zero if needed"""
    return f"{number:>2d}"


def format_year_to_number(time_stamp: dict) -> int:
    """Take in a dict with time stamp and convert to a number"""
    return int(
        f"{time_stamp['year']}{time_stamp['month']:>2d}{time_stamp['day']:>2d}{time_stamp['hour']:>2d}{time_stamp['minute']:>2d}{time_stamp['second']:>2d}")


def sort_games() -> (dict, dict):
    """Sort the games into current and completed."""
    all_games = load_most_recent_games()
    sorted_by_timestamp = OrderedDict(
        sorted(all_games.items(), key=lambda k: format_year_to_number(k[1]['time_stamp'])))
    current_games = OrderedDict()
    completed_games = OrderedDict()
    for game in sorted_by_timestamp:
        if sorted_by_timestamp[game].get("game_completed"):
            completed_games[game] = sorted_by_timestamp[game]
        else:
            current_games[game] = sorted_by_timestamp[game]
    # logging.debug(f"{current_games=}")
    # logging.debug(completed_games)
    return completed_games, current_games


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
