from selenium.webdriver import Firefox, FirefoxProfile
import threading, queue, os, urllib.request

# can be increased in case of slow internet speeds and/or poor cpu performance
IMPLICIT_WAIT = 2

# the Tweet class holds tweet information
class Tweet:
    def __init__(self, user, text, date, time):
        self.user = user
        self.text = text
        self.date = date
        self.time = time
    def __str__(self):
        return ','.join((self.user, '"{}"'.format(self.text), self.date, self.time))

class MediaTweet(Tweet):
    def __init__(self, user, text, date, time, media):
        super().__init__(user, text, date, time)
        self.media = media
    def download_media(self, overwrite=False):
        for url, filename in self.media.items():
            media_path = '{}/{}'.format(self.user, filename)
            if not os.path.exists(media_path) or overwrite:
                if verbose: print('    - Downloading {}...'.format(media_path))
                with urllib.request.urlopen(url, timeout=5) as media_request:
                    media_data = media_request.read()
                with open(media_path, 'wb') as media_file:
                    media_file.write(media_data)
            elif not overwrite:
                if verbose: print('    - File {} already exists!'.format(media_path))
    def __str__(self):
        return super().__str__() + ',' + \
                '"{}"'.format(','.join(self.media.values())) + ',' + \
                '"{}"'.format(','.join(self.media.keys()))

class MediaDownloadThread(threading.Thread):
    def __init__(self, queue, overwrite=False):
        threading.Thread.__init__(self)
        self.queue = queue
        self.overwrite = overwrite

    def run(self):
        while True:
            if media_tweet := self.queue.get():
                media_tweet.download_media(self.overwrite)
            else:
                break
            self.queue.task_done()

# return a tweet's user given its webelement
def tweet_user(tweet_element):
    return tweet_element.find_element_by_xpath(".//span[contains(@class, 'username')]").text[1:]

# return a tweet's text given its webelement
def tweet_text(tweet_element):
    return tweet_element.find_element_by_xpath(".//p[contains(@class, 'tweet-text')]").text

# return a tweet's date and time of posting given its webelement
def tweet_datetime(tweet_element):
    return tweet_element.find_element_by_xpath(".//a[contains(@class, 'tweet-timestamp')]")\
            .get_attribute('title')\
            .split(' - ')[::-1]

# return info about a tweet given its webelement
def tweet_info(tweet_element):
    return (tweet_user(tweet_element), tweet_text(tweet_element), *tweet_datetime(tweet_element))

# return a list of a tweet's image urls
def tweet_media(tweet_element):
    try:
        media_container = tweet_element.find_element_by_xpath(".//div[@class='AdaptiveMediaOuterContainer']")
        media_elements = media_container.find_elements_by_xpath(".//img[@src]")
        media = {e.get_attribute('src')+':orig':e.get_attribute('src').split('/')[-1] for e in media_elements}
        return media
    except:
        return {}

# tweet scraper, implemented as generator
def profile_tweet_elements(driver):
    tweet_list = driver.find_element_by_xpath("//div[@id='timeline']")
    tweet_element = tweet_list.find_element_by_xpath(".//li[contains(@id, 'stream-item-tweet')]")

    yield tweet_element

    try:
        while True:
            driver.implicitly_wait(IMPLICIT_WAIT)
            driver.execute_script('arguments[0].scrollIntoView(true)', tweet_element)
            tweet_element = tweet_element.find_element_by_xpath("./following-sibling::li")
            yield tweet_element
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
        for tweet_element in profile_tweet_elements(driver):
            driver.implicitly_wait(IMPLICIT_WAIT/40)
            if media := tweet_media(tweet_element):
                tweet = MediaTweet(*tweet_info(tweet_element), media)
                if download_media:
                    download_queue.put(tweet)
            else:
                tweet = Tweet(*tweet_info(tweet_element))
            if verbose: print(tweet)
    except:
        raise
    finally:
        print('(!) Core halting...')
        if download_media:
            download_queue.join()
            download_queue.put(None)
            download_thread.join()
