"""Provide ability to listen for commands fromMatrix."""

import asyncio
from datetime import datetime
import json
import logging
import math
from nio import AsyncClient
import requests


logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s')


def figure_out_base_sixty(number: int) -> (int, int):
    """Figure out the next number up if I have more than 59 seconds or minutes."""
    if number > 59:
        return math.floor(number/60), number % 60
    else:
        return 0, number


def figure_out_days(number: int) -> (int, int):
    """Figure out number of days given a number of hours."""
    if number > 23:
        return math.floor(number/60), number % 60
    else:
        return 0, number


def return_time(time_difference) -> (int, int, int, int):
    """Return time in a useful manner."""
    days = time_difference.days
    seconds = time_difference.seconds
    minutes, seconds = figure_out_base_sixty(seconds)
    hours, minutes = figure_out_base_sixty(minutes)
    days_plus, hours = figure_out_days(hours)
    days += days_plus
    return days, hours, minutes, seconds


def determine_time_delta(year, month, day, hour, minute, second) -> str:
    time_of_question = datetime.now()
    time_of_turn = datetime(year, month, day, hour, minute, second)
    difference = time_of_question - time_of_turn
    days, hours, minutes, seconds = return_time(difference)
    return f"It's been {days} days {hours} hours {minutes} minutes {seconds} seconds since the last turn."


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
                return_text += f"{game} awaiting turn {turn_number} by {player}. "
                if response_dictionary[key].get('time_stamp'):
                    time_text = determine_time_delta(response_dictionary[key]['time_stamp']['year'],
                                                     response_dictionary[key]['time_stamp']['month'],
                                                     response_dictionary[key]['time_stamp']['day'],
                                                     response_dictionary[key]['time_stamp']['hour'],
                                                     response_dictionary[key]['time_stamp']['minute'],
                                                     response_dictionary[key]['time_stamp']['second'])
                    return_text += time_text
                return_text += '\n'
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
            return_text += f"{game} awaiting turn {turn_number} by {player_name} "
            if response_dictionary[key].get('time_stamp'):
                time_text = determine_time_delta(response_dictionary[key]['time_stamp']['year'],
                                                 response_dictionary[key]['time_stamp']['month'],
                                                 response_dictionary[key]['time_stamp']['day'],
                                                 response_dictionary[key]['time_stamp']['hour'],
                                                 response_dictionary[key]['time_stamp']['minute'],
                                                 response_dictionary[key]['time_stamp']['second'])
                return_text += time_text
            return_text += '\n'
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
