#!/usr/bin/python

'''
This code collects Twitter data using the Twitter Streaming API. The data is
printed to stdout and can be saved locally with ./get_tweets.py > tweets.txt.
'''

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import time


#assings authentication variables, use your own keys and tokens 
access_token = your access token ...
access_token_secret = your access secret ...
consumer_key = your key ...
consumer_secret = your secret ...



class StdOutListener(StreamListener):
#this is a basic listener that just prints received tweets to stdout.
#StdOutListener is a subclass of the StreamListener that inherits all methods of
#StreamListener including on_data and on_error, which I override here.


    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status



def main():
    #handles Twitter authentication and the connection to Twitter Streaming API
    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, listener)

    nsec = 60

    #the while loop ensures that in case of an unexpected error (for instance
    # a connection timeout), the streaming continues
    while True:
        try:
            #filters Twitter Streams to capture data by the keywords
            #set async = False to avoid starting a new thread
            stream.filter(track=['anxiety', 'stress'], async = False)
            break
        except:
            time.sleep(nsec)

if __name__ == '__main__':
    main()

