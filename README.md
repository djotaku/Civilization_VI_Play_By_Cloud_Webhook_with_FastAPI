# Civilization VI Play By Cloud (And Play Your Damn Turn) Webhook (with Python FastAPI)

Using Python FastAPI creates a webhook endpoint for Civilization VI's Play By Cloud or [Play Your Damn Turn](https://www.playyourdamnturn.com/) Webhooks and pushes notifications to Matrix.

I will accept Pull Requests to add other services: eg Discord, Telegram, Email, SMS, etc

## Updates

A mini dev log until I get things fully operational

20210303 - I have ported over much of the helper code from my Flask implementation. I haven't copied over the real main.py yet, it's just the hello world example so that I could check out functionality of uvicorn vs gunicorn. I have decided that for my first version (0.1?) I will just port the Flask implementation almost line-for-line rather than taking advantage of the benefits of FastAPI. I have a long list of changes I want to make both to take better advantage of FastAPI and just a few ideas I had on how to make the code more portable once I decided to share it on Github (and perhaps eventually make a Python Package on PyPi).

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
"gameName": "the name of your game",
"userName": "the user's Steam username",
"round": 0,
"civName": "the name of your civilization",
"leaderName": "the name of your civ leader (and for some of them the attribute)"
}
```
This is why I have two different endpoints, one for Play by Cloud and one for Play Your Damn Turn (PYDT). Also note that the PBC turn number is a string while the PYDT JSON is an integer.

## How to use this code on your own

20210302 - Yes, yes...the full code isn't here yet. I originally wrote the code using Flask and this repo will be for the FastAPI rewrite. Luckily, it's very easy to translate from one to the other, so I plan to have working FastAPI code this upcoming weekend.

notes on steps for later:
for dev:
- create a virtual environment 
- pip install -r requirements.txt
- edit the config files with the appropriate data
- run the server and listener scripts
- set up Civilization VI (and, optionally PYDT) with the webhook API URL
if end up making a Python package:
  -the steps needed there - some of the above about be covered by the package