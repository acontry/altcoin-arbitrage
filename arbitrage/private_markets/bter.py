# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market, TradeException
import time
import base64
import hmac
import urllib.parse
import requests
import hashlib
import sys
import json
import config


class PrivateBter(Market):
    url = "https://bter.com/api/1/private/"

    def __init__(self):
        super().__init__()
        self.key = config.bter_key
        self.secret = config.bter_secret
        self.get_balances()

    def query(self, method, req):
        # generate POST data string
        req["nonce"] = int(time.time())
        post_data = urllib.parse.urlencode(req)
        # sign it
        sign = hmac.new(self.secret.encode("ascii"), post_data.encode("ascii"), hashlib.sha512).hexdigest()
        # extra headers for request
        headers = {"Sign": sign, "Key": self.key}

        try:
            res = requests.post(self.url+method, data=req, headers=headers)
        except Exception as e:
            raise Exception("Error sending request to %s - %s" % (self.name, e))
        try:
            value = res.json()
        except Exception as e:
            raise Exception("Unable to decode response from %s - %s" %
                            (self.name, e))
        return value

      # get market ID (return None if not found)
    def get_market_id(self, p_coin, s_coin):
        mkt_id = 0
        try:
            res = self.query("getmarkets", {})
            for i, market in enumerate(res["return"]):
                if (market["primary_currency_code"].upper() == p_coin.upper() and
                            market["secondary_currency_code"].upper() == s_coin.upper()):
                    mkt_id = market["marketid"]
            return mkt_id
        except Exception:
            return None

    def _buy(self, amount, price):
        """Create a buy limit order"""
        params = {"marketid": self.mkt_id, "ordertype": "Buy", "quantity": amount, "price": price}
        response = self.query("createorder", params)
        if response["success"] == 0:
            raise TradeException(response["error"])

    def _sell(self, amount, price):
        """Create a sell limit order"""
        params = {"marketid": self.mkt_id, "ordertype": "Sell", "quantity": amount, "price": price}
        response = self.query("createorder", params)
        if response["success"] == 0:
            raise TradeException(response["error"])

    def get_balances(self):
        """Get balance"""
        try:
            res = self.query("getfunds", {})
            self.p_coin_balance = float(res["return"]["balances_available"][self.p_coin])
            self.s_coin_balance = float(res["return"]["balances_available"][self.s_coin])
        except Exception:
            raise Exception("Error getting balance")
