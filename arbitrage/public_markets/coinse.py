__author__ = 'alex'

import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market

class CoinsE(Market):
    def __init__(self):
        super(CoinsE, self).__init__()
        self.update_rate = 60

    def update_depth(self):
        #Dogecoin/BTC exchange URL
        url = 'https://www.coins-e.com/api/v2/market/DOGE_BTC/depth/'
        res = urllib.request.urlopen(url)
        depth = json.loads(res.read().decode('utf8'))
        self.depth = self.format_depth(depth)

    def sort_and_format(self, orders, reverse=False):
        orders.sort(key=lambda x: float(x['r']), reverse=reverse)
        r = []
        for i in orders:
            r.append({'price': float(i['r']), 'amount': float(i['q'])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(
            depth['marketdepth']['bids'], True)
        asks = self.sort_and_format(
            depth['marketdepth']['asks'], False)

        # Only keep asks priced above bids
        asks[:] = [ask for ask in asks if ask['price'] >= bids[0]['price']]
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = CoinsE()
    print(market.get_ticker())
