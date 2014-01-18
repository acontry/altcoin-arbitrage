# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market, TradeException
import time
import hmac
import urllib.parse
import urllib.request
import requests
import hashlib
import random
from collections import OrderedDict
import json
import config


class PrivateVircurex(Market):
    domain = "https://vircurex.com"

    def __init__(self):
        super().__init__()
        self.secrets = config.vircurex_secrets
        self.user = config.vircurex_user
        self.get_info()

    #OLD
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

    def secure_request(self, command, params):
        """params is an ordered dictionary of parameters to pass."""
        secret = self.secrets[command]
        t = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())  # UTC time
        txid = "%s-%f" % (t, random.randint(0, 1 << 31))
        txid = hashlib.sha256(txid.encode("ascii")).hexdigest()  # unique transmission ID using random hash
        # token computation
        vp = [command] + list(params.keys())
        token_input = "%s;%s;%s;%s;%s" % (secret, self.user, t, txid, ';'.join(map(str, vp)))
        token = hashlib.sha256(token_input.encode("ascii")).hexdigest()
        # cbuilding request
        reqp = {"account": self.user, "id": txid, "token": token, "timestamp": t}
        reqp.update(params)
        url = "%s/api/%s.json?%s" % (self.domain, command, urllib.parse.urlencode(reqp))  # url
        data = urllib.request.urlopen(url).read()
        return json.loads(data)

    #TODO
    def _buy(self, amount, price):
        """Create a buy limit order"""
        params = {"marketid": self.mkt_id, "ordertype": "Buy", "quantity": amount, "price": price}
        response = self.query("createorder", params)
        if response["success"] == 0:
            raise TradeException(response["error"])

    #TODO
    def _sell(self, amount, price):
        """Create a sell limit order"""
        params = {"marketid": self.mkt_id, "ordertype": "Sell", "quantity": amount, "price": price}
        response = self.query("createorder", params)
        if response["success"] == 0:
            raise TradeException(response["error"])

    #TODO
    def get_info(self):
        """Get balance"""
        try:
            res = self.secure_request("get_balances", {})
            self.p_coin_balance = float(res["return"]["balances_available"][self.p_coin])
            self.s_coin_balance = float(res["return"]["balances_available"][self.s_coin])
        except Exception:
            raise Exception("Error getting balance")
