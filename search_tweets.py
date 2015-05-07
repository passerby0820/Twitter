#!/usr/bin/python

'''
This code filters Twitter tweets. It takes tweets collected through
Twitter Streaming API over one month in Toronto region and
a vocabulary (keywords) file, and processes the 'text' field in tweets
to filter tweets that are relevant to the specific domain.
'''


import sys
import re
from TweetToMongo import TweetToMongo



#find vocab from a webpage txt file
def get_seed_vocab(file_in, file_out, regex_string):
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
    #tweet_set.insert_to_collection('toronto_tweets.txt', 'tweets')

    #create a seed_vocab list from items in the vocab.txt file
    f = open('vocab.txt', 'r')
    seed_vocab = f.readlines()
    f.close()
    seed_vocab = [item.replace('\n', '').decode('utf-8') for item in seed_vocab]

    #filter tweets containing words of the vocab
    #tweet_set.filter_tweets(seed_vocab, 'tweets', 'health')

    vocab = seed_vocab
    count =1
    #call the get_vocab_tweets method recursively to build a vocab from tweets
    while count<3:
        new_vocab = tweet_set.get_tweets_vocab(vocab, seed_vocab, 'tweets')
        vocab = new_vocab
        print 'Round %d of vocabulary building ended\n' %count
        count += 1
    print vocab


    #close the MongoDB connection
    tweet_set.client.close()


if __name__=='__main__':
    main()
