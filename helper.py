from datetime import datetime
import time
import numpy as np
import time
from twython import TwythonRateLimitError, TwythonError, TwythonAuthError
from dateutil.parser import parse
from dateutil.tz import tzutc
tzinfos = {"UTC": tzutc}

def queryAndInsertRelationshipsAndProfiles_Followers(twitter, c,conn, today,user_id):
	followers=[]
	cursor=-1
	while (cursor!=0):
		try:
			temp_followers=twitter.get_followers_ids(user_id=user_id,cursor=cursor)
			cursor = temp_followers['next_cursor']
			followers+=temp_followers['ids']
		
		except Exception as e:
			if(e.error_code==404 or e.error_code==401):
				cursor==0
				break;
			else:
				print("Too many requests, go sleep for a while, but will insert friends profile in meantime")
				queryAndInsertUsersProfiles(twitter, c, conn, today, followers)
				insertUserRelationship(c,conn,[(j,user_id) for j in followers],today)
				followers=[]
				rate_limit_status=twitter.get_application_rate_limit_status()
				# reset_in=rate_limit_status['resources']['followers'][ '/followers/ids']['reset'] - datetime.now().timestamp() ##Python3.5
				reset_in=rate_limit_status['resources']['followers'][ '/followers/ids']['reset'] - time.time() ##python 2.7
				time.sleep(reset_in+60)
				try:
					temp_followers=twitter.get_followers_ids(user_id=user_id,cursor=cursor)
					cursor = temp_followers['next_cursor']
					followers+=temp_followers['ids']

				except Exception as e:
					if(e.error_code==404 or e.error_code==401):
						print("Error ", e.error_code, ' passing')
						cursor==0
						break;
	
	queryAndInsertUsersProfiles(twitter, c, conn, today, followers)
	insertUserRelationship(c,conn,[(j,user_id) for j in followers],today)



def queryAndInsertRelationshipsAndProfiles_Friends(twitter,c,conn, today,user_id):
	friends=[]
	cursor=-1
	while (cursor!=0):
		try:
			temp_friends=twitter.get_friends_ids(user_id=user_id,cursor=cursor)
			cursor = temp_friends['next_cursor']
			friends+=temp_friends['ids']
		
		except Exception as e:
			if(e.error_code==404 or e.error_code==401):
				cursor==0
				break;
			else:
				print("Too many requests, go sleep for a while, but will insert friends profile in meantime")
				queryAndInsertUsersProfiles(twitter, c, conn, today, friends)
				insertUserRelationship(c,conn,[(user_id,j) for j in friends],today)
				friends=[]
				rate_limit_status=twitter.get_application_rate_limit_status()
				# reset_in=rate_limit_status['resources']['friends'][ '/friends/ids']['reset'] - datetime.now().timestamp() ##python3.5
				reset_in=rate_limit_status['resources']['friends'][ '/friends/ids']['reset'] - time.time() ##python 2.7
				time.sleep(reset_in+60)
				try:
					temp_friends=twitter.get_friends_ids(user_id=user_id,cursor=cursor)
			
					cursor = temp_friends['next_cursor']
					friends+=temp_friends['ids']
				except Exception as e:
					if(e.error_code==404 or e.error_code==401):
						print("Error ", e.error_code, ' passing')
						cursor==0
						break;
	
	queryAndInsertUsersProfiles(twitter, c, conn, today, friends)
	insertUserRelationship(c,conn,[(user_id,j) for j in friends],today)


def queryUserFriends(twitter, today,user_id):
	friends=[]
	cursor=-1
	while (cursor!=0):
		try:
			temp_friends=twitter.get_friends_ids(user_id=user_id,cursor=cursor)
			cursor = temp_friends['next_cursor']
			friends+=temp_friends['ids']
		
		except Exception as e:
			if(e.error_code==404 or e.error_code==401):
				cursor==0
				break;
			else:
				print("Too many requests, go sleep for a while")
				time.sleep(15*60+30)
				try:
					temp_friends=twitter.get_friends_ids(user_id=user_id,cursor=cursor)
			
					cursor = temp_friends['next_cursor']
					friends+=temp_friends['ids']
				except Exception as e:
					if(e.error_code==404 or e.error_code==401):
						print("Error ", e.error_code, ' passing')
						cursor==0
						break;

	return friends;

def queryUserFollowers(twitter, today,user_id):
	followers=[]
	cursor=-1
	while (cursor!=0):
		try:
			temp_followers=twitter.get_followers_ids(user_id=user_id,cursor=cursor)
			cursor = temp_followers['next_cursor']
			followers+=temp_followers['ids']
		
		except Exception as e:
			if(e.error_code==404 or e.error_code==401):
				break;
			else:
				print("Too many requests, go sleep for a while")
				time.sleep(15*60+30)
				try:
					temp_followers=twitter.get_followers_ids(user_id=user_id,cursor=cursor)
					cursor = temp_followers['next_cursor']
					followers+=temp_followers['ids']

				except Exception as e:
					if(e.error_code==404 or e.error_code==401):
						print("Error ", e.error_code, ' passing')
						break;
	
	return followers;



def queryAndInsertUsersLatestTweets(twitter, c, conn, today, target_users):
	new_tweets=[]
	for user in target_users:
		print('Now querying tweets of user ', user)
		try : 
			temp_tweets=twitter.get_user_timeline(user_id=user,count=200)
			new_tweets=new_tweets+temp_tweets

		except Exception as e:
			if(e.error_code==404 or e.error_code==401):
				pass;
			else:
				print("Too many requests, go sleep for a while")
				insertTweets(conn,c, new_tweets)
				time.sleep(15*60+30)
				new_tweets=[]
				temp_tweets=twitter.get_user_timeline(user_id=user,count=200)
				new_tweets=new_tweets+temp_tweets


		print('Done querying user ', user)
	
	insertTweets(conn,c, new_tweets)


