import time
import urllib.request
import urllib.error
import urllib.parse
import requests
import config
import logging

class Market(object):
    def __init__(self):
        self.name = self.__class__.__name__
        self.p_coin = config.p_coin
        self.s_coin = config.s_coin
        self.depth = {}
        self.depth_updated = 0
        # Configurable parameters
        self.update_rate = 60
        self.fees = {"buy": {"fee": 0.002, "coin": "p_coin"}, "sell": {"fee": 0.002, "coin": "s_coin"}}

    def get_depth(self):
        # If the update rate dictates that it is time to update the market, do it
        timediff = time.time() - self.depth_updated
        if timediff > self.update_rate:
            self.ask_update_depth()
        # If the last updated time indicates that the market is expired, set the bids/asks to 0
        timediff = time.time() - self.depth_updated
        if timediff > config.market_expiration_time:
            logging.warning('Market: %s order book is expired', self.name)
            self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [
                {'price': 0, 'amount': 0}]}
        return self.depth

    def ask_update_depth(self):
        try:
            self.update_depth()
            self.depth_updated = time.time()
        except (requests.HTTPError, urllib.error.URLError) as e:
            logging.error("HTTPError, can't update market: %s" % self.name)
        except Exception as e:
            logging.error("Can't update market: %s - %s" % (self.name, str(e)))

    def get_ticker(self):
        depth = self.get_depth()
        res = {'ask': 0, 'bid': 0}
        if len(depth['asks']) > 0 and len(depth["bids"]) > 0:
            res = {'ask': depth['asks'][0],
                   'bid': depth['bids'][0]}
        return res

    ## Abstract methods
    def update_depth(self):
        pass

    def buy(self, price, amount):
        pass

    def sell(self, price, amount):
        pass
