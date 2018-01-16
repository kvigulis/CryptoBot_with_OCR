import winsound
import time
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json


consumer_key = 'xxx'
consumer_secret = 'xxxx'
access_token = 'xxxxx'
access_token_secret = 'xxxx'


class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        d = json.loads(data)

        if list(d.keys())[0]== 'created_at':

            if d['user']['screen_name'] == 'officialmcafee' and d["in_reply_to_screen_name"] == None \
                    and d['is_quote_status'] == False:
                print("Text: ", d['text'])
                #print("Data: ", d)
                winsound.PlaySound('alarm_sound2.wav', winsound.SND_FILENAME)
                return True
            elif 'coin of the' in d['text']:
                print("Related to 'coin of the day' Text - user : ",d['user']['name'], " : ", d['text'],'\n')
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
