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

![alt text](https://github.com/NicolasGDM/Query_twitter_data/blob/master/miscellaneous/create_dir.png)

(for eg the same name as the hashtag you are querying). Warning : DO NOT go in that new folder. At all times make sure where you are by typing pwd, you should be in the parent folder of the one just created.

- Type the following command : 

![alt text](https://github.com/NicolasGDM/Query_twitter_data/blob/master/miscellaneous/stream_command_line.png)

In more details:

    * python is the name of the program that will run the script you put after (can be python3, python2... usually python works by default if you have only one python version installed)
    * stream.py (first argument) is the name of the file you want to run
    * -d folder_name (second argument) is the name of the folder you just created and want to store data in (json files)
    * -q target_hashtag (third argument) is the name of the hashtag you want to stream
    
- Do not close laptop. On MAC you can do Ctrl+Shift+Power Button to put screen off but keep process going.


This process will create a .json file stream_hashtagName.json. When this file starts to be too big, you can run the insert_json.py file to insert it into database. The steaming will continue in a new file.



######## 2) Searching - search.py 
- Open a terminal, go to working folder (the one where the script is)
- Type the following command : 
  
![alt text](https://github.com/NicolasGDM/Query_twitter_data/blob/master/miscellaneous/search_command_line.png)

In more details:

    * python is the name of the program that will run the script you put after (can be python3, python2... usually python works by default if you have only one python version installed)
    * search.py (first argument) is the name of the file you want to run
    * credentials.py (second argument) is the name of the file in which you put your credentials
    * hashtags (third argument) is the mode (either hashtags to query tweets that contains hashtags, or users to query tweets used by a set of users)
    * database_name  (fourth arugment) is the name you picked for the folder (same as database)
    * target_hashtag is the hasthag you want to query
    
  This will create a folder of the same name as the database, create a database, query the data, and insert it into the database.
  
 If you want to query multiple hashtags with the same credentials file, run :
 
![alt text](https://github.com/NicolasGDM/Query_twitter_data/blob/master/miscellaneous/search_command_line_more_than_one_hash.png)
