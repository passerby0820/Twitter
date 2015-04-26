#!/usr/bin/python

'''
This code processes Twitter text. It takes tweets obtained through
Twitter Streaming API over one month in Toronto region and processes
the 'text' field to build a classifier for health and medical tweets.
'''


import pymongo
import json
import sys
import re
import pandas as pd
import ast
from TweetParsing import TweetParsing
from sklearn.feature_extraction.text import CountVectorizer
from nltk import PorterStemmer
import timeit


#insert docs from txt file to a MongoDB database.
def insert_to_db(filename, client):

    db = client['toronto_tweets_database']

    #insert all the tweets into the collection
    f = open(filename, 'r')
    for line in f:
        try:
            #if input is string of python dic, make a python dic by
            tweet = ast.literal_eval(line)
            #if input file is json, make python dic by
            # tweet = json.loads(line)
            db.tweets.insert(tweet, safe = True)
        except:
            continue
    f.close()


#given a vocabulary of health keywords, filter tweets that contain at least
# one word of the vocab.

def get_health_tweets(client, vocab):

    db = client['toronto_tweets_database']
    #join items in the vocab list by '|', which works as or
    regex_string= '|'.join(vocab)
    REGEX = re.compile(regex_string)
    filtered_tweets = db.tweets.find({'text': {'$regex':REGEX}})

    for tweet in filtered_tweets:
        db.health.insert(tweet, safe = True)


#take a seed vocab and build a vocab of tweets containing words of the seed vocab
def get_vocab_tweets(client, vocab, seed_vocab):

    db = client['toronto_tweets_database']

    #initialize bag of words object
    num_features = 2000
    cv = CountVectorizer(analyzer = 'word', max_features = num_features)

    parsed_tweets = []

    regex_string = '|'.join(vocab)
    REGEX = re.compile(regex_string)

    print 'Filtering tweets containing a word of the vocab ...\n'
    filtered_tweets = db.tweets.find({'text': {'$regex':REGEX}})

    num = 1
    for tweet in filtered_tweets:

        if num>=5000 and num%5000 == 0:
            print 'Parsing filtered tweet %d  \n' %num

        #use the tweet_to_words method to parse tweets
        parsed_tweet = TweetParsing.tweet_to_words(tweet['text'],
                                                   remove_stopwords = True)

        parsed_tweets.append(parsed_tweet)
        num += 1


    print 'Bag of words ...\n'
    #find a vocab of the filtered tweets and vectorize them using a bag of word
    #model
    vectorized_tweets = cv.fit_transform(parsed_tweets).toarray()

    #get words with their frequency in a list of tuples
    words_freq = zip(cv.get_feature_names(), vectorized_tweets.sum(axis=0))

    #sort the list by frequency of words
    words_freq = sorted(words_freq, key = lambda x: x[1])

    new_vocab = [item[0] for item in words_freq]

    #concatenate selected elements of the new vocab to the seed vocab
    vocab = seed_vocab + new_vocab[len(new_vocab)//10:2*len(new_vocab)//10]

    client.close()

    return vocab


#find health vocab from a webpage text
def get_vocab_web(file_in, file_out, regex_string):
    f = open(file_in, 'r')
    match = set(re.findall(regex_string, f.read()))
    f.close()

    f = open(file_out, 'w')
    for item in match:
        f.write(item)
        f.write('\n')
    f.close()



def main():
    # connect to MongoDB
    try:
        client = pymongo.Connection(host = 'localhost', port = 27017)
        print 'connected successfully'
    except:
        sys.stderr.write("Could not connect to MongoDB: %s" % e)


    #insert tweets from the txt file to a MongoDB collection
    # insert_to_db('toronto_tweets.txt', client)

    f = open('vocab.txt', 'r')
    seed_vocab = f.readlines()
    f.close()
    seed_vocab = [item.replace('\n', '') for item in seed_vocab]

    vocab = seed_vocab
    count =1
    #call the get_vocab_tweets function recursively to build a vocab from tweets
    while count<6:
        new_vocab = get_vocab_tweets(client, vocab, seed_vocab)
        vocab = new_vocab
        print 'Round %d of vocabulary building ended\n' %count
        count += 1
    print vocab


    #filter tweets containing words of the vocab
    # get_health_tweets(client, vocab)


if __name__=='__main__':
    main()
