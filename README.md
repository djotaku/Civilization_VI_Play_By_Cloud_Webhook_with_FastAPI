# Civilization VI Play By Cloud (And Play Your Damn Turn) Webhook (with Python FastAPI)

Using Python FastAPI creates a webhook endpoint for Civilization VI's Play By Cloud or [Play Your Damn Turn](https://www.playyourdamnturn.com/) Webhooks and pushes notifications to Matrix.

I will accept Pull Requests to add other services: eg Discord, Telegram, Email, SMS, etc

Note: while there is no code right now - I have already created [this functionality with Flask](http://www.ericsbinaryworld.com/2021/03/01/programming-jan-feb-2021/#civ-vi-play-by-cloud-webhook), but on reddit someone told me that FastAPI would be much better for a simple JSON API program like this one. After looking at FastAPI's documentation - I agree that for this particular program - FastAPI would produce cleaner, self-documenting, easier to maintain code.

## Introduction

February 2019, Firaxis added Play by Cloud to Civilization VI. Previously, you had to use a third party service for Play by Email (PBEM) like [Play Your Damn Turn](https://www.playyourdamnturn.com/). Recently, I started using Play by Cloud, but I found the Steam Alerts lacking. Luckily, the startup diaglog tells you about webhooks. Unfortunately, when I searched the web, there were many implementations, but not much explanation that would help me develop my own solution. Most of what you will find out there involves setting up a webhook for integration with Discord and/or involves PHP or Javascript. I'm not that big on Discord. I have a Matrix server and I am a Python programmer. So I set about to figure this out on my own. 

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
"gameName": "the name of your game",
"userName": "the user's Steam username",
"round": the round number (int),
"civName": "the name of your civilization",
"leaderName": "the name of your civ leader (and for some of them the attribute)"
}
```
This is why I have two different endpoints, one for Play by Cloud and one for Play Your Damn Turn (PYDT).

## How to use this code on your own

20210302 - Yes, yes...there's no code here yet. I originally wrote the code using Flask and this repo will be for the FastAPI rewrite. Luckily, it's very easy to translate from one to the other, so I plan to have working FastAPI code this upcoming weekend.

notes on steps for later:
- create a virtual environment
- pip install -r requirements.txt
- edit the config files with the appropriate data
- run the server and listener scripts
- set up Civilization VI (and, optionally PYDT) with the webhook API URL
