from fastapi import APIRouter
from starlette.requests import Request

from ..dependencies import templates, load_most_recent_games


router = APIRouter(tags=['index'])


@router.get('/')
def index(request: Request):
    all_games = load_most_recent_games()
    current_games = dict()
    completed_games = dict()
    for game in all_games:
        if all_games[game].get("game_completed"):
            completed_games[game] = all_games[game]
        else:
            current_games[game] = all_games[game]
    return templates.TemplateResponse('index.html', {'request': request,
                                                     "current_games": current_games,
                                                     "completed_games": completed_games})