def queryAndInsertUsersTimelines(twitter,c,conn,user_id):
	counter=0
	tweets=[]
	temp_tweets=[]
	try:
		temp_tweets=twitter.get_user_timeline(user_id=user_id,count=200)
		tweets+=temp_tweets
		
	except Exception as e:
		if(e.error_code==404 or e.error_code==401):
			pass;
		else:
			print("Too many requests, go sleep for a while, but will insert timeline collected so far in the meantime")
			counter+=len(tweets)
			insertTweets(conn,c,tweets)
			tweets=[]
			rate_limit_status=twitter.get_application_rate_limit_status()
			reset_in=rate_limit_status['resources']['statuses']['/statuses/user_timeline']['reset'] - time.time() ##python 2.7
			time.sleep(reset_in+60)
	
			try:
				temp_tweets=[]
				temp_tweets=twitter.get_user_timeline(user_id=user_id,count=200)
				tweets+=temp_tweets

			except Exception as e:
				if(e.error_code==404 or e.error_code==401):
					print("Error ", e.error_code, ' passing')
					pass;

	while (len(temp_tweets)>0):
		m_id=min([i['id'] for i in tweets])-1
		try:
			temp_tweets=[]
			temp_tweets=twitter.get_user_timeline(user_id=user_id,count=200,max_id=m_id)
			tweets+=temp_tweets
		
		except Exception as e:
			if(e.error_code==404 or e.error_code==401):
				break;
			else:
				print("Too many requests, go sleep for a while, but will insert timeline collected so far in the meantime")
				counter+=len(tweets)
				insertTweets(conn,c,tweets)
				tweets=[]
				rate_limit_status=twitter.get_application_rate_limit_status()
				reset_in=rate_limit_status['resources']['statuses']['/statuses/user_timeline']['reset'] - time.time() ##python 2.7
				time.sleep(reset_in+60)
				try:
					temp_tweets=[]
					temp_tweets=twitter.get_user_timeline(user_id=user_id,count=200,max_id=m_id)
					tweets+=temp_tweets

				except Exception as e:
					if(e.error_code==404 or e.error_code==401):
						print("Error ", e.error_code, ' passing')
						break;

	
	counter+=len(tweets)
	insertTweets(conn,c,tweets)
	return counter;


def queryUserTimeline(twitter, user_id):
	tweets=[]
	try : 
		temp_tweets=twitter.get_user_timeline(user_id=user_id,count=200)

	except TwythonRateLimitError:
		print("Too many requests, go sleep for a while")
		time.sleep(15*60+30)
		temp_tweets=twitter.get_user_timeline(user_id=user_id,count=200)
	
	tweets+=temp_tweets
	while (len(temp_tweets)>0):
		m_id=min([i['id'] for i in tweets])-1
		try:
			temp_tweets=twitter.get_user_timeline(user_id=user_id,count=200,max_id=m_id)
		
		except TwythonRateLimitError:
			print("Too many requests, go sleep for a while")
			time.sleep(15*60+30)
			temp_tweets=twitter.get_user_timeline(user_id=user_id,count=200,max_id=m_id)

		tweets+=temp_tweets
	
	return tweets;

def queryTweetsContainingHashtag(twitter, input_list_of_target_hashtags, start_date, end_date, earliestTweet, latestTweet, maxTweets=1000000):
	output_list_of_tweets = []
	max_tweets = maxTweets

	if(type(start_date)==datetime):
		sd = start_date.strftime('%Y-%m-%d')
	else:
		sd = start_date

	if(type(end_date)==datetime):
		ed = end_date.strftime('%Y-%m-%d')
	else:
		ed = end_date

	output_list_of_tweets=[]
	for h in input_list_of_target_hashtags:
		print("Querying keyword ", h)
		new=getTweetsByHashtag(twitter, h, sd, ed, earliestTweet, latestTweet, max_tweets)
		output_list_of_tweets = output_list_of_tweets + new
		ids = [i['id'] for i in output_list_of_tweets]
		print("Got ",len(new), " new tweets")
		print("Got ",len(np.unique(ids)), " unique tweets so far")

	return output_list_of_tweets


def queryAndInsertTweetsContainingHashtag(twitter, input_list_of_target_hashtags, start_date, end_date, earliestTweet, latestTweet, maxTweets, conn, c, today):
	output_list_of_tweets = []
	max_tweets = maxTweets

	if(type(start_date)==datetime):
		sd = start_date.strftime('%Y-%m-%d')
	else:
		sd = start_date

	if(type(end_date)==datetime):
		ed = end_date.strftime('%Y-%m-%d')
	else:
		ed = end_date

	output_list_of_tweets=[]
	for h in input_list_of_target_hashtags:
		print("Querying keyword ", h)
		getAndInsertTweetsByHashtag(twitter, h, sd, ed, earliestTweet, latestTweet, max_tweets, conn, c, today)

	return output_list_of_tweets

