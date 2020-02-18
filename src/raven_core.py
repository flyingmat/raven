import threading, queue, os, urllib.request

# can be increased in case of slow internet speeds and/or poor cpu performance
IMPLICIT_WAIT = 2

# the Tweet class holds tweet information
class Tweet:
    def __init__(self, user, text, date, time, media={}):
        self.user = user
        self.text = text
        self.date = date
        self.time = time
        self.media = media

    def __str__(self):
        return '{}: {}'.format(self.user, self.text.replace('\n', ' '))

    def download_media(self, overwrite=False, verbose=True):
        for url, filename in self.media.items():
            media_path = '{}/{}'.format(self.user, filename)
            if not os.path.isdir(self.user):
                os.mkdir(self.user)
            if not os.path.isfile(media_path) or overwrite:
                if verbose: print('    - Downloading {}...'.format(media_path))
                with urllib.request.urlopen(url, timeout=5) as media_request:
                    media_data = media_request.read()
                with open(media_path, 'wb') as media_file:
                    media_file.write(media_data)
            elif not overwrite:
                if verbose: print('    - File {} already exists!'.format(media_path))

    def as_csv(self):
        return ','.join((\
                self.user,
                '"{}"'.format(self.text.replace('\n', ' ')),
                self.date,
                self.time,
                '"{}"'.format(','.join(self.media.values())),
                '"{}"'.format(','.join(self.media.keys())),
                ))

class MediaDownloadThread(threading.Thread):
    def __init__(self, queue, overwrite=False, verbose=False):
        threading.Thread.__init__(self)
        self.queue = queue
        self.overwrite = overwrite
        self.verbose = verbose

    def run(self):
        while True:
            if media_tweet := self.queue.get():
                media_tweet.download_media(self.overwrite, self.verbose)
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
def stream_tweet_elements(driver):
    tweet_list = driver.find_element_by_xpath("//div[@id='timeline']")
    tweet_element = tweet_list.find_element_by_xpath(".//li[contains(@id, 'stream-item-tweet')]")

    yield tweet_element

    try:
        while True:
            driver.implicitly_wait(IMPLICIT_WAIT)
            driver.execute_script('arguments[0].scrollIntoView(true)', tweet_element)
            tweet_element = tweet_element.find_element_by_xpath("./following-sibling::li[contains(@id, 'stream-item-tweet')]")
            yield tweet_element
    except:
        return

# tweet stream dumping function
def tweet_stream_dump(driver, url, n=-1, download_media=False, overwrite_media=False, verbose=False):
    driver.get(url)
    tweets = []

    if download_media:
        download_queue = queue.Queue()
        download_thread = MediaDownloadThread(download_queue, overwrite=overwrite_media, verbose=verbose)
        download_thread.start()
    try:
        for tweet_element in stream_tweet_elements(driver):
            if n > -1 and tweet_i == n:
                break
            driver.implicitly_wait(IMPLICIT_WAIT/40)
            if media := tweet_media(tweet_element):
                tweet = Tweet(*tweet_info(tweet_element), media)
                if download_media:
                    download_queue.put(tweet)
            else:
                tweet = Tweet(*tweet_info(tweet_element))
            print(tweet)
            tweets.append(tweet)
    except:
        raise
    else:
        return tweets
    finally:
        print('(!) Core halting...')
        if download_media:
            if not verbose:
                print('(!) Media is being downloaded...')
            download_queue.join()
            download_queue.put(None)
            download_thread.join()
