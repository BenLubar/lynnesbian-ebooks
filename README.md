# mstdn-ebooks
**Lynnear Edition**

This version makes quite a few changes from [the original](https://github.com/Jess3Jane/mastodon-ebooks), such as:
- Unicode support
- Non-Markov stuff
- Meme generation with ImageMagick
- Stores toots in a sqlite database rather than a text file
  - Doesn't unecessarily redownload all toots every time
- its very cute

For an example of what this bot can do, see [this botsin.space account](https://botsin.space/@lynnesbian_ebooks).

## Install/usage guide
An installation and usage guide is available for unix-based platforms (linux, macOS...) [here](https://cloud.lynnesbian.space/s/Qxxm2sYdMZaqWat).

## Install/usage guide
An installation and usage guide is available for unix-based platforms (linux, macOS...) [here](https://cloud.lynnesbian.space/s/Qxxm2sYdMZaqWat).

## Original README
hey look it's an ebooks bot

python3

install the requirements with `sudo pip3 install -r requirements`

make a bot (probably on bots in space) and follow the target accounts

run `python3 main.py` to login and scrape

run `python3 gen.py` to make a toot

cron is an okay choice to make it toot regularly