def getAndInsertTweetsByHashtag(twitter, query, start_date, end_date, earliestTweet, latestTweet, max_tweets, conn, c, today):
	tweets = []
	cursor = -1
	notBefore = earliestTweet
	keepgoing=True

	try :
		results = twitter.search(q=query, count=100, since_id = notBefore, max_id= latestTweet, result_type='recent', include_entities=True)
		if('statuses' in results and len(results['statuses'])>0):
			cursor = sorted([i['id'] for i in results['statuses']])[0]-1
			tweets += results['statuses']
		else:
			keepgoing=False;

	except TwythonRateLimitError:
		print("Too many requests, go sleep for a while")
		print("Will start insterting tweets in the meatime, got ", len(tweets), " to insert")
		insertTweets(conn,c, tweets)
		tweets = []
		time.sleep(15*60+30)
		try :
			results = twitter.search(q=query, count=100, since_id = notBefore, max_id= cursor, result_type='recent', include_entities=True)
			if('statuses' in results and len(results['statuses'])>0):
				cursor = sorted([i['id'] for i in results['statuses']])[0]-1
				tweets += results['statuses']
			else:
				keepgoing=False;
				
		except TwythonError:
			pass;

	while keepgoing:

		if(len(results['statuses'])==0):
			break;

		if(len(tweets) >= max_tweets):
			break

		if(cursor==0):
			break;

		try :
			results = twitter.search(q=query, count=100, since_id=notBefore, max_id=cursor, result_type='recent', include_entities=True)
			if('statuses' in results and len(results['statuses'])>0):
				cursor = sorted([i['id'] for i in results['statuses']])[0]-1
				tweets += results['statuses']


			else:
				print("No more results")
				break;

		except TwythonRateLimitError:
			print("Too many requests, go sleep for a while")
			print("Will start insterting tweets in the meatimee, got ", len(tweets), " to insert")
			insertTweets(conn,c, tweets)
			tweets = []			
			time.sleep(15*60+30)
			try :
				results = twitter.search(q=query, count=100, since_id=notBefore , max_id=cursor,  result_type='recent', include_entities=True)
				if('statuses' in results and len(results['statuses'])>0):
					cursor = sorted([i['id'] for i in results['statuses']])[0]-1
					tweets += results['statuses']

				else: 
					print("No more results")
					break;
			
			except TwythonError:
				break;
	print("Insterting final batch of tweets. got ", len(tweets), " to insert")
	insertTweets(conn,c, tweets)

def getAndInsertTweetsWithPicsByLocation(twitter, start_date, end_date, earliestTweet, latestTweet, max_tweets, conn, c, today):
	tweets = []
	cursor = -1
	notBefore = earliestTweet
	keepgoing=True

	try :
		results = twitter.search(q='* filter:media', count=100, geocode='39.833333,-98.583333,1600mi', since_id = notBefore, max_id= latestTweet, result_type='recent', include_entities=True)
		if('statuses' in results and len(results['statuses'])>0):
			cursor = sorted([i['id'] for i in results['statuses']])[0]-1
			tweets += results['statuses']
		else:
			keepgoing=False;

	except TwythonRateLimitError:
		print("Too many requests, go sleep for a while")
		print("Will start insterting tweets in the meatime, got ", len(tweets), " to insert")
		insertTweets(conn,c, tweets)
		tweets = []
		time.sleep(15*60+30)
		try :
			results = twitter.search(q='* filter:media', count=100, geocode='39.833333,-98.583333,1600mi', since_id = notBefore, max_id= cursor, result_type='recent', include_entities=True)
			if('statuses' in results and len(results['statuses'])>0):
				cursor = sorted([i['id'] for i in results['statuses']])[0]-1
				tweets += results['statuses']
			else:
				keepgoing=False;
				
		except TwythonError:
			pass;

	while keepgoing:

		if(len(results['statuses'])==0):
			break;

		if(len(tweets) >= max_tweets):
			break

		if(cursor==0):
			break;

		try :
			results = twitter.search(q='* filter:media', count=100, geocode='39.833333,-98.583333,1600mi', since_id=notBefore, max_id=cursor, result_type='recent', include_entities=True)
			if('statuses' in results and len(results['statuses'])>0):
				cursor = sorted([i['id'] for i in results['statuses']])[0]-1
				tweets += results['statuses']


			else:
				print("No more results")
				break;

		except TwythonRateLimitError:
			print("Too many requests, go sleep for a while")
			print("Will start insterting tweets in the meatimee, got ", len(tweets), " to insert")
			insertTweets(conn,c, tweets)
			tweets = []			
			time.sleep(15*60+30)
			try :
				results = twitter.search(q='* filter:media', count=100, geocode='39.833333,-98.583333,1600mi', since_id=notBefore , max_id=cursor,  result_type='recent', include_entities=True)
				if('statuses' in results and len(results['statuses'])>0):
					cursor = sorted([i['id'] for i in results['statuses']])[0]-1
					tweets += results['statuses']

				else: 
					print("No more results")
					break;
			
			except TwythonError:
				break;
	print("Insterting final batch of tweets. got ", len(tweets), " to insert")
	insertTweets(conn,c, tweets)






def getTweetsByHashtag(twitter, query, start_date, end_date, earliestTweet, latestTweet, max_tweets):
	tweets = []
	cursor = -1
	notBefore = earliestTweet
	keepgoing=True

	try :
		results = twitter.search(q=query, count=100, since_id = notBefore, max_id= latestTweet, result_type='recent', include_entities=True)
		if('statuses' in results and len(results['statuses'])>0):
			cursor = sorted([i['id'] for i in results['statuses']])[0]-1
			tweets += results['statuses']
		else:
			keepgoing=False;

	except TwythonRateLimitError:
		print("Too many requests, go sleep for a while")
		time.sleep(15*60+30)
		try :
			results = twitter.search(q=query, count=100, since_id = notBefore, max_id= cursor, result_type='recent', include_entities=True)
			if('statuses' in results and len(results['statuses'])>0):
				cursor = sorted([i['id'] for i in results['statuses']])[0]-1
				tweets += results['statuses']
			else:
				keepgoing=False;
				
		except TwythonError:
			pass;

	while keepgoing:

		if(len(results['statuses'])==0):
			break;

		if(len(tweets) >= max_tweets):
			break

		if(cursor==0):
			break;

		try :
			results = twitter.search(q=query, count=100, since_id=notBefore, max_id=cursor, result_type='recent', include_entities=True)
			if('statuses' in results and len(results['statuses'])>0):
				cursor = sorted([i['id'] for i in results['statuses']])[0]-1
				tweets += results['statuses']


			else:
				print("No more results")
				break;

		except TwythonRateLimitError:
			print("Too many requests, go sleep for a while")
			
			time.sleep(15*60+30)
			try :
				results = twitter.search(q=query, count=100, since_id=notBefore , max_id=cursor,  result_type='recent', include_entities=True)
				if('statuses' in results and len(results['statuses'])>0):
					cursor = sorted([i['id'] for i in results['statuses']])[0]-1
					tweets += results['statuses']

				else: 
					print("No more results")
					break;
			
			except TwythonError:
				break;


	return tweets


