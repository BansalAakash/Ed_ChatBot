# Ed_ChatBot
AI based ChatBot(Android app with python backend and node-firebase connectivity) - Minor Project

###The backend uses libraries like NLTK and textblob to tokenize and lametize text. Then after analyzing text through a series of algorithms,the bot generates the output dersied for the user. If the output is an INTENT or a MESSAGE, then pushes the result on to firebase which then pushes the result to android app.

## The "firebase2.js" file is responsible for the connectivity with firebase and "mettle.py" file with the help of a "pythonclient.py" script.

###"mettle.py" is the server code processing all the data and performing all the textual operations, and then writing the data back to firebase database.

###The job of "pythonclient.py" is to take the message from "firebase2.js" which in turn is notified by firebase and  to hand over the code to "mettle.py" i.e. server.
