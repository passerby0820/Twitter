#!/usr/bin/python

'''
This code filters Twitter tweets. It takes tweets collected through
Twitter Streaming API over one month in Toronto region and
a vocabulary (keywords) file, and processes the 'text' field in tweets
to filter tweets that are relevant to the specific domain. It also drives a
new vocabulary from the tweets.
'''


import sys
import re
from TweetToMongo import TweetToMongo


def get_seed_vocab(file_in, file_out, regex_string):
    '''finds vocab from a webpage txt file'''

    f = open(file_in, 'r')
    match = set(re.findall(regex_string, f.read()))
    f.close()

    f = open(file_out, 'w')
    for item in match:
        f.write(item)
        f.write('\n')
    f.close()



def main():
    #create an instance object of the class TweetToMongo and
    #use database 'toronto_tweets'
    tweet_set = TweetToMongo('toronto_tweets')

    #insert tweets from the txt file to a MongoDB collection
    tweet_set.insert_to_collection('toronto_tweets.txt', 'tweets')

    #create a vocab list from items in the vocab.txt file
    f = open('vocab.txt', 'r')
    vocab = f.readlines()
    f.close()
    vocab = [item.replace('\n', '').decode('utf-8') for item in vocab]

    #join items in the vocab list by '|', which works as or
    regex_string = '|'.join(vocab)

    #filter tweets containing words of the vocab
    tweet_set.filter_tweets(regex_string, 'tweets', 'health')

    #call the get_tweets_vocab method to build a vocab from tweets
    new_vocab = tweet_set.get_tweets_vocab(vocab, 'tweets')

    print new_vocab

    #close the MongoDB connection
    tweet_set.client.close()


if __name__=='__main__':
    main()
