from fastapi import APIRouter
from starlette.requests import Request

from ..dependencies import templates, sort_games

router = APIRouter(tags=['index'])


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
