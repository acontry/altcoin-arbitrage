__author__ = 'alex'

import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market

#http://pubapi.cryptsy.com/api.php?method=singlemarketdata&marketid=132
class CryptsyDOGEtoBTC(Market):
    def __init__(self):
        super(CryptsyDOGEtoBTC, self).__init__("USD")
        self.update_rate = 60

    def update_depth(self):
        #Dogecoin/BTC exchange URL
        url = 'http://pubapi.cryptsy.com/api.php?method=singlemarketdata&marketid=132'
        res = urllib.request.urlopen(url)
        depth = json.loads(res.read().decode('utf8'))
        self.depth = self.format_depth(depth)

    def sort_and_format(self, orders, reverse=False):
        orders.sort(key=lambda x: float(x['price']), reverse=reverse)
        r = []
        for i in orders:
            r.append({'price': float(i['price']), 'amount': float(i['quantity'])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(
            depth['return']['markets']['DOGE']['buyorders'], True)
        asks = self.sort_and_format(
            depth['return']['markets']['DOGE']['sellorders'], False)
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = CryptsyDOGEtoBTC()
    print(market.get_ticker())
