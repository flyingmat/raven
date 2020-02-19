from raven_core import *
import re

def n_media_analysis(tweets):
    media_stats = {}
    for tweet in tweets:
        if tweet.media:
            media_stats[len(tweet.media)] = 1 if len(tweet.media) not in \
                    media_stats else media_stats[len(tweet.media)] + 1
    print('Tweets with images: {}%'.format(round(sum(media_stats.values())*100/len(tweets))))
    for n_media, amount in media_stats.items():
        print('{}: {} tweets'.format(n_media, amount))

def hashtag_analysis(tweets):
    hashtags = {}
    hashtag_pattern = r'#(.*?)(\W|\Z|\n)'
    for tweet in tweets:
        matches = []
        try:
            for m in re.findall(hashtag_pattern, tweet.text):
                hashtags[m[0].lower()] = 1 if m[0].lower() not in hashtags else \
                        hashtags[m[0].lower()] + 1
        except:
            pass
    hashtags_sorted = sorted(hashtags.items(), key=lambda h: -h[1])
    print('{} hashtags ({} total):\n'.format(len(hashtags_sorted), sum(hashtags.values())) + \
            '\n'.join(['#{},{},{},{}'.format(h[0], \
                            h[1],\
                            (100*h[1]/hashtags_sorted[0][1]), \
                            (100*h[1]/sum(hashtags.values()))
                    ) \
            for h in hashtags_sorted]))