def queryUsersProfiles(twitter, input_list_users_ids):
	
	unique_ids = np.unique(input_list_users_ids)
	count=0
	users= [int(i) for i in unique_ids]
	number_batch = int(len(users)/100)
	last_batch_size = len(users)%100
	profiles=[]

	for i in range(0,number_batch+1):
		print("Querying batch n ", i, " on ", number_batch)
		try :
			results = twitter.lookup_user(user_id=users[i*100:(i+1)*100])
			profiles += results
		

		except Exception as e:
			if(e.error_code==404):
				pass;
			else:
				print("Too many requests, go sleep for a while")
				time.sleep(15*60)
				try: 
					results = twitter.lookup_user(user_id=users[i*100:(i+1)*100])
					profiles += results
				except :
					pass;


	return profiles;


def queryAndInsertUsersProfilesForTrack(twitter, c, conn, today, input_list_users_ids):
	
	new_users = []

	unique_ids = np.unique(input_list_users_ids)
	users= [int(i) for i in unique_ids]
	number_batch = int(len(users)/100)
	last_batch_size = len(users)%100
	profiles=[]
	new=[]
	for i in range(0,number_batch+1):
		print("Querying batch n ", i, " on ", number_batch)
		try :
			results = twitter.lookup_user(user_id=users[i*100:(i+1)*100])
			profiles += results
			new += results

		except Exception as e:
			if(e.error_code==404):
				pass;
			else:
				print("Too many requests, go sleep for a while")
				insertUserTrack(c,conn,new,today)
				new=[]
				time.sleep(15*60+30)
				try :
					results = twitter.lookup_user(user_id=users[i*100:(i+1)*100])
					profiles += results
					new+=results
			
				except TwythonError:
					pass;

	insertUserTrack(c,conn,new,today)

def queryAndInsertUsersProfiles(twitter, c, conn, today, input_list_users_ids):
	
	new_users = []

	unique_ids = np.unique(input_list_users_ids)
	users= [int(i) for i in unique_ids]
	number_batch = int(len(users)/100)
	last_batch_size = len(users)%100
	profiles=[]
	new=[]
	for i in range(0,number_batch+1):
		print("Querying batch n ", i, " on ", number_batch)
		try :
			results = twitter.lookup_user(user_id=users[i*100:(i+1)*100])
			profiles += results
			new += results

		except Exception as e:
			if(e.error_code==404):
				pass;
			else:
				print("Too many requests, go sleep for a while")
				insertUserProfiles(c,conn,new,today,today)
				new=[]
				time.sleep(15*60+30)
				try :
					results = twitter.lookup_user(user_id=users[i*100:(i+1)*100])
					profiles += results
					new+=results
			
				except TwythonError:
					pass;

	insertUserProfiles(c,conn,new,today,today)

def queryUsersProfilesThatPostedTheTweets(twitter, input_list_of_queried_tweets):
	
	new_users = []

	ids_of_users_that_posted_tweets = [tweet['user']['id_str'] for tweet in input_list_of_queried_tweets]
	unique_ids = np.unique(ids_of_users_that_posted_tweets)

	for user in unique_ids : 
		try: 
			new_user = twitter.show_user(user_id=user)
		except : 
			print("already got " +str(len(new_users)) + " but going to sleep")
			time.sleep(15*60+30)
			try: 
				new_user = twitter.show_user(user_id=user)
			except :
				continue;
		new_users.append(new_user)

	return new_users;

def queryAndInsertUsersProfilesThatPostedTheTweets(twitter, c, conn, today, input_list_of_queried_tweets):
	
	new_users = []

	ids_of_users_that_posted_tweets = [tweet['user']['id_str'] for tweet in input_list_of_queried_tweets]
	unique_ids = np.unique(ids_of_users_that_posted_tweets)
	users= [int(i) for i in unique_ids]
	number_batch = int(len(users)/100)
	last_batch_size = len(users)%100
	profiles=[]
	new=[]
	for i in range(0,number_batch+1):
		print("Querying batch n ", i, " on ", number_batch)
		try :
			results = twitter.lookup_user(user_id=users[i*100:(i+1)*100])
			profiles += results
			new += results

		except Exception as e:
			if(e.error_code==404):
				pass;
			else:
				print("Too many requests, go sleep for a while")
				insertUserProfiles(c,conn,new,today,today)
				new=[]
				time.sleep(15*60+30)
				try :
					results = twitter.lookup_user(user_id=users[i*100:(i+1)*100])
					profiles += results
					new+=results
			
				except TwythonError:
					pass;

	insertUserProfiles(c,conn,new,today,today)



################################################# INSERT IN SQLITE DB  #################################################

######### NOTE : this n=20...

