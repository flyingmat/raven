from raven_core import *

def n_media_analysis(tweets):
    media_stats = {}
    for tweet in tweets:
        if type(tweet) == MediaTweet:
            media_stats[len(tweet.media)] = 1 if len(tweet.media) not in \
                    media_stats else media_stats[len(tweet.media)] + 1
    print('Tweets with images: {}%'.format(round(sum(media_stats.values())*100/len(tweets))))
    for n_media, amount in media_stats.items():
        print('{}: {} tweets'.format(n_media, amount))
