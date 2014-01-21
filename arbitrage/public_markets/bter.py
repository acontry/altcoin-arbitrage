__author__ = 'alex'

import requests
from .market import Market

#http://pubapi.cryptsy.com/api.php?method=singlemarketdata&marketid=132
class Bter(Market):
    def __init__(self):
        super(Bter, self).__init__()
        self.update_rate = 60

    def update_depth(self):
        #Dogecoin/BTC exchange URL
        url = 'https://bter.com/api/1/depth/doge_btc'
        res = requests.get(url)
        depth = res.json()
        self.depth = self.format_depth(depth)

    def sort_and_format(self, orders, reverse=False):
        orders.sort(key=lambda x: float(x[0]), reverse=reverse)
        r = []
        for i in orders:
            r.append({'price': float(i[0]), 'amount': float(i[1])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(
            depth['bids'], True)
        asks = self.sort_and_format(
            depth['asks'], False)
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = Bter()
    print(market.get_ticker())
