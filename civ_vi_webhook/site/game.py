from fastapi import APIRouter
from starlette.requests import Request

from ..dependencies import db_game_to_dictionary, templates
from ..services.db import game_service

router = APIRouter(tags=['game', 'site'], include_in_schema=False)


async def get_game(game_name: str) -> dict:
    """Get a game from the DB."""
    game = await game_service.get_game(game_name)
    return await db_game_to_dictionary(game) if game else {}


@router.get('/game/{game_name}')
async def game_details(request: Request, game_name: str):
    details = await get_game(game_name)
    return templates.TemplateResponse('game_details.html', {'request': request,
                                                            'game': details})
