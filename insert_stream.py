import sqlite3
import sys
import json
import os
from os import rename
import time
from helper import *


db=sys.argv[1]


if not os.path.exists(db):
    os.makedirs('./'+db)


rename('./'+db+'/stream_'+db+'.json', './'+db+'/ready_to_insert.json')

print('File renamed, sleeping one minute to allow for streamer to switch')
print("\n")
##sleep for the time the streamer switches to a new json file
time.sleep(60)

print('Ready to insert database')
print("\n")
conn = sqlite3.connect('./'+db+'/'+db+'.db')
c = conn.cursor()

print('Creating tables if not exist')
print("\n")

create_tables(c,conn)
create_tweet_tables(c,conn)

print('Inserting tweet objects')
print("\n")
tweets = []
jsonfile = open('./'+db+'/ready_to_insert.json', 'r').read().split('\n')

for f in jsonfile[1:-1]:
	file = open('./'+db+'/temp.json', 'w')
	file.write(f)
	file.close()
	file = open('./'+db+'/temp.json', 'r')
	tweet=json.load(file, strict=False)
	tweets.append(tweet)

##get rid of non tweets
tweets=[i for i in tweets if 'created_at' in i]


insertTweets(conn,c, tweets)



