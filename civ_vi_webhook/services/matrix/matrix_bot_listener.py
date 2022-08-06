"""Provide ability to listen for commands fromMatrix."""

import asyncio
import json
import logging
from nio import AsyncClient
import requests

from civ_vi_webhook.dependencies import determine_time_delta

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s')


class ListenerMatrixBot:
    """A bot to send alerts about the game to Matrix"""

    def __init__(self):
        try:
            with open('matrix.conf') as file:
                self.config = json.load(file)
                logging.debug("Listener Matrix Config loaded.")
                file.close()
                self.url = self.config.get('webhook_url')
        except FileNotFoundError:
            logging.warning("Settings not found.")

    async def login(self):
        client = AsyncClient(self.config.get('server'), self.config.get('username'))
        response = await client.login(password=self.config.get("password"))
        logging.info(f"Listener Login response: {response}")
        logging.debug(f"Listener Room would be: {self.config.get('room')}")
        return client

    def get_current_games(self, player_to_blame: str = ""):
        """Get the list of games from the recent games endpoint.

        :returns: A dictionary of the games, next player, and turn number.
        """
        response = requests.get(f"{self.url}/current_games",
                                params={'player_to_blame': player_to_blame}) if player_to_blame else requests.get(
            f"{self.url}/current_games")

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {}

    @staticmethod
    def format_response_text(games_list: list[dict]) -> str:
        """Format the list of games for both format_current games and format_blame_games"""
        return_text = ""
        for game in games_list:
            game_name = game['game_name']
            player = game['game_info'].get('player_name')
            turn_number = game['game_info'].get('turn_number')
            return_text += f"{game_name} awaiting turn {turn_number} by {player}. "
            if game['game_info'].get('time_stamp'):
                time_text = determine_time_delta(game['game_info']['time_stamp']['year'],
                                                 game['game_info']['time_stamp']['month'],
                                                 game['game_info']['time_stamp']['day'],
                                                 game['game_info']['time_stamp']['hour'],
                                                 game['game_info']['time_stamp']['minute'],
                                                 game['game_info']['time_stamp']['second'])
                return_text += time_text
            return_text += '\n'
        return return_text

    def format_current_games(self):
        """Format the list of current games for display in Matrix server."""
        return_text = "Here is a list of the games currently known about on the server:\n"
        if response_json := self.get_current_games():
            response = response_json
            games = response['games']
            logging.debug(f"{games=}")
            return_text += self.format_response_text(games)
            logging.debug(return_text)
        else:
            return_text = "There are no games available on the server. Or an error occurred."
        return return_text

    def format_blame_games(self, player_name: str) -> str:
        number_of_games = 0
        return_text = ""
        response = requests.get(f"{self.url}/total_number_of_games")
        total_number_of_games = response.json().get('total_games')
        if response_json := self.get_current_games(player_name):
            response = response_json
            games = response['games']
            return_text += self.format_response_text(games)
            logging.debug(return_text)
            number_of_games = len(games)
        if 0 < number_of_games < 2:
            return f"There is {number_of_games} game out of {total_number_of_games} waiting for {player_name} " \
                   f"to take their turn:\n" + return_text
        elif number_of_games > 1:
            if number_of_games == total_number_of_games:
                return f"There are {number_of_games} games out of {total_number_of_games} waiting for {player_name} " \
                       f"to take their turn:\n" + return_text + "It's all on you!! 😅"
            else:
                return f"There are {number_of_games} games out of {total_number_of_games} waiting for {player_name} " \
                       f"to take their turn:\n" + return_text
        else:
            return f"There aren't any games waiting for {player_name}. Great job!"

    def delete_game(self, game_to_delete: str) -> str:
        """Delete the game requested by the user.

        If that isn't a game, let the user know.

        :param game_to_delete: The Game to delete.
        :returns: A string letting the user know the success or failure of the deletion.
        """
        response = requests.delete(f"{self.url}/delete_game", params={'game_to_delete': game_to_delete})
        if response.status_code == 200:
            game_info = response.json()
            return f"Deleted {game_info['deleted_game']}"
        elif response.status_code == 404:
            return f"{game_to_delete} was not in the system."

    def complete_game(self, game_to_complete: str) -> str:
        """Mark the game as completed in the database.

        If the game doesn't exist, let the user know.

        :param game_to_complete: The game to mark as completed
        :returns: A string to let the user know if it succeeded or not.
        """
        response = requests.put(f"{self.url}/complete_game", params={'game_to_complete': game_to_complete})
        if response.status_code == 200:
            completion_status = response.json()
            logging.debug(f"{completion_status=}")
            return f"Marked {completion_status['completed_game']['game_name']} as completed."
        elif response.status_code == 404:
            return f"{game_to_complete} was not found. Did you spell it correctly?"

    def decipher_commands(self, command: str) -> str:
        """Decide what the bot is being asked to do.

        :param command: A string containing a command for Civ_Bot.
        :returns: A formatted string for Civ_Bot to send to the room.
        """
        if command == "help":
            return """Current Commands:
                      !Civ_Bot help - this message
                      !Civ_Bot current games - the list of games Civ_Bot currently knows about.
                      !Civ_Bot blame <Matrix Username> - list of games waiting for that person.
                      !Civ_Bot delete <name of game> - delete the game from the database.
                      !Civ_Bot complete <name of game> - mark the game as deleted
                      """

        elif command == "current games":
            return self.format_current_games()
        elif command.startswith("blame"):
            player_to_blame = command.lstrip("blame ")
            return self.format_blame_games(player_to_blame)
        elif command.startswith("delete"):
            game = command.lstrip("delete ")
            return self.delete_game(game)
        elif command.startswith("complete"):
            game = command.lstrip("complete ")
            return self.complete_game(game)
        else:
            return "Sorry, I didn't recognize that command. Try !Civ_Bot help to see command list."

    async def main(self):
        my_client = await self.login()
        with open('next_batch', 'r') as next_batch_token:
            my_client.next_batch = next_batch_token.read()
        while True:
            sync_response = await my_client.sync(30000)
            with open('next_batch', 'w') as next_batch_token:
                next_batch_token.write(sync_response.next_batch)
            if len(sync_response.rooms.join) > 0:
                joins = sync_response.rooms.join
                for room_id in joins:
                    for event in joins[room_id].timeline.events:
                        if hasattr(event, 'body') and event.body.startswith("!Civ_Bot"):
                            data_to_send = self.decipher_commands(event.body.lstrip("!Civ_Bot "))
                            logging.debug(data_to_send)
                            content = {"body": data_to_send, "msgtype": "m.text"}
                            await my_client.room_send(room_id, 'm.room.message', content)


my_matrix_bot = ListenerMatrixBot()
asyncio.run(my_matrix_bot.main())
