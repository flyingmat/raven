from core import *
import argparse

parser = argparse.ArgumentParser(description='Raven is a Twitter scraping utility written in python.')
parser.add_argument('profile', metavar='PROFILE', help='Profile URL')

def init_driver():
    ffprofile = FirefoxProfile()
    ffprofile.set_preference('general.useragent.override', 'Mozilla/5.0 (Windows NT 9.0; WOW64; Trident/7.0; rv:11.0) like Gecko')

    driver = Firefox(ffprofile)
    driver.implicitly_wait(5)
    driver.set_window_size(1000,1000)

    return driver

def main():
    args = parser.parse_args()

    driver = init_driver()
    profile_dump(driver, args.profile)

    driver.quit()

if __name__ == '__main__':
    main()
