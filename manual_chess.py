#!/usr/bin/python

import time
import hmac
import urllib
import requests
import hashlib
import base64
import sys
import json

import ast

# IMPORTANT: remember to set the amount of BTC you want to trade.
btc_in_vallet = 0.0005757 # put the amount of BTC you want to trade.
safety_margin = 0.2

API_KEY = 'xxxx'
API_SECRET = 'xxxxx'


def api_query( method, req = None ):
    if not req:
        req = {}
    # print "def api_query( method = " + method + ", req = " + str( req ) + " ):"
    public_set = set(
        ["GetCurrencies", "GetTradePairs", "GetMarkets", "GetMarket", "GetMarketHistory", "GetMarketOrders"])
    private_set = set(
        ["GetBalance", "GetDepositAddress", "GetOpenOrders", "GetTradeHistory", "GetTransactions", "SubmitTrade",
         "CancelTrade", "SubmitTip"])
    if method in public_set:
        url = "https://www.cryptopia.co.nz/api/" + method
        if req:
            for param in req:
                url += '/' + str(param)
        r = requests.get(url)
    elif method in private_set:
        url = "https://www.cryptopia.co.nz/Api/" + method
        nonce = str(int(time.time()))
        post_data = json.dumps(req);
        m = hashlib.md5()
        m.update(post_data.encode('utf-8'))
        requestContentBase64String = base64.b64encode(m.digest()).decode('utf-8')
        signature = API_KEY + "POST" + urllib.parse.quote_plus(url).lower() + nonce + requestContentBase64String
        hmacsignature = base64.b64encode(
            hmac.new(base64.b64decode(API_SECRET), signature.encode('utf-8'), hashlib.sha256).digest())
        header_value = "amx " + API_KEY + ":" + hmacsignature.decode('utf-8') + ":" + nonce
        headers = {'Authorization': header_value, 'Content-Type': 'application/json; charset=utf-8'}
        r = requests.post(url, data=post_data, headers=headers)
    response = r.text
    #print("( Response ): " + response)
    return response.replace("false", "False").replace("true", "True").replace('":null', '":None')


with open('moves.json', 'r') as fp: # A Dictionary with all the 'BTC' trade pairs in lowercase.
    PairDict = json.load(fp)
#print(PairDict)



# The input is not case sensitive and spaces will be ignored
label = input("\n\nEnter the SYMBOL for coin of the week: ").lower().replace(' ', '') # Should get as user input or from OCR. The rest is the same for both.
TradePair = label + "/btc"
if TradePair in PairDict.values(): # Check if the coin trades on Cryptopia. Remember to update the dictionary.
    print("\n>>>>", label, "is on Cryptopia <<<<")
    tradePair_underscore = label + "_BTC"
    print(tradePair_underscore)

    prices = []
    sum = 0
    print("\nOur trade volume in BTC: ", btc_in_vallet)
    buy_price = 0
    retry_counter = 0

    print("\n============  Sell Orders: ===========") # Request for 5 sell orders from the top.
    before = time.time()
    data = ast.literal_eval(api_query("GetMarketOrders", [tradePair_underscore, 5]))["Data"]['Sell']
    order_found = False
    for order in data:
        prices.append(order["Price"])
        sum = sum + order["Total"]
        print("Price: ",f'{order["Price"]:.8f}' , ";   Sum:", sum)
        if sum > btc_in_vallet:
            # IMPORTANT: remember to set the correct margain
            buy_price = order["Price"]*safety_margin  # smallest 'buy price' with Sum(BTC) larger than we own. Add 20% margin to account for other fast BOTs.
            break
    print("======================================\n")
    after = time.time()
    print("[ DEBUG: 'Open Sell Orders' request execution time: ", after - before, "seconds ]")
    # Buy only if the buy price is less than 170% of the cheapest Sell Order.
    go_for_it = True
    while go_for_it: # Try buying until, either 'Success: true' or buy price > 170% initial, cheapst price.
        go_for_it = False
        before_trade = time.time()
        buy_amount = btc_in_vallet * 0.9979 / buy_price
        if buy_price < prices[0] * 1.7:
            #trade_response = ast.literal_eval(api_query("GetMarketOrders", [tradePair_underscore, 5]))
            print("\nTry a trade at buy price:", f'{buy_price:.8f}', "\n( The initial sell price was: ", f'{prices[0]:.8f}',")\n\n")
            print("Amount:", buy_amount)
            trade_response = ast.literal_eval(api_query("SubmitTrade", {"Market": tradePair_underscore, "Type": 'Buy', "Rate": buy_price, "Amount": buy_amount})) # Send trade request and convert response string to dictionary.
        else:
            print("The Buy price has exceeded 170% of the initial price:", prices[0])
            break
        after_trade = time.time()
        print("[ DEBUG: 'Trade' request execution time: ", after_trade - before_trade, "seconds ]")
        print(trade_response)
        if trade_response["Success"] == False and retry_counter < 5:
            go_for_it = True
            retry_counter = retry_counter+1
            time.sleep(1)
            #buy_price = buy_price*1.05 # increase the buy price by 10%
            print("[DEBUG: Trade request Failed ]")
        elif trade_response["Success"] == True:
            print("\n\n+ + + + + + + + +    Trade order opened    + + + + + + +\n")
            print(buy_amount, " BTC trading at price: ", f'{buy_price:.8f}', " for coin ", label)
            print("\n+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + +\n\n")
            if trade_response["Data"]["FilledOrders"]:
                print(">>>> TRADE COMPELETED <<<<")
            else:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!! TRADE OPEN BUT NOT COMPLETED !!!!!!!!!!!!!!!!!!!!!!!!!!")
    # TODO: Immediately retry if failed, until - either 'Success' or the buy price exceeds 170% of the initial, cheapst price.
    # TODO: Two ways to do this: FASTER - increase the buy price by a fixed rate; SLOWER: Make a new Sell order request and choose the cheapest to sell all BTC (as in the first try).
else:
    print("Coin [", label, "] does not trade on Cryptopia")









    # PairDict = {}
# for pair in data:
#     PairDict[pair["TradePairId"]] = pair["Label"].lower()
#
# with open('moves.json', 'w') as fp:
#     json.dump(PairDict, fp)
# print(PairDict)


# {"Success":True,"Message":None,"Data":{"TradePairId":100,"Label":"DOT/BTC","AskPrice":0.00000020,"BidPrice":0.00000019,"Low":0.00000019,"High":0.00000021,"Volume":1263556.65136394,"LastPrice":0.00000019,"LastVolume":774.83684404,"BuyVolume":50896673.08961847,"SellVolume":33046510.52562918,"Change":0.0},"Error":None}

# Private:
#print(api_query("GetBalance"))



# +
# print api_query("GetBalance", {'CurrencyId':2} )