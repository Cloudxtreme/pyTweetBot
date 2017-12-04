# pyTweetBot
A Twitter bot written in Python to replace yourself, search and publish news about specific subjects on Twitter.

## Installation

## Configuration file

pyTweetBot takes its configuration in a JSON file which looks as follow :

    {
        "database" :
        {
            "host" : "",
            "username" : "",
            "password" : "",
            "database" : ""
        },
        "email" : "bot@bot.com",
        "scheduler" :
        {
            "sleep": [6, 13]
        },
        "hashtags":
        [
        ],
        "twitter" :
        {
            "auth_token1" : "",
            "auth_token2" : "",
            "access_token1" : "",
            "access_token2" : "",
            "user" : ""
        },
        "friends" :
        {
            "max_new_followers" : 40,
            "max_new_unfollow" : 40,
            "follow_unfollow_ratio_limit" : 1.2,
            "interval" : [30, 45]
        },
        "forbidden_words" :
        [
        ],
        "direct_message" : "",
        "tweet" : {
            "max_tweets" : 1200,
            "exclude" : [],
            "interval" : [2.0, 4.0]
        },
        "news" :
        [
            {
                "keyword" : "",
                "countries" : ["us","fr"],
                "languages" : ["en","fr"],
                "hashtags" : []
            }
        ],
        "rss" :
        [
            {"url" : "http://feeds.feedburner.com/TechCrunch/startups", "hashtags" : "#startups", "via" : "@techcrunch"},
            {"url" : "http://feeds.feedburner.com/TechCrunch/fundings-exits", "hashtags" : "#fundings", "via" : "@techcrunch"}
        ],
        "retweet" :
        {
            "max_retweets" : 600,
            "max_likes" : 600,
            "keywords" : [],
            "nbpages" : 40,
            "retweet_prob" : 0.5,
            "limit_prob" : 1.0
            "interval" : [2.0, 4.0]
        },
        "github" :
        {
            "login": "",
            "password": "",
            "exclude": [],
            "topics" : []
        }
    }

Their is two required sections :
* Database : contains the information to connect to the MySQL database (host, username, password, database)

### Twitter configuration

## Find new tweets

`python pyTweetBot find-tweets --config /etc/bots/bot.conf --model /etc/bots/models/find_tweets.p --features words+bigrams+trigram`

## Find new retweets

`python pyTweetBot find-retweets`

## Automatise execution with crontab
