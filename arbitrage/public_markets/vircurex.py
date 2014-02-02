__author__ = 'alex'

import requests
from .market import Market

class Vircurex(Market):
    def __init__(self):
        super(Vircurex, self).__init__()
        self.update_rate = 60

    def update_depth(self):
        url = 'https://api.vircurex.com/api/orderbook.json'
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
    market = Vircurex()
    print(market.get_ticker())
