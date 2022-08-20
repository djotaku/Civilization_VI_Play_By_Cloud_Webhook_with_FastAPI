from ...models.db.games import Game, CompletedGames, CurrentGames, GameInfo, TimeStamp


async def create_game(game_name: str, player_id: str, turn_number: int, time_stamp: dict, turn_deltas: list,
                      average_turn_time: str, all_players: set):
    time_stamp = TimeStamp(year=time_stamp.get("year"), month=time_stamp.get("month"),
                           day=time_stamp.get("day"), hour=time_stamp.get("hour"), minute=time_stamp.get("minute"),
                           second=time_stamp.get("second"))
    all_players.add(player_id)
    game_info = GameInfo(next_player_id=player_id, turn_number=turn_number, time_stamp=time_stamp,
                         turn_deltas=turn_deltas, average_turn_time=average_turn_time, all_players=all_players)
    game = Game(game_name=game_name, game_info=game_info)
    await game.save()
    await add_game_to_current_games(str(game.id))


async def check_for_game(game_name: str) -> bool:
    """Check if the game already exists."""
    return bool(game := await Game.find_one(Game.game_name == game_name))


async def get_game(game_name: str) -> Game:
    """Return an existing game."""
    return await Game.find_one(Game.game_name == game_name)


async def create_current_games_document():
    current_games_document = CurrentGames(current_games=[])
    await current_games_document.save()


async def add_game_to_current_games(game_id: str):
    """Take in a Game ID and add it to the Current Games List."""
    current_games = await CurrentGames.find_one()
    if not current_games:
        await create_current_games_document()
    current_games.current_games.append(game_id)
    await current_games.save()


async def create_completed_games_document():
    completed_games = CompletedGames(completed_games=[])
    await completed_games.save()


async def update_game(game_name: str, player_id: str, turn_number: int, time_stamp: dict, turn_deltas: list,
                      average_turn_time: str, all_players: set):
    game = await Game.find_one(Game.game_name == game_name)
    time_stamp = TimeStamp(year=time_stamp.get("year"), month=time_stamp.get("month"),
                           day=time_stamp.get("day"), hour=time_stamp.get("hour"), minute=time_stamp.get("minute"),
                           second=time_stamp.get("second"))
    all_players.add(player_id)
    game_info = GameInfo(next_player_id=player_id, turn_number=turn_number, time_stamp=time_stamp,
                         turn_deltas=turn_deltas, average_turn_time=average_turn_time, all_players=all_players)
    game.game_info = game_info
    await game.save()


async def add_game_to_finished_games(game_id: str):
    completed_games = await CompletedGames.find_one()
    if not completed_games:
        await create_completed_games_document()
    completed_games.completed_games.append(game_id)
    await completed_games.save()


async def mark_game_completed(game_name: str):
    game = await Game.find_one(Game.game_name == game_name)
    game.game_info.game_completed = True
    await game.save()
    await add_game_to_finished_games(str(game.id))