def insertTweets(conn,c, tweets): #put the tweet in the tweet table, update the tweet media, tweet hashtag, tweet url
	#First make string of values to insert.
	try :
		ca=[datetime.strptime(i['created_at'].replace('+0000','UTC'),'%a %b %d %H:%M:%S %Z %Y') for i in tweets]
	except ValueError:
		try :
			ca=[datetime.strptime(i['created_at'].replace('+0000','UTC')[4:],'%b %d %H:%M:%S %Z %Y') for i in tweets]
		except ValueError:
			ca=[parse(i['created_at'].replace('+0000','UTC')) for i in tweets]
	created_at=ca
	t=tweets
	count = 0
	n=50
	while(len(t)>0):
		count +=1 
		tweets=t[0:n]
		created_at=ca[0:n]
		tweetstring=""
		htstring=""
		umstring=""
		urlstring=""
		vals=""
		t=t[n:max(n,len(t))]
		ca=ca[n:max(n,len(ca))]
		for i in range(len(tweets)):
			tweet=tweets[i]
			tweetstring+='('
			tweetstring+= tweet['id_str']+','
			if 'user' in tweet.keys():
				# tweetstring+= str(tweet['user']['id'])+","
				tweetstring+=tweet['user']['id_str']+","
				tweetstring+= "'"+tweet['user']['screen_name']+"',"
			else:
				tweetstring+='NULL,NULL,'
			tweetstring+= "'"+created_at[i].strftime("%Y-%m-%d %H:%M:%S")+"',"
			tweetstring+= "'"+totranslate(tweet['text'])[0:180]+" ',"
			if tweet['geo'] is None:
				tweetstring+='NULL,NULL,'
			else:
				tweetstring+=str(tweet['geo']['coordinates'][0])+','+str(tweet['geo']['coordinates'][1])+','
			if tweet['place'] is None:
				tweetstring+='NULL,NULL,'
			else:
				tweetstring+= "'"+tweet['place']['place_type']+"',"
				tweetstring+= "'"+totranslate(tweet['place']['name'])[0:40]+" ',"
			tweetstring+= "'"+str(tweet['lang'])[0:3]+"',"
			tweetstring+="'"+tweet['source'].replace("'","''")[0:109]+" ',"
			if 'retweet_count' in tweet.keys():
				tweetstring+= str(tweet['retweet_count'])+","
			else:
				tweetstring+= "NULL,"
			if 'favorite_count' in tweet.keys():
				tweetstring+= str(tweet['favorite_count'])+","
			else:
				tweetstring+= "NULL,"
			if 'retweeted_status' in tweet.keys():
				tweetstring+=str(tweet['retweeted_status']['id_str'])+','
			else:
				tweetstring+='NULL,'
			if tweet['in_reply_to_status_id'] is None:
				tweetstring+='NULL,NULL,NULL'
			else:
				tweetstring+=str(tweet['in_reply_to_status_id'])+','+str(tweet['in_reply_to_user_id'])+",'"+tweet['in_reply_to_screen_name']+"'"
			if i==len(tweets)-1:
				tweetstring+=')'
			else:
				tweetstring+= '),\n'
			for j in tweet['entities']['hashtags']:
				if htstring=="":
					htstring+='('
				else:
					htstring+=',\n('
				htstring+=str(tweet['id_str'])+','
				htstring+="'"+j['text'][0:180]+"')"
			for j in tweet['entities']['urls']:
				if urlstring=="":
					urlstring+='('
				else:
					urlstring+=',\n('
				urlstring+=str(tweet['id_str'])+','
				urlstring+="'"+j['url'].replace("'","''")+"',"
				if 'expanded_url' in j.keys():
					urlstring+="'"+j['expanded_url'].replace("'","''")+"')"
				else:
					urlstring+="NULL)"                                
			for j in tweet['entities']['user_mentions']:
				if umstring=="":
					umstring+='('
				else:
					umstring+=',\n('
				umstring+=str(tweet['id_str'])+','
				if j['id_str'] is None:
					umstring+='NULL'+","	
				else:
					umstring+=str(j['id_str'])+","

				umstring+="'"+j['screen_name']+"',"
				if j['name'] is None:
					umstring+=	"NULL)"
				else:

					umstring+="'"+totranslate(j['name'])[0:40]+" ')"

			if 'media' in tweet['entities'].keys():
				if 'extended_entities' in tweet.keys():
					txt='extended_entities'
				else:
					txt='entities'
				for k in range(len(tweet[txt]['media'])):
					if vals=="":
						vals+='('
					else:
						vals+=',\n('
					j=tweet[txt]['media'][k]
					vals+=str(tweet['id_str'])+","
					vals+="NULL,"
					vals+=str(j['id_str'])+','
					if 'source_status_id' in j.keys():
						vals+=str(j['source_user_id'])+","
						vals+=str(j['source_status_id'])+","
					else:
						vals+="NULL,NULL,"
					vals+="NULL,"
					vals+="'"+j['url']+"',"
					vals+="'"+j['media_url'][0:79]+" ',"
					vals+="'"+j['display_url']+"')"
		if tweetstring !="":
			c.execute('INSERT OR IGNORE INTO tweet (tweet_id,'
					+'user_id,'
					+'screen_name,'
					+'created_at,'
					+'text,'
					+'geo_lat,'
					+'geo_long,'
					+'place_type,'
					+'place_name,'
					+'lang,'
					+'source,'
					+'retweet_count,'
					+'favorite_count,'
					+'retweet_status_id,'
					+'reply_to_status_id,'
					+'reply_to_user_id,' 
					+'reply_to_screen_name'#No comma here!
					+')\n'
					+'VALUES\n'
					+tweetstring
					+';')
		if htstring !="":
			c.execute('INSERT OR IGNORE INTO tweet_hashtags (tweet_id,'
					+'hashtag'
					+')\n'
					+'VALUES\n'
					+htstring
					+';')
		if umstring !="":
			c.execute('INSERT OR IGNORE INTO tweet_usermentions (tweet_id,'
					+'user_mention_id,'
					+'user_mention_screen_name,'
					+'user_mention_name'
					+')\n'
					+'VALUES\n'
					+umstring
					+';')
		if urlstring !="":
			c.execute('INSERT OR IGNORE INTO tweet_url (tweet_id,'
					+'url,'
					+'expanded_url'
					+')\n'
					+'VALUES\n'
					+urlstring
					+';')
		if vals !="":
			c.execute('INSERT OR IGNORE INTO tweet_media (tweet_id,'
					+'pic_hash,'
					+'pic_id,'
					+'pic_source_user_id,'
					+'pic_source_status_id,'
					+'pic_filename,'
					+'url,'
					+'media_url,'
					+'display_url'
					+')\n'
					+'VALUES\n'
					+vals
					+';')
		conn.commit()

