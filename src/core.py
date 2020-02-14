from selenium.webdriver import Firefox, FirefoxProfile
import threading, queue, os, urllib.request

# can be increased in case of slow internet speeds and/or poor cpu performance
IMPLICIT_WAIT = 0.5

# the Tweet class holds tweet information
class Tweet:
    def __init__(self, text, media_urls = []):
        self.text = text
        self.media_urls = media_urls

class MediaDownloadThread(threading.Thread):
    def __init__(self, queue, overwrite=False):
        threading.Thread.__init__(self)
        self.queue = queue
        self.overwrite = overwrite

    def run(self):
        while True:
            if media_url := self.queue.get():
                download_media(media_url, self.overwrite)
            else:
                break
            self.queue.task_done()

# return a tweet's text given its webelement
def tweet_text(tweet_element):
    return tweet_element.find_element_by_xpath(".//p[contains(@class, 'tweet-text')]").text

# return a list of a tweet's image urls
def tweet_media_urls(tweet_element):
    try:
        media_container = tweet_element.find_element_by_xpath(".//div[@class='AdaptiveMediaOuterContainer']")
        media_elements = media_container.find_elements_by_xpath(".//*[@src]")
        media_urls = [e.get_attribute('src')+':orig' for e in media_elements]
        return media_urls
    except:
        return []

def download_media(media_url, overwrite=False):
    filename = media_url.split('/')[-1].split(':')[0]
    if not os.path.exists(filename) or overwrite:
        print('    - Downloading {}...'.format(filename))
        with urllib.request.urlopen(media_url, timeout=5) as media:
            media_data = media.read()
        with open(filename, 'wb') as media_file:
            media_file.write(media_data)
    elif not overwrite:
        print('    - File {} already exists!'.format(filename))

# tweet scraper, implemented as generator
def profile_tweet_scrape(driver):
    driver.implicitly_wait(IMPLICIT_WAIT)
    tweet_list = driver.find_element_by_xpath("//div[@id='timeline']")
    tweet = tweet_list.find_element_by_xpath(".//li[contains(@id, 'stream-item-tweet')]")

    driver.implicitly_wait(IMPLICIT_WAIT/4)
    yield Tweet(tweet_text(tweet), tweet_media_urls(tweet))

    try:
        while True:
            driver.execute_script('arguments[0].scrollIntoView(true)', tweet)
            tweet = tweet.find_element_by_xpath("./following-sibling::li")
            yield Tweet(tweet_text(tweet), tweet_media_urls(tweet))
    except:
        return

# profile dumping function, prints all of a user's tweets
def profile_dump(driver, profile_url, download_media=True, overwrite_media=False):
    driver.get(profile_url)

    if download_media:
        download_queue = queue.Queue()
        download_thread = MediaDownloadThread(download_queue, overwrite=overwrite_media)
        download_thread.start()
    try:
        for tweet in profile_tweet_scrape(driver):
            if download_media:
                for media_url in tweet.media_urls:
                    download_queue.put(media_url)
    except:
        raise
    finally:
        print('(!) Core halting...')
        download_queue.join()
        download_queue.put(None)
        download_thread.join()
