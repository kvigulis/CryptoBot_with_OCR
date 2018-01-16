import winsound
import time
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import re

try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract
import cv2
import urllib.request
import numpy as np

from concurrent.futures import ThreadPoolExecutor, Future
pool = ThreadPoolExecutor(max_workers=2)

import chess

import logging
from datetime import datetime

def get_current_time():
    return datetime.now().strftime('%Y-%m-%d; %H:%M:%S.%f')

# TODO: DANGER: Always remember to disable 'Quick edit mode' for PowerShell, when running the code from it, to avoid halting the program by accidental mouse click on the PowerShell window.

logfile_name = 'history_' + datetime.now().strftime('%Y-%m-%d;%H-%M-%S') + '.txt'
logging.basicConfig(filename=logfile_name,level=logging.DEBUG)
logging.info(' ============ %s ============ File started', get_current_time())

# TODO: **********************************************************************************
twitter_user_name = 'karlisvigulis'
btc_in_vallet = 0.00052
safety_margin = 0.2

# ==== Twitter part(message fetch): =====
consumer_key = 'xxx'
consumer_secret = 'xxxx'
access_token = 'xxxxx'
access_token_secret = 'xxxxx'

first_window = webdriver.Chrome("C:\chromedriver.exe")  # Search result window (main)
first_window.implicitly_wait(25)
first_window.get("https://www.twitter.com")


def OCR_twitter(link):

    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR_305\\tesseract'
    # Include the above line, if you don't have tesseract executable in your PATH
    # Example tesseract_cmd: 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'

    before = time.time()
    first_window.get(link) # open the tweeted link in Chrome
    image_link = first_window.find_element_by_class_name('AdaptiveMedia-container').get_attribute('innerHTML')
    image_link = re.search("(?P<url>https?://[^\s]+)", image_link).group("url")[:-1] # find link in HTML source code
    print(image_link)
    first_window.get(image_link) # open the coin image in Chrome
    first_window.save_screenshot('twitter.png')
    img = cv2.imread('twitter.png')
    after = time.time()
    print("Find image URL time: ", after - before)
    #logging.info(get_current_time(), " - Find image URL time: ")
    before = time.time()
    height, width, channels = img.shape
    roi = img[int(height * 0.02):int(height * 0.4), int(width * 0.1):int(width * 0.9)]
    cv2.imwrite('twitter.png', roi)

    text = pytesseract.image_to_string(Image.open('twitter.png'), lang='eng')

    print("Text: ", text)
    label = text.split("(")[1].split(")")[0]
    print("Label: ", label)
    after = time.time()
    print("OCR time: ", after - before)
    return label

class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        d = json.loads(data)

        if list(d.keys())[0]== 'created_at':
            # TODO: **********************************************************************************
            if d['user']['screen_name'] == twitter_user_name and d["in_reply_to_screen_name"] == None \
                    and d['is_quote_status'] == False:
                print("Text: ", d['text'])
                print(get_current_time(), "START TIME")
                logging.info(' ============ %s  ============ - McAfee tweet text received: %s', get_current_time(), d['text'])
                tweet_link = re.search("(?P<url>https?://[^\s]+)", d['text']).group("url")
                get_current_time()
                coin_label = OCR_twitter(tweet_link)
                print("Coin Label: ", coin_label)
                logging.info(' ============ %s  ============ - OCR done. Coin label inference: %s', get_current_time(), coin_label)
                #logging.info(get_current_time(), " - Coin Label Recognised: ", coin_label)
                pool.submit(winsound.PlaySound,'alarm_sound2.wav', winsound.SND_FILENAME)
                chess.chess_trade(coin_label,btc_in_vallet,safety_margin)
                return True
            elif 'coin of the' in d['text']:
                print("Related to 'coin of the week' Text - user : ",d['user']['name'], " : ", d['text'],'\n')
                #winsound.PlaySound('alarm_enemy.wav', winsound.SND_FILENAME)

    def on_error(self, status):
        print("status: ",status)

l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

stream = Stream(auth, l)
stream.filter(track=['coin'], follow=['961445378','944708774119575552','378174881']) # put the user id into the 'follow' list



# officialmcafee === 961445378;
# karlisvigulis === 944708774119575552
# EnzoKX21 === 378174881

# ==== Twitter part(image fetch): =====
# test link:   https://t.co/niDMslc5np






