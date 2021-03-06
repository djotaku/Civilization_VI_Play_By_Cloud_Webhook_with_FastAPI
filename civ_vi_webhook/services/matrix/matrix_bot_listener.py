"""Provide ability to listen for commands fromMatrix."""

import asyncio
import json
import logging
from nio import AsyncClient
import requests


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
            logging.warning(f"Settings not found.")

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
        if player_to_blame == "":
            response = requests.get(f"{self.url}/current_games")
        else:
            response = requests.get(f"{self.url}/current_games", params={'player_to_blame': player_to_blame})
        if response.status_code == 200:
            return dict(response.json())
        elif response.status_code == 404:
            return {}

    def format_current_games(self):
        """Format the list of current games for display in Matrix server."""
        return_text = "Here is a list of the games currently known about on the server:\n"
        response_dictionary = self.get_current_games()
        if response_dictionary:
            for key in response_dictionary:
                game = key
                player = response_dictionary[key].get('player_name')
                turn_number = response_dictionary[key].get('turn_number')
                return_text += f"{game} awaiting turn {turn_number} by {player}\n"
                logging.debug(return_text)
        else:
            return_text = "There are no games available on the server. Or an error occurred."
        return return_text

    def format_blame_games(self, player_name: str) -> str:
        number_of_games = 0
        return_text = ""
        response_dictionary = self.get_current_games(player_name)
        response = requests.get(f"{self.url}/total_number_of_games")
        total_number_of_games = int(response.text)
        for key in response_dictionary:
            game = key
            turn_number = response_dictionary[key].get('turn_number')
            return_text += f"{game} awaiting turn {turn_number} by {player_name}\n"
            number_of_games += 1
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

    def decipher_commands(self, command: str) -> str:
        """Decide what the bot is being asked to do.

        :param command: A string containing a command for Civ_Bot.
        :returns: A formatted string for Civ_Bot to send to the room.
        """
        if command == "help":
            return """Current Commands:
                      !Civ_Bot help - this message
                      !Civ_Bot current games - the list of games Civ_Bot currently knows about.
                      !Civ_Bot blame <Matrix Username> - list of games waiting for that person."""

        elif command == "current games":
            return self.format_current_games()
        elif command.startswith("blame"):
            player_to_blame = command.lstrip("blame ")
            return self.format_blame_games(player_to_blame)
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
