#! /usr/bin/env python3
# coding = utf-8

from pyspark import SparkContext, SparkConf
import json
import subprocess
import pickle
import itertools
import re
from html import entities 
from math import log



# 1 Initialize Spark context

# init spark context
conf = SparkConf().setMaster("local[4]").setAppName("tweet_analysis")
sc = SparkContext(conf=conf)

# Make RDD from the data in the file given by the file path present in hw2-files.txt + cache
rdd = sc.textFile("hw2-files-10mb.txt").cache()
count = rdd.count()
print('Number of elements:', count)
# Number of elements: 2150



# 2/ Parse JSON strings to JSON objects
# Filter broken tweet by checking if the line is not in json format

def safe_parse(raw_json):
    """
    Input is a String
    Output is a JSON object if the tweet is valid and None if not valid
    """
    try:
        json_object = json.loads(raw_json)
        return json_object
    except ValueError as e:
        return None

# Parse raw JSON tweets to obtain valid JSON objects:
rdd_tweet = rdd.map(lambda json_str: safe_parse(json_str))

# Check if json object of the broken tweet has a created_at field:
rdd_filtered = rdd_tweet.filter(lambda tweet: "created_at" in tweet)

#construct a pair RDD of (user_id, text):
# user_id is the id_str data field of the user dictionary
# text is the text data field
rdd_tweet = rdd_filtered.map(lambda tweet: (tweet["user"]["id_str"], tweet["text"])).cache() # .encode("utf-8") ?

rdd_user = rdd_tweet.map(lambda x: x[0]).cache()

print(rdd_tweet.take(1)[0])
# ('470520068', "I'm voting 4 #BernieSanders bc he doesn't ride a CAPITALIST PIG adorned w/ #GoldmanSachs $. SYSTEM RIGGED CLASS WAR https://t.co/P7pFm2MT9e")



# 3/ Count the number of different users in all valid tweets

# extract(map) user + distinct + count
users_count = rdd_user.distinct().count()
print('The number of unique users is:', users_count)
# The number of unique users is: 1748



# 4/ Load a pickle file as a dict and broadcast it to all node

# Use local file with your Spark session => Broadcast a dictionary to all nodes
partition =  pickle.load( open( "users-partition.pickle", "rb" ) )

# partition = sc.binaryFiles("users-partition.pickle")
print(f"Lengh of pickel partition: {len(partition)}")
print(type(partition))

# show partition key-item:
out = dict(itertools.islice(partition.items(), 5))
print(out)
# {'609232972': 4, '975151075': 4, '14247572': 4, '2987788788': 4, '3064695250': 2}



# 5/ Tweets per user partition

bc_partition = sc.broadcast(partition)
# dictionary.get(keyname, value_if_key_not_found) 
rdd_user_group = rdd_user.map(lambda user:(bc_partition.value.get(user, 7), 1)).cache()
# [(3, 1), (6, 1), (3, 1), (6, 1), (4, 1), ...]

# reduce by group + agg count
rdd_group_total = rdd_user_group.reduceByKey(lambda a, b: a + b).sortByKey(ascending=True)
# [(0, 87), (1, 242), (2, 41), (3, 349), (4, 101), ...]

counts_per_partition = rdd_group_total.collect()

for group_id, count in counts_per_partition:
    print('Group %d posted %d tweets' % (group_id, count))

# Group 0 posted 87 tweets
# Group 1 posted 242 tweets
# Group 2 posted 41 tweets
# Group 3 posted 349 tweets
# Group 4 posted 101 tweets
# Group 5 posted 358 tweets
# Group 6 posted 434 tweets
# Group 7 posted 521 tweets



# 6/ Tokenize tweets

# A function provided by the University of California San Diego that filter words.

#!/usr/bin/env python

"""
Credit UC San Diego
"""

__author__ = "Christopher Potts"
__copyright__ = "Copyright 2011, Christopher Potts"
__credits__ = []
__license__ = "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License: http://creativecommons.org/licenses/by-nc-sa/3.0/"
__version__ = "1.0"
__maintainer__ = "Christopher Potts"
__email__ = "See the author's website"

######################################################################



######################################################################
# The following strings are components in the regular expression
# that is used for tokenizing. It's important that phone_number
# appears first in the final regex (since it can contain whitespace).
# It also could matter that tags comes after emoticons, due to the
# possibility of having text like
#
#     <:| and some text >:)
#
# Most imporatantly, the final element should always be last, since it
# does a last ditch whitespace-based tokenization of whatever is left.

# This particular element is used in a couple ways, so we define it
# with a name:
emoticon_string = r"""
    (?:
      [<>]?
      [:;=8]                     # eyes
      [\-o\*\']?                 # optional nose
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth      
      |
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      [\-o\*\']?                 # optional nose
      [:;=8]                     # eyes
      [<>]?
    )"""

