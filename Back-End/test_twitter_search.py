import unittest
from twitter_search import new_tweet_request


# A few things to test for:
# - If we ask to get x number of tweets, it returns x number of tweets
# - It throws an error with a tag that has no tweets with it. 

class search_test_case(unittest.TestCase):
    
    def test_standard_request(self):
        expected_JSON = {
            "queryStringParameters": {
                "term": "Wednesday"
            }
        }   

        self.assertTrue(len(new_tweet_request(expected_JSON,None)),20)


    def test_no_tweets(self):
        expected_no_results_parameters_JSON = {
            "queryStringParameters": {
                "term": "N0Twe3tsWithThisLab3l"
            }
        }
        expected_no_results_parameters_return= {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": "{\"Error\": \"Not Enough Tweets Found\"}"
        }

        self.assertEqual(new_tweet_request(expected_no_results_parameters_JSON,None),expected_no_results_parameters_return)


    def test_unexpected_term(self):
        unexpected_term_parameters = {
            "queryStringParameters": {
                "tem": "N0Twe3tsWithThisLab3l"
            }
        }
        unexpected_term_parameters_return= {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": "{\"Error\": \"\\\"term\\\" not included\"}"
        }

        self.assertEqual(new_tweet_request(unexpected_term_parameters,None),unexpected_term_parameters_return)




if __name__ == '__main__':
    unittest.main()