# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market, TradeException
import time
import requests
import hashlib
import random
from collections import OrderedDict
import config


class PrivateVircurex(Market):
    domain = "https://api.vircurex.com"

    def __init__(self):
        super().__init__()
        self.secrets = config.vircurex_secrets
        self.user = config.vircurex_user
        self.get_balances()

    def secure_request(self, command, params):
        """params is an ordered dictionary of parameters to pass."""
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

    def get_balances(self):
        """Get balance"""
        try:
            res = self.secure_request("get_balances", {})
            self.p_coin_balance = float(res["balances"][self.p_coin]["availablebalance"])
            self.s_coin_balance = float(res["balances"][self.s_coin]["availablebalance"])

        except Exception:
            raise Exception("Error getting balance: Vircurex error %d" % res['status'])
