from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from raven_core import *
from raven_analysis import *
import argparse, traceback

# cli argument parser
parser = argparse.ArgumentParser(description='Raven is a Twitter scraping utility written in python.')
parser.add_argument('target_type', choices=['profile', 'query', 'url'])
parser.add_argument('target', metavar='TARGET', help='target to be scraped')
parser.add_argument('-n', dest='tweet_amount', type=int, help='maximum amount of tweets')
parser.add_argument('-d', '--download-media', dest='download_media', action='store_const', const=True, default=False, help='download the user''s media')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_const', const=True, default=False, help='verbose execution')
parser.add_argument('--overwrite', dest='overwrite', action='store_const', const=True, default=False, help='overwrite files when downloading media')
parser.add_argument('--headless', dest='headless', action='store_const', const=True, default=False, help='run an headless webdriver')

# creates a properly setup webdriver instance
def init_driver(headless=False):
    ffprofile = FirefoxProfile()
    # fix to get the old twitter ui
    ffprofile.set_preference('general.useragent.override', 'Mozilla/5.0 (Windows NT 9.0; WOW64; Trident/7.0; rv:11.0) like Gecko')

    options = FirefoxOptions()
    options.headless = headless

    driver = Firefox(ffprofile, options=options)
    driver.implicitly_wait(IMPLICIT_WAIT)
    driver.set_window_size(1000,1000)

    return driver

def main():
    args = parser.parse_args()

    driver = init_driver(args.headless)
    try:
        if args.target_type == 'profile':
            target_url = 'https://www.twitter.com/{}'.format(args.target)
        elif args.target_type == 'query':
            target_url = 'https://www.twitter.com/search?q={}'.format(urllib.parse.quote(args.target))
        elif args.target_type == 'url':
            target_url = args.target
        tweets = tweet_stream_dump(driver, target_url, n=args.tweet_amount, download_media=args.download_media, overwrite_media=args.overwrite, verbose=args.verbose)
        hashtag_analysis(tweets)
    except Exception as e:
        #print('(!) Unexpected error! {}'.format(e))
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
