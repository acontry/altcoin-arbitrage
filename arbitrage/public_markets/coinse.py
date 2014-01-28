__author__ = 'alex'

import urllib.request
import urllib.error
import urllib.parse
import requests
import json
from .market import Market

class CoinsE(Market):
    def __init__(self):
        super(CoinsE, self).__init__()
        self.update_rate = 60

    def update_depth(self):
        #Dogecoin/BTC exchange URL
        url = 'https://www.coins-e.com/api/v2/market/DOGE_BTC/depth/'
        res = requests.get(url)
        depth = res.json()
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

        # Bid prices should be less than ask prices, so go through depths to "execute" trades and clean
        # up the bids and asks
        while bids[0]['price'] >= asks[0]['price']:
            # If bid amount is greater than ask amount, update bid volume and remove "completed" ask
            if bids[0]['amount'] > asks[0]['amount']:
                bids[0]['amount'] -= asks[0]['amount']
                asks.remove(asks[0])
            # If ask amount is greater than bid amount, do the opposite
            elif bids[0]['amount'] < asks[0]['amount']:
                asks[0]['amount'] -= bids[0]['amount']
                bids.remove(bids[0])
            # If the volumes are miraculously equal
            else:
                asks.remove(asks[0])
                bids.remove(bids[0])

        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = CoinsE()
    print(market.get_ticker())