def insertTweetsHydrated(conn,c, tweets): #put the tweet in the tweet table, update the tweet media, tweet hashtag, tweet url
	#First make string of values to insert.
	ca=[datetime.strptime(i['created_at'].replace('+0000','UTC'),'%a %b %d %H:%M:%S %Z %Y') for i in tweets]
	created_at=ca
	t=tweets
	count = 0
	n=100
	while(len(t)>0):
		count +=1 
		# print("at batch ", count)
		tweets=t[0:n]
		created_at=ca[0:n]
		tweetstring=""
		htstring=""
		umstring=""
		urlstring=""
		vals=""
		t=t[n:max(n,len(t))]
		ca=ca[n:max(n,len(ca))]
		for i in range(len(tweets)):
			tweet=tweets[i]
			tweetstring+='('
			tweetstring+= str(tweet['id_str'])+','
			if 'user' in tweet.keys():
				tweetstring+= tweet['user']['id_str']+","
				tweetstring+= "'"+tweet['user']['screen_name']+"',"
			else:
				tweetstring+='NULL,NULL,'
			tweetstring+= "'"+created_at[i].strftime("%Y-%m-%d %H:%M:%S")+"',"
			tweetstring+= "'"+totranslate(tweet['text'])[0:180]+" ',"
			if tweet['geo'] is None:
				tweetstring+='NULL,NULL,'
			else:
				tweetstring+=str(tweet['geo']['coordinates'][0])+','+str(tweet['geo']['coordinates'][1])+','
			if tweet['place'] is None:
				tweetstring+='NULL,NULL,'
			else:
				tweetstring+= "'"+tweet['place']['place_type']+"',"
				tweetstring+= "'"+totranslate(tweet['place']['name'])[0:40]+" ',"
			tweetstring+= "'"+str(tweet['lang'])[0:3]+"',"
			tweetstring+="'"+tweet['source'].replace("'","''")[0:109]+" ',"
			if 'retweet_count' in tweet.keys():
				tweetstring+= str(tweet['retweet_count'])+","
			else:
				tweetstring+= "NULL,"
			if 'favorite_count' in tweet.keys():
				tweetstring+= str(tweet['favorite_count'])+","
			else:
				tweetstring+= "NULL,"
			if 'retweeted_status' in tweet.keys():
				tweetstring+=str(tweet['retweeted_status']['id_str'])+','
			else:
				tweetstring+='NULL,'
			if tweet['in_reply_to_status_id'] is None:
				tweetstring+='NULL,NULL,NULL'
			else:
				tweetstring+=str(tweet['in_reply_to_status_id'])+','+str(tweet['in_reply_to_user_id'])+",'"+tweet['in_reply_to_screen_name']+"'"
			if i==len(tweets)-1:
				tweetstring+=')'
			else:
				tweetstring+= '),\n'
			for j in tweet['entities']['hashtags']:
				if htstring=="":
					htstring+='('
				else:
					htstring+=',\n('
				htstring+=str(tweet['id'])+','
				htstring+="'"+j['text'][0:180]+"')"
			for j in tweet['entities']['urls']:
				if urlstring=="":
					urlstring+='('
				else:
					urlstring+=',\n('
				urlstring+=str(tweet['id_str'])+','
				urlstring+="'"+j['url'].replace("'","''")+"',"
				if 'expanded_url' in j.keys():
					urlstring+="'"+j['expanded_url'].replace("'","''")+"')"
				else:
					urlstring+="NULL)"                                
			for j in tweet['entities']['user_mentions']:
				if umstring=="":
					umstring+='('
				else:
					umstring+=',\n('
				umstring+=str(tweet['id_str'])+','
				umstring+=str(j['id_str'])+","
				umstring+="'"+j['screen_name']+"',"
				umstring+="'"+totranslate(j['name'])[0:40]+" ')"
			if 'media' in tweet['entities'].keys():
				if 'extended_entities' in tweet.keys():
					txt='extended_entities'
				else:
					txt='entities'
				for k in range(len(tweet[txt]['media'])):
					if vals=="":
						vals+='('
					else:
						vals+=',\n('
					j=tweet[txt]['media'][k]
					vals+=str(tweet['id_str'])+","
					vals+="NULL,"
					vals+=str(j['id_str'])+','
					if 'source_status_id' in j.keys():
						vals+=str(j['source_user_id'])+","
						vals+=str(j['source_status_id'])+","
					else:
						vals+="NULL,NULL,"
					vals+="NULL,"
					vals+="'"+j['url']+"',"
					vals+="'"+j['media_url'][0:79]+" ',"
					vals+="'"+j['display_url']+"')"
		if tweetstring !="":
			c.execute('INSERT OR IGNORE INTO tweet (tweet_id,'
					+'user_id,'
					+'screen_name,'
					+'created_at,'
					+'text,'
					+'geo_lat,'
					+'geo_long,'
					+'place_type,'
					+'place_name,'
					+'lang,'
					+'source,'
					+'retweet_count,'
					+'favorite_count,'
					+'retweet_status_id,'
					+'reply_to_status_id,'
					+'reply_to_user_id,' 
					+'reply_to_screen_name'#No comma here!
					+')\n'
					+'VALUES\n'
					+tweetstring
					+';')
		if htstring !="":
			c.execute('INSERT OR IGNORE INTO tweet_hashtags (tweet_id,'
					+'hashtag'
					+')\n'
					+'VALUES\n'
					+htstring
					+';')
		if umstring !="":
			c.execute('INSERT OR IGNORE INTO tweet_usermentions (tweet_id,'
					+'user_mention_id,'
					+'user_mention_screen_name,'
					+'user_mention_name'
					+')\n'
					+'VALUES\n'
					+umstring
					+';')
		if urlstring !="":
			c.execute('INSERT OR IGNORE INTO tweet_url (tweet_id,'
					+'url,'
					+'expanded_url'
					+')\n'
					+'VALUES\n'
					+urlstring
					+';')
		if vals !="":
			c.execute('INSERT OR IGNORE INTO tweet_media (tweet_id,'
					+'pic_hash,'
					+'pic_id,'
					+'pic_source_user_id,'
					+'pic_source_status_id,'
					+'pic_filename,'
					+'url,'
					+'media_url,'
					+'display_url'
					+')\n'
					+'VALUES\n'
					+vals
					+';')
		conn.commit()


