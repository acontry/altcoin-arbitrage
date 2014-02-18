# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market, TradeException
import time
import hmac
import urllib.parse
import requests
import hashlib
import config


class PrivateCoinsE(Market):
    api_url = "https://www.coins-e.com/api/v2/"

    def __init__(self):
        super().__init__()
        self.key = config.coinse_key
        self.secret = config.coinse_secret
        self.fees = {"buy": {"fee": 0.002, "coin": "s_coin"}, "sell": {"fee": 0.002, "coin": "p_coin"}}
        self.get_balances()

    def query(self, method_url, req):
        url = self.api_url + method_url
        # generate POST data string
        req["nonce"] = int(1000 * time.time())
        post_data = urllib.parse.urlencode(req)
        # sign it
        sign = hmac.new(self.secret.encode("ascii"), post_data.encode("ascii"), hashlib.sha512).hexdigest()
        # extra headers for request
        headers = {"Sign": sign, "Key": self.key}

        try:
            res = requests.post(url, data=req, headers=headers)
        except Exception as e:
            raise Exception("Error sending request to %s - %s" % (self.name, e))
        try:
            value = res.json()
        except Exception as e:
            raise Exception("Unable to decode response from %s - %s" %
                            (self.name, e))
        return value

    def _place_order(self, amount, price, type):
        """Place a buy/sell order. type should be buy or sell."""
        url = "market/" + self.p_coin + "_" + self.s_coin + "/"
        params = {"method": "neworder", "order_type": type, "rate": price, "quantity": amount}
        return self.query(url, params)

    def _buy(self, amount, price):
        """Create a buy limit order"""
        response = self._place_order(amount, price, "buy")
        if response["status"] != "true":
            raise TradeException(response["error"])
        return response["order"]["id"]

    def _sell(self, amount, price):
        """Create a sell limit order"""
        response = self._place_order(amount, price, "sell")
        if response["status"] != "true":
            raise TradeException(response["error"])
        return response["order"]["id"]

    def get_balances(self):
        """Get balance of primary coin and secondary coin"""
        try:
            req = {"method": "getwallets"}
            res = self.query("wallet/all/", req)
            self.p_coin_balance = float(res["wallets"][self.p_coin]["a"])
            self.s_coin_balance = float(res["wallets"][self.s_coin]["a"])
        except Exception:
            raise Exception("Error getting balance")
