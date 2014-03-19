
from .market import Market, TradeException
import time
import hmac
import urllib.parse
import urllib.request
import requests
import hashlib
import config
import database
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

    def query(self, method, req={}):
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

    def get_open_orders(self):
        # Might not be necessary
        response = self.query('orderlist', {})
        if not response["result"]:
            raise TradeException(response["msg"])
        return response

    def _buy(self, amount, price):
        """Create a buy limit order"""
        currency_pair = self.p_coin.lower() + "_" + self.s_coin.lower()
        req = {"pair": currency_pair, "type": "BUY", "rate": price, "amount": amount}
        response = self.query("placeorder", req)
        if not response["result"]:
            raise TradeException(response["msg"])
        order_id = response['order_id']
        # Check open order list to see if the most recent open order matches this order:
        # match by price and primary coin type. If we find it output the real order id,
        # otherwise return the dummy order id returned from the order request.
        time.sleep(10)
        open_orders = self.get_open_orders()['orders']
        open_orders.sort(key=lambda x: x['id'], reverse=True)
        if open_orders and float(open_orders[0]['sell_amount']) == (price * 1000) and \
                        open_orders[0]['buy_type'] == self.p_coin:
            order_id = open_orders[0]['id']
        return order_id

    def _sell(self, amount, price):
        """Create a sell limit order"""
        currency_pair = self.p_coin.lower() + "_" + self.s_coin.lower()
        req = {"pair": currency_pair, "type": "SELL", "rate": price, "amount": amount}
        response = self.query("placeorder", req)
        if not response["result"]:
            raise TradeException(response["msg"])
        order_id = response['order_id']
        # Check open order list to see if the most recent open order matches this order:
        # match by price and primary coin type. If we find it output the real order id,
        # otherwise return the dummy order id returned from the order request.
        time.sleep(10)
        open_orders = self.get_open_orders()['orders']
        open_orders.sort(key=lambda x: x['id'], reverse=True)
        if open_orders and float(open_orders[0]['buy_amount']) == (price * 1000) and \
                        open_orders[0]['sell_type'] == self.p_coin:
            order_id = open_orders[0]['id']
        return order_id

    def update_order_status(self):
        if not self.open_orders:
            return
        response = self.query('orderlist')
        remaining_open_orders = []
        completed_order_ids = []
        for open_order in self.open_orders:
            found_order = [found_order for found_order in response['orders'] if
                           found_order['id'] == open_order['order_id']]
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
            res = self.query("getfunds")
            if self.p_coin in res["available_funds"]:
                self.p_coin_balance = float(res["available_funds"][self.p_coin])
            else:
                self.p_coin_balance = 0
            if self.s_coin in res["available_funds"]:
                self.s_coin_balance = float(res["available_funds"][self.s_coin])
            else:
                self.s_coin_balance = 0
        except Exception:
            raise Exception("Error getting balance")
