import tweepy
import json
from opencage.geocoder import OpenCageGeocode # pylint: disable=import-error

#Key's needed for the different API's. 
#It is not recommended you store keys here. If you are running this on AWS, use their Secrets Manager.
#This is only temp storage to run it locally.
############################################################################
#Twitter
customer_key = ""
customer_secret = ""

access_token = ""
access_token_secret = ""
############################################################################

#OpenCage
Opencage_key = ""
############################################################################


def new_tweet_request(event, context):
    
    #This can be changed to get mo
    amount = 20
    
    #Check to see if there a term in our string parameters.
    body = None
    term = None
    if 'term' in event['queryStringParameters']:
        term = event['queryStringParameters']['term']
    else:
        body = {
            'Error':'"term" not included'
        }
    
    #Check to see if the term has been assigned in our string parameters
    if not validate_input(term) and body is None:
        body = {
            'Error': 'term not assigned'
        }
    
    #If we made it this far with no error, its safe to assume our term is valid.
    if body is None:
        body = get_tweet_request(term,amount)

    return {
        'statusCode':200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }
#Make sure we get a str & its not blank.
def validate_input(term):
    
    if type(term) != str:
        return False
    if not term:
        return False
    
    return True

#Authentication for Twitter API. 
#Since this code will only run when it's needed, we need to authenticate each time. 
def authenticate_twitter_request():
    auth = tweepy.OAuthHandler(customer_key, customer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    return api



# This function will get the amount of tweets we need and adjust the amount of tweets we request depending on how many we've found so far. 
def get_tweet_request(term, total_amount):
    #Save our list of tweets we got.
    tweet_list = []

    #Authenticate Twitter & OpenCage
    api = authenticate_twitter_request()
    geocoder = OpenCageGeocode(Opencage_key)
    
    #Store the oldest ID of the batch of tweets so we'll have a reference to how far back we need to go if we need to get more tweets. We'll use this later in our loop.
    oldest_id = None
    
    #Initally get more tweets than is needed as not everyone will have a location in their profile and this will reduce the amount of API calls we need.
    amount_to_get = total_amount * 2

    while len(tweet_list) != total_amount:
        #API search call for tweets using the term we want with the amount we want.
        get_tweets = api.search(q=term, result_type = "recent", count = amount_to_get, include_entities = False, max_id = oldest_id, wait_on_rate_limit_notify = True)
        
        #We don't want to get the same ID twice so we need to subtract 1 from the ID the newer tweets will have a higher ID while the older tweets will have a lower number. 
        if get_tweets:
            #Assign the max_id of our current batch of tweets. That way if we need to get more tweets with a location, We know how far back our starting point will be.
            oldest_id = get_tweets[-1].id

        if oldest_id is not None:
            oldest_id -= 1

        if not get_tweets:
            return{
                'Error': 'Not Enough Tweets Found'
            }

        #Loop through each item we got, check the text & check to see if there is a location. 
        #We also want to ignore tweets containing RT or @. see filter_text function for comments.
        for tweet in get_tweets:
            if not filter_text(tweet.text):
                continue
            if not tweet.user.location:
                continue
            else:
                validate_location = geocoder.geocode(tweet.user.location, limit = 1, min_confidence = 8, no_annotations = 1)
                if not validate_location:
                    continue
                else:
                    tweet_list.append({
                    'tweet_text':tweet.text,
                    'tweet_screen_name':tweet.user.screen_name,
                    'tweet_id':tweet.id_str, # Saved for linking the tweet later if we need to.
                    'tweet_location':{'lat':validate_location[0]["geometry"]["lat"], 'lng':validate_location[0]["geometry"]["lng"]}
                    })

                    #If we get the length we want, just break out of the loop
                    if len(tweet_list) == total_amount:
                        break

        #At the end of looking through our batch of tweets, We need to update the remainder of tweets.                    
        amount_to_get = total_amount - len(tweet_list)
        
        #The standard search lets me make 450 requests per 15 minute window. If a request is made where users don't have their location and I just have 1 tweet with a location to get, I'll be making a lot of requests.
        #These 2 lines of code makes it so if I am under half, I just keep getting half of what I needed. It will reduce the amount of requests I need to make. 
        if amount_to_get < (total_amount / 2) and total_amount >  5:
            amount_to_get = total_amount /2
            int(amount_to_get)

    return tweet_list


# Exclude tweets that start with an @ or RT
# @ means its directed to someone rather than a someone commenting on a topic or hashtag. 
# RT (retweet) means that its the same tweet being tweeted all over again which means I may end up with a few of the same tweets.
def filter_text(text):
    if text[0] == '@':
        return False

    if text.split(' ',1)[0] == "RT":
        return False

    return True