def insertUserRelationship(c,conn,data,obtained_date): #Insert a collection of users accessed on a certain date.
	u=data
	n=100
	while(len(u)>0):
		data=u[0:n]
		u=u[n:max(n,len(u))]
		relationshipstring=""
		for i in range(len(data)):
				pair=data[i]
				relationshipstring+='('
				relationshipstring+= str(pair[0])+','
				relationshipstring+= str(pair[1])+','
				relationshipstring+= "'"+obtained_date.strftime("%Y-%m-%d %H:%M:%S") +"'" 
				if i==len(data)-1:
					relationshipstring+=')'
				else:
					relationshipstring+= '),\n'
		if relationshipstring !="":
			c.execute('INSERT INTO relationships (follower_id,'
					+'friend_id,'
					+'date'
					+')\n'
					+'VALUES\n'
					+relationshipstring
					+'\n'
					+';')
		conn.commit()
	return None;


def insertUserTrack(c,conn,data,obtained_date): #Insert a collection of users accessed on a certain date.
	u=data
	n=100
	while(len(u)>0):
		data=u[0:n]
		u=u[n:max(n,len(u))]
		profilestring=""
		for i in range(len(data)):
				user=data[i]
				profilestring+='('
				profilestring+= str(user['id_str'])+','
				profilestring+= "'"+obtained_date.strftime("%Y-%m-%d %H:%M:%S") +"'," 
				profilestring+= str(user['friends_count'])+','
				profilestring+= str(user['followers_count'])+','
				profilestring+= str(user['statuses_count'])
				if i==len(data)-1:
					profilestring+=')'
				else:
					profilestring+= '),\n'
		if profilestring !="":
			print(profilestring)
			c.execute('INSERT INTO tracking (user_id,'
					+'date,'
					+'friends_count,'
					+'followers_count,'
					+'statuses_count'
					+')\n'
					+'VALUES\n'
					+profilestring
					+'\n'
					+';')
		conn.commit()
	return None;


def insertUserProfiles(c,conn,users,obtained_date,access_date): #Insert a collection of users accessed on a certain date.
	#First make string of values to insert.
	ca=[datetime.strptime(i['created_at'].replace('+0000','UTC'),'%a %b %d %H:%M:%S %Z %Y') for i in users]
	u=users
	n=100
	while(len(u)>0):
		users=u[0:n]
		u=u[n:max(n,len(u))]
		created_at=ca[0:n]
		ca=ca[n:max(n,len(ca))]
		profilestring=""
		for i in range(len(users)):
				user=users[i]
				profilestring+='('
				profilestring+= str(user['id_str'])+','
				profilestring+= "'"+str(user['screen_name'])+"',"
				profilestring+= "'"+totranslate(user['name'])[0:40]+" ',"
				profilestring+= "'"+created_at[i].strftime("%Y-%m-%d %H:%M:%S")+"',"
				profilestring+= "'"+totranslate(user['description'])[0:200]+" ',"
				if 'status' in user.keys():
					profilestring+= str(user['status']['id_str'])+","
				else:
					profilestring+='NULL,'
				profilestring+= "'"+str(user['geo_enabled'])+"',"
				profilestring+= "'"+str(user['protected'])+"',"
				profilestring+= str(user['friends_count'])+','
				profilestring+= str(user['followers_count'])+','
				profilestring+= str(user['favourites_count'])+','
				profilestring+= str(user['statuses_count'])+','
				if user['lang'] is None:
					profilestring+= 'NULL,'
				else:
					profilestring+= "'"+str(user['lang'])[0:3]+"',"
				if user['location'] is None:
					profilestring+= 'NULL,'
				else:
					profilestring+= "'"+totranslate(user['location'])[0:75]+" ',"
				profilestring+= "'"+str(user['verified'])+"',"
				if user['url'] is None:
					profilestring += 'NULL,'
				else:
					if user['entities']['url']['urls'][0]['expanded_url'] is None:
						profilestring+="'"+str(user['entities']['url']['urls'][0]['url'].replace("'","''"))+"',"
					else:
						try:
							profilestring+= "'"+str(user['entities']['url']['urls'][0]['expanded_url'].replace("'","''"))+"',"
						except : 
							profilestring+="'"+str(user['entities']['url']['urls'][0]['url'].replace("'","''"))+"',"

				profilestring+= "'"+str(user['default_profile_image'])+"',"
				if user['time_zone'] is None:
					profilestring+='NULL,NULL,'
				else:
					profilestring+= "'"+totranslate(user['time_zone'])+"',"
					profilestring+= str(user['utc_offset'])+','
				profilestring+="NULL,NULL,NULL,NULL,"
				profilestring+= "'"+obtained_date.strftime("%Y-%m-%d %H:%M:%S") +"',"
				profilestring+= "'"+access_date.strftime("%Y-%m-%d %H:%M:%S") +"',"
				profilestring+= "'True'"#No comma here
				if i==len(users)-1:
					profilestring+=')'
				else:
					profilestring+= '),\n'
		if profilestring !="":
			c.execute('INSERT OR IGNORE INTO user_profile (user_id,'
					+'screen_name,'
					+'name,'
					+'created_at,'
					+'description,'
					+'status_id,'
					+'geo_enabled,'
					+'protected,'
					+'friends_count,'
					+'followers_count,'
					+'favourites_count,'
					+'statuses_count,'
					+'lang,'
					+'location,'
					+'verified,'
					+'profile_url,'
					+'default_image,'
					+'time_zone,'
					+'UTC_offset,'
					+'profile_pic_hash,'
					+'profile_pic_filename,'
					+'profile_banner_hash,'
					+'profile_banner_filename,'
					+'obtained,'
					+'last_accessed,'
					+'active'
					+')\n'
					+'VALUES\n'
					+profilestring
					+'\n'
					+';')
		conn.commit()
	return None;

