from fastapi import APIRouter
from starlette.requests import Request

from ..dependencies import templates, load_most_recent_games

router = APIRouter(tags=['index'])


def sort_games() -> (dict, dict):
    """Sort the games into current and completed."""
    all_games = load_most_recent_games()
    current_games = {}
    completed_games = {}
    for game in all_games:
        if all_games[game].get("game_completed"):
            completed_games[game] = all_games[game]
        else:
            current_games[game] = all_games[game]
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
