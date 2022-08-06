# Matrix Service

This presumes that you've created an account for the Matrix bot and invited it to the room specified in the matrix.conf. 

You will also need to sign in as the bot and accept the invite.

Once your bot has joined the room, you can interact with it via the following commands:

- !Civ_Bot help - this message
- !Civ_Bot current games - the list of games Civ_Bot currently knows about.
- !Civ_Bot blame <Matrix Username> - list of games waiting for that person.
- !Civ_Bot delete <name of game> - delete the game from the database.
- !Civ_Bot complete <name of game> - mark the game as deleted

Some example output from my server:

I typed: !Civ_Bot current games

and the server returned (I have added the bullets for the sake of making the markdown legible):

- Corpo Scum! awaiting turn 171 by Dan. It's been 208 days 1 hours 58 minutes 22 seconds since the last turn.
- Secret Allies awaiting turn 192 by David. It's been 187 days 0 hours 54 minutes 41 seconds since the last turn.
- Zoombie ee ee ee awaiting turn 229 by Dan. It's been 156 days 1 hours 9 minutes 44 seconds since the last turn.
- 1st Rise and Fall Game awaiting turn 137 by Eric. It's been 72 days 5 hours 18 minutes 46 seconds since the last turn.
- Game 3! awaiting turn 140 by Eric. It's been 72 days 5 hours 25 minutes 13 seconds since the last turn.
- Gathering Storm! 2 awaiting turn 88 by David. It's been 19 days 5 hours 14 minutes 40 seconds since the last turn.
- Gathering Storm! 1 awaiting turn 92 by Eric. It's been 72 days 5 hours 21 minutes 43 seconds since the last turn.
- Mesas Play awaiting turn 230 by Dan. It's been 0 days 0 hours 35 minutes 17 seconds since the last turn.
- Eric and Dan Duel awaiting turn 69 by Dan. It's been 0 days 0 hours 33 minutes 2 seconds since the last turn.
- Duel with Dave awaiting turn 45 by David. It's been 0 days 0 hours 31 minutes 25 seconds since the last turn.
- One Oh Eight's Game awaiting turn 42 by Dan. It's been 0 days 16 hours 30 minutes 34 seconds since the last turn.
- Race to the Stars! awaiting turn 32 by Dan. It's been 0 days 16 hours 20 minutes 31 seconds since the last turn.
- Dark Age is Coming! awaiting turn 133 by Eric. It's been 72 days 15 hours 2 minutes 27 seconds since the last turn.
- Stormy Game awaiting turn 89 by David. It's been 19 days 5 hours 10 minutes 38 seconds since the last turn.
- Dan Will Rise. His Brothers Will Fall. awaiting turn 135 by David. It's been 19 days 5 hours 7 minutes 1 seconds since the last turn.
- Deity vs. Shlubs awaiting turn 169 by David. It's been 150 days 21 hours 10 minutes 39 seconds since the last turn.
- Join the Team! awaiting turn 174 by David. It's been 144 days 22 hours 13 minutes 8 seconds since the last turn.
- Challenge awaiting turn 133 by David. It's been 72 days 5 hours 37 minutes 26 seconds since the last turn.
- Culture Club awaiting turn 122 by Dan. It's been 0 days 15 hours 25 minutes 19 seconds since the last turn.
- Science Club awaiting turn 88 by David. It's been 72 days 5 hours 28 minutes 35 seconds since the last turn.

When I typed !Civ_Bot blame Eric

the server responded with (again, I've added bullets for legibility with markdown on this page):

There are 4 games out of 18 waiting for Eric to take their turn:
- 1st Rise and Fall Game awaiting turn 137 by Eric. It's been 72 days 5 hours 31 minutes 10 seconds since the last turn.
- Game 3! awaiting turn 140 by Eric. It's been 72 days 5 hours 37 minutes 37 seconds since the last turn.
- Gathering Storm! 1 awaiting turn 92 by Eric. It's been 72 days 5 hours 34 minutes 7 seconds since the last turn.
- Dark Age is Coming! awaiting turn 133 by Eric. It's been 72 days 15 hours 14 minutes 51 seconds since the last turn.