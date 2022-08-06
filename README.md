# Civilization VI Play By Cloud (And Play Your Damn Turn) Webhook (with Python FastAPI)

Using Python FastAPI creates a webhook endpoint for Civilization VI's Play By Cloud or [Play Your Damn Turn](https://www.playyourdamnturn.com/) Webhooks and pushes notifications to Matrix.

I will accept Pull Requests to add other services: eg Discord, Telegram, Email, SMS, Mastodon, etc

## Introduction

February 2019, Firaxis added Play by Cloud to Civilization VI. Previously, you had to use a third party service for Play by Email (PBEM) like [Play Your Damn Turn](https://www.playyourdamnturn.com/). Recently, I started using Play by Cloud, but I found the Steam Alerts lacking. Luckily, the startup dialog tells you about webhooks. Unfortunately, when I searched the web, there were many implementations, but not much explanation that would help me develop my own solution. Most of what you will find out there involves setting up a webhook for integration with Discord and/or involves PHP or Javascript. I'm not that big on Discord. I have a Matrix server and I am a Python programmer. So I set about to figure this out on my own.

I first created [this functionality with Flask](http://www.ericsbinaryworld.com/2021/03/01/programming-jan-feb-2021/#civ-vi-play-by-cloud-webhook), but on reddit someone told me that FastAPI would be much better for a simple JSON API program like this one. After looking at FastAPI's documentation - I agree that for this particular program - FastAPI would produce cleaner, self-documenting, easier to maintain code.

### The Payload

As of March 2021, unfortunately the payload sent by Play by Cloud is rather annoyingly named and barebones. It looks like this:

```JSON
{
"value1": "the name of your game",
"value2": "the player's Steam name",
"value3": "the turn number"
}
```
If you happen to already be using (or prefer) Play Your Damn Turn (PYDT), they use a richer API for their payload:

```JSON
{
"value1": "the name of your game",
"value2": "the player's Steam name",
"value3": "the turn number",
"gameName": "the name of your game",
"userName": "the user's Steam username",
"round": 0,
"civName": "the name of your civilization",
"leaderName": "the name of your civ leader (and for some of them the attribute)"
}
```
This is why I have two different endpoints, one for Play by Cloud and one for Play Your Damn Turn (PYDT).

## Endpoints

All of this is documented in the code and by visiting the URL where you are running this code /docs eg: mycivilizationwebhooks.com/docs . Here is a brief overview:

If we assume your URL is mycivilizationwebhooks.com, then:

mycivilizationwebhooks.com/webhook - this is the endpoint to enter into Civ VI. It will create a message after each turn and send it to Matrix

mycivilizationwebhooks.com/pydt - this is the endpoint to enter into Play Your Damn Turn. It will create a message after each turn and send it to Matrix.

mycivilizationwebhooks.com/current_games - will return all the games the program knows about

mycivilizationwebhooks.com/delete_game - it will delete the game you pass to it. Say, when you're done with the game and no longer want to track it.

## How to use this code on your own

I have switched to using Poetry to develop and run this project. 

Pre-requirements
- poetry (installed via your OS's package manager)
- nginx or apachie web server

On a server running Nginx or Apache, go to the folder that will contain this code. Clone the git repo.

Install the dependencies:

```bash
poetry install
```

Copy the sample_matrix.conf file to the main directory of the program. (The same directory with the server and listener bash scripts) Edit the values to match those of a user you have created on the Matrix server to be a bot. 

Using 2 terminals or a terminal muxer like screen or tmux, use one window for the server script and one for the listener script.

in one terminal or window serve the FastAPI app via Uvicorn:
```bash
poetry shell
uvicorn civ_vi_webhook.main:app --port 5000 --host 0.0.0.0 --reload
```

in the other one start the Matrix listener bot to listen for commands in Matrix: 
```bash
poetry shell
python -m civ_vi_webhook.services.matrix.matrix_bot_listener.py
```

Set up Nginx or Ampache to serve requests to your URL to uvicorn's port.

Set up Civilization VI (for Play by Cloud) or Play Your Damn Turn to point to the appropriate endpoints.