def totranslate(string):
	tempstr=string.replace("'","^").encode('unicode-escape').decode('utf-8', 'ignore')
	return(tempstr)

def create_tables(c,conn):
	c.execute("CREATE TABLE IF NOT EXISTS user "
		+ "("
		+ "user_id BIGINT PRIMARY KEY,"
		+ "friends_count INT,"
		+ "followers_count INT,"
		+ "protected BOOL,"
		+ "verified BOOL,"
		+ "geo_enabled BOOL,"
		+ "statuses_count INT,"
		+ "tweet_rate FLOAT);")
	conn.commit()
	return(None)



def create_tables_track(c,conn):
	c.execute("CREATE TABLE IF NOT EXISTS tracking"
		+ "("
		+ "user_id BIGINT,"
		+ "date datetime,"
		+ "friends_count INT,"
		+ "followers_count INT,"
		+ "statuses_count INT);")
	conn.commit()
	return(None)

def create_relationship_table(c,conn):
	c.execute("CREATE TABLE IF NOT EXISTS relationships"
		+ "("
		+ "follower_id BIGINT,"
		+ "friend_id BIGINT,"
		+ "date datetime);")
	conn.commit()
	return(None)


def create_tweet_tables(c,conn):
	c.execute('CREATE TABLE IF NOT EXISTS user_profile (user_id BIGINT,' #user table needs some updates, to include current status id (should also be inserted into tweets)
			+'screen_name VARCHAR(40),'
			+'name VARCHAR(40),'
			+'created_at DATETIME,'
			+'description VARCHAR(200),'
			+'status_id BIGINT,'
			+'geo_enabled VARCHAR(5),'
			+'protected VARCHAR(5),'
			+'friends_count INT,'
			+'followers_count INT,'
			+'favourites_count INT,'
			+'statuses_count INT,'
			+'lang VARCHAR(3),'
			+'location VARCHAR(75),'
			+'verified VARCHAR(5),'
			+'profile_url VARCHAR(200),'
			+'default_image VARCHAR(5),'
			+'time_zone VARCHAR(45),'
			+'UTC_offset INT,'
			+'profile_pic_hash CHAR(16),'
			+'profile_pic_filename VARCHAR(40),'
			+'profile_banner_hash CHAR(16),'
			+'profile_banner_filename VARCHAR(40),'
			+'obtained DATE,'
			+'last_accessed DATE,'
			+'active VARCHAR(5),'
			+'PRIMARY KEY (user_id,screen_name)'
			+');')
	c.execute('CREATE TABLE IF NOT EXISTS tweet (tweet_id BIGINT PRIMARY KEY,'
			+'user_id BIGINT,'
			+'screen_name VARCHAR(40),'
			+'created_at DATETIME,'
			+'text VARCHAR(180),'
			+'geo_lat FLOAT,'
			+'geo_long FLOAT,'
			+'place_type VARCHAR(20),'
			+'place_name VARCHAR(40),'
			+'lang VARCHAR(3),'
			+'source VARCHAR(110),'
			+'retweet_count INT,'
			+'favorite_count INT,'
			+'retweet_status_id BIGINT,'
			+'reply_to_status_id BIGINT,'
			+'reply_to_user_id BIGINT,'
			+'reply_to_screen_name VARCHAR(40),'
			+'FOREIGN KEY (user_id,screen_name) REFERENCES user_profile (user_id,screen_name),'
			+'FOREIGN KEY (reply_to_user_id,reply_to_screen_name) REFERENCES user_profile (user_id,screen_name),'
			+'FOREIGN KEY (reply_to_status_id) REFERENCES tweet (tweet_id));')
	c.execute('CREATE TABLE IF NOT EXISTS tweet_media (tweet_id BIGINT,'
			+'pic_hash CHAR(16),'
			+'pic_id BIGINT,'
			+'pic_source_user_id BIGINT,'
			+'pic_source_status_id BIGINT,'
			+'pic_filename VARCHAR(70),'
			+'url VARCHAR(80),'
			+'media_url VARCHAR(80),'
			+'display_url VARCHAR(80),'
			+'FOREIGN KEY (tweet_id) REFERENCES tweet (tweet_id),'
			+'PRIMARY KEY (tweet_id,pic_id)'
			+');')
	c.execute('CREATE TABLE IF NOT EXISTS tweet_hashtags (tweet_id BIGINT,'
			+'hashtag VARCHAR(50),'
			+'FOREIGN KEY (tweet_id) REFERENCES tweet (tweet_id),'
			+'PRIMARY KEY (tweet_id,hashtag)'
			+');')
	c.execute('CREATE TABLE IF NOT EXISTS tweet_usermentions (tweet_id BIGINT,'
			+'user_mention_id BIGINT,'
			+'user_mention_screen_name VARCHAR(40),'
			+'user_mention_name VARCHAR(40),'
			+'FOREIGN KEY (tweet_id) REFERENCES tweet (tweet_id),'
			+'PRIMARY KEY (tweet_id,user_mention_id)'
			+');')
	c.execute('CREATE TABLE IF NOT EXISTS tweet_url (tweet_id BIGINT,'
			+'url VARCHAR(100),'
			+'expanded_url VARCHAR(200),'
			+'FOREIGN KEY (tweet_id) REFERENCES tweet (tweet_id),'
			+'PRIMARY KEY (tweet_id,url)'
			+');')
	conn.commit()
	return None;



