from selenium.webdriver import Firefox, FirefoxProfile

# can be increased in case of slow internet speeds and/or poor cpu performance
IMPLICIT_WAIT = 2

# the Tweet class holds tweet information
class Tweet:
    def __init__(self, text, media_urls = []):
        self.text = text
        self.media_urls = media_urls

# return a tweet's text given its webelement
def tweet_text(tweet_element):
    return tweet_element.find_element_by_xpath(".//p[contains(@class, 'tweet-text')]").text

def tweet_media_urls(tweet_element):
    try:
        media_container = tweet_element.find_element_by_xpath(".//div[@class='AdaptiveMediaOuterContainer']")
        media_elements = media_container.find_elements_by_xpath(".//*[@src]")
        media_urls = [e.get_attribute('src')+':orig' for e in media_elements]
        return media_urls
    except:
        return []

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
        raise StopIteration

# profile dumping function, prints all of a user's tweets
def profile_dump(driver, profile_url):
    driver.get(profile_url)

    try:
        for tweet in profile_tweet_scrape(driver):
            print(tweet.text)
            print(tweet.media_urls)
    except StopIteration:
        pass