# The components of the tokenizer:
regex_strings = (
    # Phone numbers:
    r"""
    (?:
      (?:            # (international)
        \+?[01]
        [\-\s.]*
      )?            
      (?:            # (area code)
        [\(]?
        \d{3}
        [\-\s.\)]*
      )?    
      \d{3}          # exchange
      [\-\s.]*   
      \d{4}          # base
    )"""
    ,
    # URLs:
    r"""http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"""
    ,
    # Emoticons:
    emoticon_string
    ,    
    # HTML tags:
     r"""<[^>]+>"""
    ,
    # Twitter username:
    r"""(?:@[\w_]+)"""
    ,
    # Twitter hashtags:
    r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"""
    ,
    # Remaining word types:
    r"""
    (?:[a-z][a-z'\-_]+[a-z])       # Words with apostrophes or dashes.
    |
    (?:[+\-]?\d+[,/.:-]\d+[+\-]?)  # Numbers, including fractions, decimals.
    |
    (?:[\w_]+)                     # Words without apostrophes or dashes.
    |
    (?:\.(?:\s*\.){1,})            # Ellipsis dots. 
    |
    (?:\S)                         # Everything else that isn't whitespace.
    """
    )

######################################################################
# This is the core tokenizing regex:
    
word_re = re.compile(r"""(%s)""" % "|".join(regex_strings), re.VERBOSE | re.I | re.UNICODE)

# The emoticon string gets its own regex so that we can preserve case for them as needed:
emoticon_re = re.compile(regex_strings[1], re.VERBOSE | re.I | re.UNICODE)

# These are for regularizing HTML entities to Unicode:
html_entity_digit_re = re.compile(r"&#\d+;")
html_entity_alpha_re = re.compile(r"&\w+;")
amp = "&amp;"

######################################################################

class Tokenizer:
    def __init__(self, preserve_case=False):
        self.preserve_case = preserve_case

    def tokenize(self, s):
        """
        Argument: s -- any string or unicode object
        Value: a tokenize list of strings; conatenating this list returns the original string if preserve_case=False
        """        
        # Try to ensure unicode:
        try:
            s = str(s)
        except UnicodeDecodeError:
            s = s.encode('string_escape')
            s = str(s)
        # Fix HTML character entitites:
        s = self.__html2unicode(s)
        # Tokenize:
        words = word_re.findall(s)
        # Possible alter the case, but avoid changing emoticons like :D into :d:
        if not self.preserve_case:            
            words = map((lambda x : x if emoticon_re.search(x) else x.lower()), words)
        return words

    def tokenize_random_tweet(self):
        """
        If the twitter library is installed and a twitter connection
        can be established, then tokenize a random tweet.
        """
        try:
            import twitter
        except ImportError:
            print("Apologies. The random tweet functionality requires the Python twitter library: http://code.google.com/p/python-twitter/")
        from random import shuffle
        api = twitter.Api()
        tweets = api.GetPublicTimeline()
        if tweets:
            for tweet in tweets:
                if tweet.user.lang == 'en':            
                    return self.tokenize(tweet.text)
        else:
            raise Exception("Apologies. I couldn't get Twitter to give me a public English-language tweet. Perhaps try again")

    def __html2unicode(self, s):
        """
        Internal metod that seeks to replace all the HTML entities in
        s with their corresponding unicode characters.
        """
        # First the digits:
        ents = set(html_entity_digit_re.findall(s))
        if len(ents) > 0:
            for ent in ents:
                entnum = ent[2:-1]
                try:
                    entnum = int(entnum)
                    s = s.replace(ent, unichr(entnum))	
                except:
                    pass
        # Now the alpha versions:
        ents = set(html_entity_alpha_re.findall(s))
        ents = filter((lambda x : x != amp), ents)
        for ent in ents:
            entname = ent[1:-1]
            try:            
                s = s.replace(ent, unichr(entities.name2codepoint[entname]))
            except:
                pass                    
            s = s.replace(amp, " and ")
        return s
# END OF UCSD FUNCTIONS


# Compute relative popularity score function

tok = Tokenizer(preserve_case=False)

def get_rel_popularity(c_k, c_all):
    """Compute relative popularity score"""
    return log(1.0 * c_k / c_all) / log(2)

# Tokenize tweets
splitter = lambda x: [(x[0],t) for t in x[1]]
rdd_tokens_with_double = rdd_tweet.map(lambda tweet: (tweet[0], tok.tokenize(tweet[1]))).flatMap(lambda t: splitter(t))
rdd_unique_user_token = rdd_tokens_with_double.distinct().cache()
# [('470520068', "i'm"), ('470520068', 'voting'), ('470520068', '#berniesanders'), ...]
rdd_tokens = rdd_unique_user_token.map(lambda user_token: user_token[1]).cache()

num_of_tokens = rdd_tokens.distinct().count()
print("Number of tokens:", num_of_tokens)
# Number of tokens: 7677



# 7/ Token popularity

# Keep tokens only the most interresting token:
#  that are mentioned by at least 100 users.

rdd_token_count = rdd_tokens.map(lambda token_count:(token_count,1)).reduceByKey(lambda x,y: x+y)
# [('.', 767), ('@realdonaldtrump', 96), ('out', 83), (';', 134), ('#votetrump', 4), ...]
rdd_token_count_sorted = rdd_token_count.map(lambda token_count:(token_count[1],token_count[0])).sortByKey(ascending= False)
# [(1046, ':'), (920, 'rt'), (767, '.'), (587, 'the'), (560, 'trump'), ...]

# rdd_token_count_sorted_top_100 = popular_tokens
rdd_token_count_sorted_top_100 = rdd_token_count_sorted.filter(lambda count_token: count_token[0]>=100)
# [(1046, ':'), (920, 'rt'), (767, '.'), (587, 'the'), (560, 'trump'), ...]

num_freq_tokens = rdd_token_count_sorted_top_100.count()
#46
rdd_token_count_sorted_top_100 = rdd_token_count_sorted_top_100.map(lambda token_count:(token_count[1],token_count[0])).cache()
# need to be swap for the function
top20 = rdd_token_count_sorted_top_100.take(20)
# [(':', 1046), ('rt', 920), ('.', 767), ('the', 587),...]

print("Number of tokens:", num_freq_tokens)
# Number of tokens: 46

print('=====' + ' ' + "overall" + '=====')
for token, score in top20:
    print("%s\t%.4f" % (token, score))
# ===== overall =====
# :	1046.0000
# rt	920.0000
# .	767.0000
# the	587.0000
# trump	560.0000
# …	520.0000
# to	501.0000
# ,	497.0000
# in	385.0000
# a	383.0000
# is	382.0000
# of	300.0000
# !	285.0000
# for	275.0000
# and	263.0000
# on	218.0000
# i	216.0000
# he	191.0000
# that	190.0000
# "	181.0000



# 8/ Relative Popularity per group

splitter = lambda x: [(x[0],t) for t in x[1]]

rdd_token_unik = rdd_tweet.map(lambda tweet: (tweet[0], tok.tokenize(tweet[1]))).flatMap(lambda t: splitter(t)).distinct()

rdd_group_token_count = rdd_token_unik.map(lambda x: ((bc_partition.value.get(x[0],7), x[1]), 1)).reduceByKey(lambda x,y: x+y).cache()
# [((3, "i'm"), 3), ((3, 'voting'), 5), ((3, '#berniesanders'), 11), ...]
# ((group, token), count)

popular_10_in_each_group = []

# loop through all groups
for gid in range(0,8):
    rdd_token_count = rdd_group_token_count.filter(lambda rdd: rdd[0][0]==gid).map(lambda rdd: (rdd[0][1], rdd[1]))
    #  [("i'm", 3), ('voting', 5), ('#berniesanders', 11), ...]
    rdd_token_v_w = rdd_token_count.join(rdd_token_count_sorted_top_100)
    #  [('i', (26, 216)), ('…', (67, 520)), ('gop', (12, 106)), ...]
    rdd_token_score = rdd_token_v_w.map(lambda rdd: (rdd[0], get_rel_popularity(rdd[1][0], rdd[1][1])))
    # [('i', -3.054447784022377), ('…', -2.9562786225706827), ('gop', -3.1429579538420436),...]
    popular_10_in_each_group.append((rdd_token_score.top(10, lambda rdd:rdd[1])))

# printer loop
for k in range(8):

    group_name = "overall"
    if k is not None:
        group_name = "group %d" % k
    print('=' * 5 + ' ' + group_name + ' ' + '=' * 5)
    for token, score in popular_10_in_each_group[k]:
        print("%s\t%.4f" % (token, score))

# ===== group 0 =====
# with	-3.6088
# cruz	-3.6554
# his	-3.6582
# amp	-3.8651
# on	-3.9608
# to	-4.0145
# &	-4.0875
# i	-4.1699
# https	-4.1699
# what	-4.1699
# ===== group 1 =====
# sanders	-2.2854
# gop	-2.4060
# hillary	-2.4330
# ’	-2.4463
# bernie	-2.4835
# "	-2.6925
# are	-2.7249
# this	-2.7633
# for	-2.8179
# about	-2.8346
# ===== group 2 =====
# with	-4.3458
# donald	-4.5146
# of	-1.9069
# ?	-1.9186
# with	-1.9307
# the	-1.9588
# be	-1.9758

sc.stop()
