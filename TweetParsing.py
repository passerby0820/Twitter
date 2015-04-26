'''
This class contains methods for pre-processing raw text.
'''

import sys
import re
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk import PorterStemmer


class TweetParsing(object):

    # convert raw tweet text into a list of words, remove html tags, 
    # punctuations, and optionally stopwords.
    @staticmethod
    def tweet_to_words(tweet, remove_stopwords = False):
        # BeautifulSoup pulls data out of html file
        # here it removes html tags and markups
        text = BeautifulSoup(tweet).get_text()

        # replace numbers by word number
        text=re.sub(r'[0-9]+','number',text)

        #replaces URLs by word httpaddr
        text = re.sub(r'(http|https)://[^\s]*', 'httpaddr', text)

        # remove punctuations (they can be analyzed for better results)
        text = re.sub(r'[^a-zA-Z]', ' ', text)
        text = text.lower()

        #make a list of words
        words_list = text.split()

        #download nltk text data sets, including stop words
        #nltk.download()

        if remove_stopwords:
            # get stopwords, searching a set is faster than searching a list
            stops = set(stopwords.words('english'))
            # remove stopwords
            words_list = [word for word in words_list if not word in stops]

        # reduce words to their stems
        stemmer=PorterStemmer()
        words_list=[stemmer.stem(word) for word in words_list]
        # return the list of words
        return words_list



    # convert a list of tweet texts to a list of clean processed tweet texts with
    # each tweet text a list of words
    @staticmethod
    def all_tweets_to_words(tweets_list, remove_stopwords = False):

        clean_tweets = []
        for tweet in tweets_list:
            if len(tweet) > 0:
                clean_tweets.append(
                    TweetParsing.tweet_to_words(tweet, remove_stopwords))

        return clean_tweets
