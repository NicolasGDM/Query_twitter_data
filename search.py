# -*- coding: UTF-8 -*-
from twython import Twython
from datetime import datetime, timedelta
import numpy as np
from helper import *
import sqlite3
from operator import itemgetter
import sys 
import os

credentials=sys.argv[1]
mode = sys.argv[2]
db=sys.argv[3]
target = sys.argv[4:]

if not os.path.exists(db):
    os.makedirs('./'+db)

conn = sqlite3.connect('./'+db+'/'+db+'.db')
c = conn.cursor()


############################################################
####################### Your credentials ###################
############################################################
with open(credentials) as f:
    lines = f.read().splitlines()
twitter = Twython(*lines)



#####################################################################################
####################### Will create sqlite tables the first time  ###################
#####################################################################################
create_tables(c,conn)
create_tweet_tables(c,conn)





#################################################################
####################### Pick start/end dates ###################
################################################################

####### NOTE : if you want you can query the DB for the most recent date, or most recent tweet id, in order not to search again for previous tweets.
####### That is useful if you want to Crontab the queries on engaging for like a week. I did that once, if you're unfamiliar with sqlite queries from python ask me =)

today=datetime.now()
today=datetime(today.year,today.month,today.day,0,0,0)
start_date = datetime(2018,9,1,0,0,0) # or you can pick start_date = today
end_date = today + timedelta(2,0) # or you can pick another end_date 
earliestTweet=0 # or you can pick latest tweet from previous query
latestTweet=-1



#####################################
########## Query a hashtag ##########
#####################################
if(mode == 'hashtags'):
	input_list_of_target_hashtags = target 
	new_tweets = queryTweetsContainingHashtag(twitter, input_list_of_target_hashtags, start_date, end_date, earliestTweet, latestTweet, maxTweets=1000000)
	print('Done querying tweets')
	print('Got at most', len(np.unique([i['id'] for i in new_tweets])), ' new tweets')
	print('Start inserting timelines in database')
	insertTweets(conn,c, new_tweets)
	
	##optional : query user profiles too... takes time
	# print('Now querying profiles of people that posted the tweets')
	# queryAndInsertUsersProfilesThatPostedTheTweets(twitter, c, conn today, new_tweets)
	
	##few line below do the same but should be slower
	# new_users = queryUsersProfilesThatPostedTheTweets(twitter, new_tweets)
	# print('Done querying profiles')
	# print('Got at most', len(np.unique([i['id'] for i in new_users])), ' new users')
	# print('Start inserting user profiles in database')
	# insertUserProfiles(c,conn,new_users,today,today)


#########################################
######## Query a user_timeline ##########
#########################################

elif(mode == 'users'):
	new_tweets = []
	target_users = [int(i) for i in target]
	print('Start querying timelines')
	for user in target_users:
		print('Now querying tweets of user ', user)
		new_tweets = new_tweets + queryUserTimeline(twitter,user)
		print('Got ', len(np.unique([i['id'] for i in new_tweets])), ' new tweets from user')
		print('Done querying user ', user)
	
	print('Done querying timelines')
	print('Start inserting timelines in database')
	insertTweets(conn,c, new_tweets)

	print('Now querying profiles of people')
	queryAndInsertUsersProfiles(twitter, c, conn, today, target_users)

	##few line below do the same but should be slower
	# new_users = queryUsersProfiles(twitter, target_users)
	# print('Start inserting user profiles in database')
	# insertUserProfiles(c,conn,new_users,today,today)




