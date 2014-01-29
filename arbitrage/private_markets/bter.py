# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market, TradeException
import time
import hmac
import urllib.parse
import urllib.request
import requests
import hashlib
import config
from datetime import datetime


class PrivateBter(Market):
    url = "https://bter.com/api/1/private/"

    def __init__(self):
        super().__init__()
        self.key = config.bter_key
        self.secret = config.bter_secret
        self.min_tx_volume = 0.001
        try:
            self.get_balances()
        except Exception:
            self.s_coin_balance = 0
            self.p_coin_balance = 0

    def query(self, method, req):
        # generate POST data string
        req["nonce"] = int(time.time())
        post_data = urllib.parse.urlencode(req)
        # sign it
        sign = hmac.new(self.secret.encode("ascii"), post_data.encode("ascii"), hashlib.sha512).hexdigest()
        # extra headers for request
        headers = {"Sign": sign, "Key": self.key}
        full_url = self.url + method
        try:
            res = requests.post(full_url, data=req, headers=headers)
        except Exception as e:
            raise Exception("Error sending request to %s - %s" % (self.name, e))
        try:
            value = res.json()
        except Exception as e:
            raise Exception("Unable to decode response from %s - %s" %
                            (self.name, e))
        return value

    def _buy(self, amount, price):
        """Create a buy limit order"""
        currency_pair = self.p_coin.lower() + "_" + self.s_coin.lower()
        req = {"pair": currency_pair, "type": "BUY", "rate": price, "amount": amount}
        response = self.query("placeorder", req)
        if response["result"] != True:
            raise TradeException(response["msg"])

    def _sell(self, amount, price):
        """Create a sell limit order"""
        currency_pair = self.p_coin.lower() + "_" + self.s_coin.lower()
        req = {"pair": currency_pair, "type": "SELL", "rate": price, "amount": amount}
        response = self.query("placeorder", req)
        if response["result"] != True:
            raise TradeException(response["msg"])

    def get_balances(self):
        """Get balance of primary coin and secondary coin"""
        try:
            res = self.query("getfunds", {})
            self.p_coin_balance = float(res["available_funds"][self.p_coin])
            self.s_coin_balance = float(res["available_funds"][self.s_coin])
        except Exception:
            raise Exception("Error getting balance")
