
from .market import Market, TradeException
import time
import requests
import hashlib
import random
from collections import OrderedDict
import config
import database


class PrivateVircurex(Market):
    domain = "https://api.vircurex.com"

    def __init__(self):
        super().__init__()
        self.secrets = config.vircurex_secrets
        self.user = config.vircurex_user
        self.get_balances()

    def secure_request(self, command, params={}, params_nohash={}):
        """params is an ordered dictionary of parameters to pass. params_nohash is a dictionary of
        parameters that aren't part of the encoded request."""

        secret = self.secrets[command]
        t = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())  # UTC time
        txid = "%s-%f" % (t, random.randint(0, 1 << 31))
        txid = hashlib.sha256(txid.encode("ascii")).hexdigest()  # unique transmission ID using random hash
        # token computation - dict order matters here!
        vp = [command] + list(params.values())
        token_input = "%s;%s;%s;%s;%s" % (secret, self.user, t, txid, ';'.join(map(str, vp)))
        token = hashlib.sha256(token_input.encode("ascii")).hexdigest()
        # Building request
        reqp = {"account": self.user, "id": txid, "token": token, "timestamp": t}
        reqp.update(params)
        reqp.update(params_nohash)
        url = "%s/api/%s.json" % (self.domain, command)
        data = requests.get(url, params=reqp)
        return data.json()

    def _buy(self, amount, price):
        """Create a buy limit order"""
        params = OrderedDict((("ordertype", "BUY"), ("amount", "{:.8f}".format(amount)),
                              ("currency1", self.p_coin), ("unitprice", "{:.8f}".format(price)),
                              ("currency2", self.s_coin)))
        response = self.secure_request("create_order", params)
        if response["status"] != 0:
            raise TradeException(response["status"])
        params = {"orderid": response["orderid"]}
        response = self.secure_request("release_order", params)
        if response["status"] != 0:
            raise TradeException(response["status"])
        return response["orderid"]

    def _sell(self, amount, price):
        """Create a sell limit order"""
        params = OrderedDict((("ordertype", "SELL"), ("amount", "{:.8f}".format(amount)),
                              ("currency1", self.p_coin), ("unitprice", "{:.8f}".format(price)),
                              ("currency2", self.s_coin)))
        response = self.secure_request("create_order", params)
        if response["status"] != 0:
            raise TradeException(response["status"])
        params = {"orderid": response["orderid"]}
        response = self.secure_request("release_order", params)
        if response["status"] != 0:
            raise TradeException(response["status"])
        return response["orderid"]

    def update_order_status(self):
        if not self.open_orders:
            pass
        response = self.secure_request('read_orders', params_nohash={'otype': 1})
        received_open_orders = []
        for i in range(1, response['numberorders'] + 1):
            order_name = 'order-' + str(i)
            received_open_orders.append(response[order_name])

        remaining_open_orders = []
        completed_order_ids = []
        for open_order in self.open_orders:
            found_order = [found_order for found_order in received_open_orders if
                           found_order['orderid'] == open_order['order_id']]
            if not found_order:
                completed_order_ids.append(open_order['order_id'])
            else:
                remaining_open_orders.append(open_order)

        self.open_orders = remaining_open_orders
        database.order_completed(self.name, completed_order_ids)

    def get_balances(self):
        """Get balance"""
        try:
            res = self.secure_request("get_balances")
            self.p_coin_balance = float(res["balances"][self.p_coin]["availablebalance"])
            self.s_coin_balance = float(res["balances"][self.s_coin]["availablebalance"])

        except Exception:
            raise Exception("Error getting balance: Vircurex error %d" % res['status'])
