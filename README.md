# Epic-Gamer-2
An epic bot that does epic things.

This is an ongoing project that I work on from time to time. Epic Gamer 2 is a rewrite of my original epic gamer discord bot. This bot currently has configuration, developer, economy, fun, info, and suggestion commands. Check out the source code for these commands in the `extensions` directory.

## Installation
- Install the latest version of Python
- Clone this repository via:
```git clone https://github.com/NatFletch/Epic-Gamer-2.git```
- Install all the required packages via
```pip install -r requirements.txt```
- Make a file at the top of the project directory called `conf.py`
- Inside `conf.py` at the following variables
```py
embed_color = # color code in memory address format (eg: 0xff0000)
token = "bottokengoeshere" # bot token goes here (str)
database_url = "postgres://urlforyourdatabasegoeshere" # url to database goes here (str)
economy = "Name of your currency goes here" # The name that will be used for currency. eg "coins" will make the the unit for the economy currency coins (str)
```
