from fastapi import APIRouter
from starlette.requests import Request

from ..dependencies import templates, load_most_recent_games


router = APIRouter(tags=['index'])


@router.get('/')
def index(request: Request):
    current_games = load_most_recent_games()
    print(current_games)
    return templates.TemplateResponse('index.html', {'request': request,
                                                     "current_games": current_games})
