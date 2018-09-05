# Query Twitter Data

You can retrieve twitter data via 2 APIs:


1) The stream API
- only for upcoming tweets
- easy of use
- requires Tweepy

2) The search API
- both for past and upcoming tweets
- requires running it every X hours/days to refresh upcoming tweets
- requires Twython

Whatever the API used, data will then be inserted in a sqlite format.

For 1) you will have to schedule the inserting script insert_stream.py
For 2) the insert is done at the end of each query, but you need to schedule the queries if you want upcoming tweets.



