from core import *
import argparse, traceback

# cli argument parser
parser = argparse.ArgumentParser(description='Raven is a Twitter scraping utility written in python.')
parser.add_argument('profile', metavar='PROFILE', help='Profile URL')
parser.add_argument('-d', '--download-media', dest='download_media', action='store_const', const=True, default=False, help='download the user''s media')
parser.add_argument('--overwrite', dest='overwrite', action='store_const', const=True, default=False, help='overwrite files when downloading media')

# creates a properly setup webdriver instance
def init_driver():
    ffprofile = FirefoxProfile()
    # fix to get the old twitter ui
    ffprofile.set_preference('general.useragent.override', 'Mozilla/5.0 (Windows NT 9.0; WOW64; Trident/7.0; rv:11.0) like Gecko')

    driver = Firefox(ffprofile)
    driver.implicitly_wait(IMPLICIT_WAIT)
    driver.set_window_size(1000,1000)

    return driver

def main():
    args = parser.parse_args()

    driver = init_driver()
    try:
        profile_dump(driver, args.profile, download_media=args.download_media, overwrite_media=args.overwrite)
    except Exception as e:
        print('(!) Unexpected error! {}'.format(e))
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
