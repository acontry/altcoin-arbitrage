__author__ = 'alex'

import requests
from .market import Market

#http://pubapi.cryptsy.com/api.php?method=singlemarketdata&marketid=132
class Cryptsy(Market):
    def __init__(self):
        super(Cryptsy, self).__init__()
        self.update_rate = 60

    def update_depth(self):
        #Dogecoin/BTC exchange URL
        url = 'http://pubapi.cryptsy.com/api.php?method=singleorderdata&marketid=132'
        res = requests.get(url)
        depth = res.json()
        self.depth = self.format_depth(depth)

    def sort_and_format(self, orders, reverse=False):
        orders.sort(key=lambda x: float(x['price']), reverse=reverse)
        r = []
        for i in orders:
            r.append({'price': float(i['price']), 'amount': float(i['quantity'])})
        r[:] = [d for d in r if d.get('amount') >= 10.0]
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(
            depth['return']['DOGE']['buyorders'], True)
        asks = self.sort_and_format(
            depth['return']['DOGE']['sellorders'], False)
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = Cryptsy()
    print(market.get_ticker())
