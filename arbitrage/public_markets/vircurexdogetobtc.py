__author__ = 'alex'

import requests
from .market import Market

class VircurexDOGEtoBTC(Market):
    def __init__(self):
        super(VircurexDOGEtoBTC, self).__init__()
        self.update_rate = 60

    def update_depth(self):
        url = 'https://vircurex.com/api/orderbook.json'
        price_query = {'base': 'DOGE', 'alt': 'BTC'}
        res = requests.get(url, data=price_query)
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
    market = VircurexDOGEtoBTC()
    print(market.get_ticker())
