# votebloke.application

### Summary
This is the implementation of Python-based, front-end application for interaction with VoteBloke blockchain infrastructure.


### Core functionalities include:
* creating a user account (generating eliptic curve key)
* importing and exporting the created keys
* creating new elections/polls
* loading elections available for voiting
* casting a vote
* closing elections and counting votes
* viewing election results on an interactive chart

### Running 
The app is browser-based and runs on a port 21317 bv default. To start, please run script 'application.py' with your python interpreter and with folder 'app' as a working directory.
Required dependencies are listed in this [file](https://github.com/VoteBloke/votebloke.application/blob/main/requirements.txt).

Please note, that for the application to run properly, you need available blockchain [fullnode](https://github.com/VoteBloke/votebloke.fullnode) server.
