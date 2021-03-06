# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market, TradeException
import time
import hmac
import urllib.parse
import requests
import hashlib
import config
import database


class PrivateCryptsy(Market):
    url = "https://api.cryptsy.com/api"

    def __init__(self):
        super().__init__()
        self.key = config.cryptsy_key
        self.secret = config.cryptsy_secret
        self.mkt_id = self.get_market_id(self.p_coin, self.s_coin)
        self.fees = {"buy": {"fee": 0.002, "coin": "s_coin"}, "sell": {"fee": 0.003, "coin": "s_coin"}}
        self.get_balances()

    def query(self, method, req):
        # generate POST data string
        req["method"] = method
        req["nonce"] = int(time.time())
        post_data = urllib.parse.urlencode(req)
        # sign it
        sign = hmac.new(self.secret.encode("ascii"), post_data.encode("ascii"), hashlib.sha512).hexdigest()
        # extra headers for request
        headers = {"Sign": sign, "Key": self.key}

        try:
            res = requests.post(self.url, data=req, headers=headers)
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
        return response["orderid"]

    def _sell(self, amount, price):
        """Create a sell limit order"""
        params = {"marketid": self.mkt_id, "ordertype": "Sell", "quantity": amount, "price": price}
        response = self.query("createorder", params)
        if response["success"] == 0:
            raise TradeException(response["error"])
        return response["orderid"]

    def update_order_status(self):
        """Updates the status of open orders. First queries for list of open orders. If orders aren't
        found there, query the list of recent trades to match to the order to confirm that it is
        completed."""
        if not self.open_orders:
            return
        params = {'marketid': self.mkt_id}
        response = self.query('myorders', params)

        remaining_open_orders = []
        completed_order_ids = []
        for open_order in self.open_orders:
            found_order = [found_order for found_order in response['return'] if
                           found_order['orderid'] == open_order['order_id']]
            if not found_order:
                completed_order_ids.append(open_order['order_id'])
            else:
                remaining_open_orders.append(open_order)

        if completed_order_ids:
            self.open_orders = remaining_open_orders
            database.order_completed(self.name, completed_order_ids)

    def get_balances(self):
        """Get balance of primary coin and secondary coin"""
        try:
            res = self.query("getinfo", {})
            self.p_coin_balance = float(res["return"]["balances_available"][self.p_coin])
            self.s_coin_balance = float(res["return"]["balances_available"][self.s_coin])
        except Exception:
            raise Exception("Error getting balance")
