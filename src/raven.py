from core import *
import argparse

# cli argument parser
parser = argparse.ArgumentParser(description='Raven is a Twitter scraping utility written in python.')
parser.add_argument('profile', metavar='PROFILE', help='Profile URL')

# creates a properly setup webdriver instance
def init_driver():
    ffprofile = FirefoxProfile()
    # fix to get the old twitter ui
    ffprofile.set_preference('general.useragent.override', 'Mozilla/5.0 (Windows NT 9.0; WOW64; Trident/7.0; rv:11.0) like Gecko')

    driver = Firefox(ffprofile)
    # can be increased in case of slow internet speeds and/or poor cpu performance
    driver.implicitly_wait(5)
    driver.set_window_size(1000,1000)

    return driver

def main():
    args = parser.parse_args()

    driver = init_driver()
    try:
        profile_dump(driver, args.profile)
    except Exception as e:
        print(e)
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
