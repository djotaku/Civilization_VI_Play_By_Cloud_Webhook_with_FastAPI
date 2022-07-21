import json

from civ_vi_webhook import api_logger


def load_most_recent_games() -> dict:
    """Loads in the most recent games from the JSON file."""
    games = {}
    try:
        with open('most_recent_games.json', 'r') as file:
            games = json.load(file)
            api_logger.debug("current_games file loaded.")
    except FileNotFoundError:
        api_logger.warning("Prior JSON file not found. If this is your first run, this is OK.")
    return games
