'''
This class contains a constructor that establishes connection to MongoDB server
and methods for inserting tweets to a MongoDb database, filtering tweets, and
building a vocabulary out of the tweet texts.
'''


import pymongo
import json
import sys
import re
import ast
from TweetParsing import TweetParsing
from sklearn.feature_extraction.text import CountVectorizer



class TweetToMongo:

    def __init__(self, db_name):
        #connect to MongoDB
        #create databse db_name if not exists, or use it if exists
        try:
            self.client = pymongo.Connection(host = 'localhost', port = 27017)
            self.database = self.client[db_name]
            print 'Connected successfully'
        except:
            #in case of errors
            print 'Could not connect to MongoDB'



    def insert_to_collection(self, filename, collection_name):
        #insert tweets from txt file to a MongoDB collection tweets
        db = self.database
        f = open(filename, 'r')
        for line in f:
            try:
                #if input is string of python dic, make a python dic by
                tweet = ast.literal_eval(line)
                #if input file is json, make python dic by
                # tweet = json.loads(line)
                db[collection_name].insert(tweet, safe = True)
            except:
                continue
        f.close()



    def filter_tweets(self, vocab, collection_in, collection_out):
        #given a vocabulary of keywords, filter tweets that contain at least
        #one word of the vocab.
        db = self.database
        #join items in the vocab list by '|', which works as or
        regex_string= '|'.join(vocab)
        REGEX = re.compile(regex_string)
        filtered_tweets = db[collection_in].find({'text': {'$regex':REGEX}})

        for tweet in filtered_tweets:
            db[collection_out].insert(tweet, safe = True)



    def get_tweets_vocab(self, vocab, seed_vocab, collection_name):
        #take a seed vocab and build a new vocab of tweets containing
        #words of the seed vocab
        db = self.database
        num_features = 2000
        #initialize bag of words object
        cv = CountVectorizer(analyzer = 'word', max_features = num_features)

        parsed_tweets = []

        regex_string = '|'.join(vocab)
        REGEX = re.compile(regex_string)

        print 'Filtering tweets containing a word of the vocab ...\n'
        filtered_tweets = db[collection_name].find({'text': {'$regex':REGEX}})

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

        #select only those elements that are not too frequent (to avoid words
        #like 'today' that are not useful)
        new_vocab = new_vocab[len(new_vocab)//10:2*len(new_vocab)//10]

        #concatenate selected elements of the new vocab to the seed vocab
        vocab = set(seed_vocab + new_vocab)

        return vocab