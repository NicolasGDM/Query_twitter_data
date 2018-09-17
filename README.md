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



############################## HOW TO RUN THE SCRIPTS ? ##############################

######## 1) Streaming - stream.py 
- Open a terminal, go to working folder (the one where the script is)
- Type command :
mkdir the/directory/you/want/the/json/files/to/be/stored 

(for eg the same name as the hashtag you are querying)

- Type the following command : 
python stream.py -d the/directory/you/want/the/json/files/to/be/stored  -q hashtag

- Do not close laptop. On MAC you can do Ctrl+Shift+Power Button to put screen off but keep process going.


This process will create a .json file stream_hashtagName.json. When this file starts to be too big, you can run the insert_json.py file to insert it into database. The steaming will continue in a new file.




