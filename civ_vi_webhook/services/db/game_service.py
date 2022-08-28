from datetime import datetime
from typing import Optional

from beanie.operators import In

from civ_vi_webhook import api_logger

from ...models.db.games import CompletedGames, CurrentGames, Game, GameInfo


async def create_game(game_name: str, player_id, turn_number: int, time_stamp: datetime, turn_deltas: list,
                      average_turn_time: str):
    all_players = {player_id}
    game_info = GameInfo(next_player_id=player_id, turn_number=turn_number, time_stamp_v2=time_stamp,
                         turn_deltas=turn_deltas, average_turn_time=average_turn_time, all_players=all_players)
    game = Game(game_name=game_name, game_info=game_info)
    await game.save()
    await add_game_to_current_games(game.id)


async def check_for_game(game_name: str) -> bool:
    """Check if the game already exists."""
    return bool(await Game.find_one(Game.game_name == game_name))


async def get_game(game_name: str) -> Game:
    """Return an existing game."""
    return await Game.find_one(Game.game_name == game_name)


async def create_current_games_document(initial_game_id=None):
    if initial_game_id:
        current_games_document = CurrentGames(current_games=[initial_game_id])
    else:
        current_games_document = CurrentGames(current_games=[])
    await current_games_document.save()


async def add_game_to_current_games(game_id):
    """Take in a Game ID and add it to the Current Games List."""
    current_games = await CurrentGames.find_one()
    if not current_games:
        await create_current_games_document(game_id)
    else:
        current_games.current_games.append(game_id)
        await current_games.save()


async def remove_game_from_current_games(game_id):
    """Remove a game ID from the current games"""
    current_games = await CurrentGames.find_one()
    current_games.current_games.remove(game_id)
    await current_games.save()


async def get_current_games(player_id: str = None) -> Optional[list[Game]]:
    """Get the current games (perhaps waiting on a specific player)."""
    current_games_document = await CurrentGames.find_one()
    games = await Game.find(In(Game.id, current_games_document.current_games)).sort(Game.game_info.time_stamp_v2).to_list()
    return [game for game in games if game.game_info.next_player_id == player_id] if player_id else games


async def create_completed_games_document(initial_game_id=None):
    if initial_game_id:
        completed_games = CompletedGames(completed_games=[initial_game_id])
        await remove_game_from_current_games(initial_game_id)
    else:
        completed_games = CompletedGames(completed_games=[])
    await completed_games.save()


async def update_game(game_name: str, player_id, turn_number: int, time_stamp: datetime, turn_deltas: list,
                      average_turn_time: str):
    game = await Game.find_one(Game.game_name == game_name)
    all_players = game.game_info.all_players
    all_players.add(player_id)
    game_info = GameInfo(next_player_id=player_id, turn_number=turn_number, time_stamp_v2=time_stamp,
                         turn_deltas=turn_deltas, average_turn_time=average_turn_time, all_players=all_players)
    game.game_info = game_info
    await game.save()


async def add_game_to_finished_games(game_id):
    completed_games = await CompletedGames.find_one()
    if not completed_games:
        await create_completed_games_document(game_id)
    else:
        completed_games.completed_games.append(game_id)
        await completed_games.save()
        await remove_game_from_current_games(game_id)


async def mark_game_completed(game_name: str):
    game = await Game.find_one(Game.game_name == game_name)
    game.game_info.game_completed = True
    await game.save()
    await add_game_to_finished_games(game.id)


async def add_winner_to_game(game_name: str, winner: str):
    game = await Game.find_one(Game.game_name == game_name)
    game.game_info.winner = winner
    await game.save()


async def get_total_game_count() -> int:
    """A count of all the games in the database."""
    return await Game.find().count()


async def get_current_games_count() -> int:
    """A count of all the games in progress in the database."""
    current_games_document = await CurrentGames.find_one()
    return await Game.find(In(Game.id, current_games_document.current_games)).count()


async def get_completed_games_count() -> int:
    """A count of all the games that are completed."""
    completed_games_document = await CompletedGames.find_one()
    if not completed_games_document:
        await create_completed_games_document()
        return 0
    return await Game.find(In(Game.id, completed_games_document.completed_games)).count()


async def get_completed_games() -> list[Game]:
    """Get the current games (perhaps waiting on a specific player)."""
    completed_games_document = await CompletedGames.find_one()
    if completed_games_document:
        games = await Game.find(In(Game.id, completed_games_document.completed_games)).sort(Game.game_info.time_stamp_v2).to_list()
        return games
    else:
        return []


async def remove_game_from_completed_games(game_id):
    """Remove a game ID from the completed games"""
    completed_games = await CompletedGames.find_one()
    completed_games.completed_games.remove(game_id)
    await completed_games.save()


async def get_all_games() -> list[Game]:
    """Get all the games in the database"""
    return await Game.find().to_list()


async def delete_game(game_name: str) -> bool:
    """Delete a game from the database"""
    game_exists = await check_for_game(game_name)
    if not game_exists:
        return False
    api_logger.debug("Game found, about to delete.")
    game_to_delete = await Game.find_one(Game.game_name == game_name)
    if game_to_delete.game_info.game_completed:
        api_logger.debug("Game had been marked as completed, removing from that list.")
        await remove_game_from_completed_games(game_to_delete.id)
    else:
        api_logger.debug("Game was not completed, removing from current games list.")
        await remove_game_from_current_games(game_to_delete.id)
    await game_to_delete.delete()
    return True


async def convert_to_new_time_stamp():
    """Convert from the old, dict time_stamp to the new datetime time_stamp_v2"""
    games = await Game.find().to_list()
    for game in games:
        if game.game_info.time_stamp:
            time_stamp = datetime(game.game_info.time_stamp.year,
                                  game.game_info.time_stamp.month,
                                  game.game_info.time_stamp.day,
                                  game.game_info.time_stamp.hour,
                                  game.game_info.time_stamp.minute,
                                  game.game_info.time_stamp.second)
            game.game_info.time_stamp_v2 = time_stamp
        await game.save()
