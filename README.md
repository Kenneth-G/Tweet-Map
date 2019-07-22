# Tweet-Map
An app that allows users to search Twitter and display the Tweets on a map.
[Live Version](https://kenneth.gargan.ie/Tweet-Map/)

## Table of contents
* [About](#about)
* [Technologies](#technologies)
* [How It Works](#how-it-works)
* [Running The Code Yourself](#running-the-code-yourself)
* [Testing The Code.](testing-the-code)
* [## Thoughts on this project.](thoughts-on-this-project-&-what-i've-learned)

## About.
Tweet Map allows you to enter in a term or hashtag and returns x number of the most recent tweets which are plotted on the map. This can be used to see how different areas of the world are responding to or tweeting about different tags or trending topics.
The live version has a current cap of 20 but this is only a hard cap while the code itself can scale.

## Technologies.
### Languages: 
- Python 3.7.
- JavaScript.

### Back-End Technologies:
- [AWS Lambda.](https://aws.amazon.com/lambda/)
- [AWS API Gateway.](https://aws.amazon.com/api-gateway/)

### Libaries Used:
- [Leaflet.](https://leafletjs.com/) - Javascript Library for Interactive Maps.
- [Tweepy.](https://tweepy.readthedocs.io/en/latest/) - Python Library for interacting with Twitters API.
- [Geocoder.](https://geocoder.readthedocs.io/) - Python Library for interacting with OpenCage Geocoder.
- [unittest](https://docs.python.org/3/library/unittest.html) - Python Library for testing code. (Locally)

### Services Used:
-[Twitter API](https://developer.twitter.com/) - For getting Tweets
-[OpenCage Geocoder](https://opencagedata.com/) - For checking users locations.

## How It Works.
### Front-End:
Once the submit button is clicked, we check to see if the input is filled in, once that check has been done, we encode the users input in case there is any special characters. We then use JavaScript's fetch API to request the data from my API. Once we get a response, depending on the response, we either display an error or we loop the JSON data and call the add marker function. 

```javascript
function addMarker(lat, long, message, screen_name, id){
    var marker = L.marker([lat, long]).addTo(layerGroup);
    var tweet_url = "https://twitter.com/" + screen_name + "/status/" +id;
    marker.bindPopup(message + " -" + '<a href="'+tweet_url+'"target="_blank">'+screen_name+'</a>');
}
```
We include the screen name of the user who tweeted it and the ID of the tweet to create an anchor tag that links back to the tweet.

### Back-End.
When AWS API Gateway receives the request, it runs the Lambda function and passes in the term user searched for. After the initial checks to make sure we have a valid term, the function that actually gets the tweets is called.

```
get_tweets = api.search(q=term, result_type = "recent", count = amount_to_get, include_entities = False, max_id = oldest_id, wait_on_rate_limit_notify = True)
```

The amount to get initially starts off as twice the amount that is needed. I made this decision as not every Twitter user has their location in their profile, After that initial batch of Tweets, the amount_to_get is calculated by: 

```python
amount_to_get = total_amount - len(tweet_list)
```

```
if amount_to_get < (total_amount / 2) and total_amount >  5:
            amount_to_get = total_amount /2
            int(amount_to_get)
```

The second block of code is to make sure that if there are only a couple of tweets left to get, we aren't flooding Twitters API with single tweet requests.


With each Tweet that comes in, the location is checked and if they have one we call GeoCage

```python
geocoder.geocode(tweet.user.location, limit = 1, min_confidence = 8, no_annotations = 1)
```
-limit = How many results we want returned (We only need 1)
-min_confidence = In cases where the location we give it isn't filled in correctly or it may not be an address, we can use the min_confidence parameter to filter those out. From testing this, 1 is too vague of an area while 10 needs to be an exact address. I've found 8 gives a bit of wiggle room in case the address isn't filled out exactly. 
-no_annotations = OpenCage can provide a lot more information about the address but we only just want the coordinates and nothing else.

More information on OpenCage Parameters can be found [here](https://opencagedata.com/api#request)


Once we have a tweet with a valid location, we save the the information and check to see if we have enough Tweets.

```python
tweet_list.append({
                    'tweet_text':tweet.text,
                    'tweet_screen_name':tweet.user.screen_name,
                    'tweet_id':tweet.id_str, # Saved for linking the tweet later if we need to.
                    'tweet_location':{'lat':validate_location[0]["geometry"]["lat"], 'lng':validate_location[0]["geometry"]["lng"]}
                    })

                    #If we get the length we want, just break out of the loop
                    if len(tweet_list) == total_amount:
                        break
```

## Running the code yourself.
There are some slight changes between running it locally & running it via AWS.

### Prerequisites:
⋅⋅* Python 3.7

- Libraries: 
You need to install the modules into your working directory as they'll be need to be included in a zip file if you want to use it on AWS

..* Tweepy
```
pip install tweepy --target <your directory>
```

..* OpenCage for Python
```
pip install opencage --target <your directory>
```
..* [AWS Account](https://aws.amazon.com/) - Needed for hosting
..* [Twitter Developer Account](https://developer.twitter.com/) - Needed for Tweets (API Key needed)
..* [Opencage Account](https://opencagedata.com/) - Needed for Geo-services (API Key needed)

While zipping them, make sure to zip the actual folder and not the directory above it. This can then be uploaded when you configure your Lambda function.

## Testing The Code.

### Locally.
I've included a test_twitter_search.py file that tests:
- Make sure the url includes a "term" parameter.
- Make sure the url "term" parameter is of the correct type.
- Check to see we get the right about of tweets (if we ask for 10, we get 10, if we ask for 20 we get 20 etc.)

### On API Gateway & Lambda.
Both these AWS services have their own testing features. A standard term test would look like:

```
{
  "queryStringParameters": {
    "term": "Wednesday"
  }
}
```

While a invalid parameter test would be entered as: 
```
{
  "queryStringParameters": {
    "trm": "Wednesday"
  }
}
```

## Thoughts on this project.
When I was thinking of a project, I didn't really know what to make. I knew I wanted it to expose me to a mixture of technologies that I hadn't had much exposure to (or none at all). I wanted it to challenge me and I didn't want it to be something that I could just follow a tutorial from start to finish. 

I settled on a Twitter Map Application because it ticked all those boxes for me. I felt it just covered so many important areas like Front-End Development, Back-End Development, API Calls (creating my own and using 3rd party) and exposure to serverless technology.

I enjoyed every moment of creating this. I loved coming across technologies like Cross-Origin Resource Sharing (CORS) and just thinking this makes securing my app so much easier. I really think that was a good choice of a project to solidify my knowledge of the development process.
