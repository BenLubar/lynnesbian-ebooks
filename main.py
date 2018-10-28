#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from mastodon import Mastodon
from os import path
from bs4 import BeautifulSoup
import os, sqlite3, signal, sys, json, re
import requests
# import re

scopes = ["read:statuses", "read:accounts", "read:follows", "write:statuses"]
cfg = json.load(open('config.json', 'r'))

if "client" not in cfg:
	print("No client credentials, registering application")
	client_id, client_secret = Mastodon.create_app("mstdn-ebooks",
		api_base_url=cfg['site'],
		scopes=scopes,
		website="https://github.com/Lynnesbian/mstdn-ebooks")

	cfg['client'] = {
		"id": client_id,
		"secret": client_secret
	}

if "secret" not in cfg:
	print("No user credentials, logging in")
	client = Mastodon(client_id = cfg['client']['id'],
		client_secret = cfg['client']['secret'],
		api_base_url=cfg['site'])

	print("Open this URL: {}".format(client.auth_request_url(scopes=scopes)))
	cfg['secret'] = client.log_in(code=input("Secret: "), scopes=scopes)

json.dump(cfg, open("config.json", "w+"))

def parse_toot(toot):
	if toot.spoiler_text != "": return
	if toot.reblog is not None: return
	# if toot.visibility not in ["public", "unlisted"]: return

	soup = BeautifulSoup(toot.content, "html.parser")
	
	# this is the code that removes all mentions
	# TODO: make it so that it removes the @ and instance but keeps the name
	for mention in soup.select("span.h-card"):
		mention.decompose()
	
	# make all linebreaks actual linebreaks
	for lb in soup.select("br"):
		lb.insert_after("\n")
		lb.decompose()

	# make each p element its own line because sometimes they decide not to be
	for p in soup.select("p"):
		p.insert_after("\n")
		p.unwrap()
	
	# keep hashtags in the toots
	for ht in soup.select("a.hashtag"):
		ht.unwrap()

	# unwrap all links (i like the bots posting links)
	for link in soup.select("a"):
		link.insert_after(link["href"])
		link.decompose()

	text = map(lambda a: a.strip(), soup.get_text().strip().split("\n"))

	#todo: we split above and join now, which is dumb, but i don't wanna mess with the map code bc i don't understand it uwu
	text = "\n".join(list(text)) 
	text = text.replace("&apos;", "'")
	return text

def get_toots(client, id, since_id):
	i = 0
	toots = client.account_statuses(id, since_id = since_id)
	while toots is not None and len(toots) > 0:
		for toot in toots:
			t = parse_toot(toot)
			if t != None:
				yield {
					"content": t,
					"id": toot.id,
					"uri": toot.uri,
				}
		try:
			toots = client.fetch_next(toots)
		except TimeoutError:
			print("Operation timed out, committing to database and exiting.")
			db.commit()
			db.close()
			sys.exit(1)
		i += 1
		if i%10 == 0:
			print(i)

client = Mastodon(
	client_id=cfg['client']['id'],
	client_secret = cfg['client']['secret'], 
	access_token=cfg['secret'], 
	api_base_url=cfg['site'])

me = client.account_verify_credentials()
following = client.account_following(me.id)

db = sqlite3.connect("ebooks.db")
db.text_factory=str
c = db.cursor()
c.execute("CREATE TABLE IF NOT EXISTS `toots` (id INT NOT NULL UNIQUE PRIMARY KEY, userid INT NOT NULL, uri VARCHAR NOT NULL, content VARCHAR NOT NULL) WITHOUT ROWID")
db.commit()

def handleCtrlC(signal, frame):
	print("\nPREMATURE EVACUATION - Saving chunks")
	db.commit()
	sys.exit(1)

signal.signal(signal.SIGINT, handleCtrlC)

for f in following:
	last_toot = c.execute("SELECT id FROM `toots` WHERE userid LIKE ? ORDER BY id DESC LIMIT 1", (f.id,)).fetchone()
	if last_toot != None:
		last_toot = last_toot[0]
	else:
		last_toot = 0
	print("Harvesting toots for user @{}, starting from {}".format(f.acct, last_toot))
	# for t in get_toots(client, f.id, last_toot):
	# 	# try:
	# 	c.execute("REPLACE INTO toots (id, userid, uri, content) VALUES (?, ?, ?, ?)", (t['id'], f.id, t['uri'], t['content']))
	# 	# except:
	# 	# 	pass #ignore toots that can't be encoded properly

	#find the user's activitypub outbox
	print("WebFingering...")
	instance = re.search(r"^.*@(.+)", f.acct)
	if instance == None:
		instance = re.search(r"https?:\/\/(.*)", cfg['site']).group(1)
	else:
		instance = instance.group(1)

	# print("{} is on {}".format(f.acct, instance))
	r = requests.get("https://{}/.well-known/host-meta")
	# template="([^"]+)"

	current = None
	while True:
		sys.exit(0)



db.commit()
db.execute("VACUUM") #compact db
db.commit()
db.close()
