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
        '''connects to MongoDB
        and creates database db_name if not exists, or use it if exists'''
        try:
            self.client = pymongo.Connection(host = 'localhost', port = 27017)
            self.database = self.client[db_name]
            print 'Connected successfully \n'
        except:
            #in case of errors
            print 'Could not connect to MongoDB \n'



    def insert_to_collection(self, filename, collection_name):
        '''inserts tweets from a txt file to a MongoDB collection tweets'''
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



    def filter_tweets(self, regex_string, collection_in, collection_out = None):
        '''given a pattern regex_string, filters tweets that contain that pattern'''
        db = self.database
        print 'Filtering tweets containing a word of the vocab ... \n'
        filtered_tweets = db[collection_in].find({'text': {'$regex':regex_string}})
        # len(re.findall(regex_string, tweet['text'])) shows number of matches

        if collection_out:
            for tweet in filtered_tweets:
                db[collection_out].insert(tweet, safe = True)
        else:
            return filtered_tweets



    @staticmethod
    def parse_tweets_tolist(filtered_tweets):
        '''takes a set of tweets, parses the text field in each tweet, and returns
        a list of parsed tweet texts.'''
        parsed_tweets = []
        num = 1
        for tweet in filtered_tweets:

            if num>=10000 and num%10000 == 0:
                print 'Parsing filtered tweet %d  \n' %num

            #use the tweet_to_words method to parse tweets
            parsed_tweet = TweetParsing.tweet_to_words(tweet['text'],
                                                       remove_stopwords = True)
            parsed_tweets.append(parsed_tweet)
            num += 1

        return parsed_tweets



    def get_tweets_vocab(self, vocab, collection_name):
        '''takes a seed vocab and builds a new vocab of tweets containing
        words of the seed vocab'''

        #join items in the vocab list by '|', which works as or
        regex_string = '|'.join(vocab)

        filtered_tweets = self.filter_tweets(regex_string, collection_name)

        print 'Parsing tweets started ... \n'
        parsed_tweets = self.parse_tweets_tolist(filtered_tweets)

        print 'Bag of words ... \n'
        #find a vocab of the filtered tweets and vectorize them using bag of words

        # vocabulary to be specified in the CountVectorizer, should be a dic
        # vocab_dic = {}
        # for item in vocab:
        #     vocab_dic[item] = vocab.index(item)

        num_features = 2000

        # initialize bag of words object
        cv = CountVectorizer(analyzer = 'word', max_features = num_features)

        vectorized_tweets = cv.fit_transform(parsed_tweets).toarray()

        #get words with their frequency in a list of tuples
        words_freq = zip(cv.get_feature_names(), vectorized_tweets.sum(axis = 0))

        #sort the list by frequency of words, ascending
        words_freq = sorted(words_freq, key = lambda x: x[1])

        new_vocab = [item[0] for item in words_freq]

        #select only those elements that are not too frequent (to avoid words
        #like 'today' that are not useful) or too rare
        new_vocab = new_vocab[len(new_vocab)//5:4*len(new_vocab)//5]

        return new_vocab
