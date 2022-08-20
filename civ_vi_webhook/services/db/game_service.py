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

# ToDO: check for game existence function, make create_game add game ID to CurrentGames, make mark game as finished function

