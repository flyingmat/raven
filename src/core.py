from selenium.webdriver import Firefox, FirefoxProfile

class Tweet:
    def __init__(self, text, media = []):
        self.text = text

def tweet_text(tweet_element):
    return tweet_element.find_element_by_xpath(".//p[contains(@class, 'tweet-text')]").text

def profile_tweet_scrape(driver):
    tweet_list = driver.find_element_by_xpath("//div[@id='timeline']")
    tweet = tweet_list.find_element_by_xpath(".//li[contains(@id, 'stream-item-tweet')]")

    yield Tweet(tweet_text(tweet))

    try:
        while True:
            driver.execute_script('arguments[0].scrollIntoView(true)', tweet)
            tweet = tweet.find_element_by_xpath("./following-sibling::li")
            yield Tweet(tweet_text(tweet))
    except:
        raise StopIteration

def profile_dump(driver, profile_url):
    driver.get(profile_url)

    try:
        for tweet in profile_tweet_scrape(driver):
            print(tweet.text)
    except:
        return False
    return True
