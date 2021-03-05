"""Provide ability to send alerts to Matrix."""

import asyncio
import json
import logging
from nio import AsyncClient

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s')


class MatrixBot:
    """A bot to send alerts about the game to Matrix"""
    def __init__(self):
        try:
            with open('matrix.conf') as file:
                self.config = json.load(file)
                logging.debug("Alert Matrix Bot Config loaded.")
                file.close()
        except FileNotFoundError:
            logging.warning(f"Settings not found.")

    async def send_message(self, message: str):
        client = AsyncClient(self.config.get('server'), self.config.get('username'))
        response = await client.login(password=self.config.get("password"))
        logging.info(f"Alert Matrix Bot Login response: {response}")
        logging.debug(f"Alert Matrix Bot has joined room would be: {self.config.get('room')}")
        msg_response = await client.room_send(room_id=self.config.get('room'), message_type="m.room.message",
                                              content={"msgtype": "m.text", "body": message})
        logging.debug(f"Message Response: {msg_response}")
        await client.close()

    def main(self, message):
        asyncio.run(self.send_message(message))


if __name__ == "__main__":
    my_matrix_bot = MatrixBot()
    my_matrix_bot.main("Test message: You have settled too close to my boundaries!")
