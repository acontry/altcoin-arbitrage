__author__ = 'alex'

import requests
from .market import Market
from private_markets import cryptsy

class Cryptsy(Market):
    def __init__(self):
        super(Cryptsy, self).__init__()
        self.update_rate = 60
        self.fees = {"buy": {"fee": 0.002, "coin": "s_coin"}, "sell": {"fee": 0.003, "coin": "s_coin"}}
        # Hack to use private market method to update cryptsy depths
        self.a = cryptsy.PrivateCryptsy()

    def update_depth(self):
        #Dogecoin/BTC exchange URL
        #url = 'http://pubapi.cryptsy.com/api.php?method=singleorderdata&marketid=132'
        #res = requests.get(url)
        #depth = res.json()

        depth = self.a.query("depth", {"marketid": 132})
        self.depth = self.format_depth(depth)

    def sort_and_format(self, orders, reverse=False):
        orders.sort(key=lambda x: float(x[0]), reverse=reverse)
        r = []
        for i in orders:
            r.append({'price': float(i[0]), 'amount': float(i[1])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(
            depth['return']['buy'], True)
        asks = self.sort_and_format(
            depth['return']['sell'], False)

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
    market = Cryptsy()
    print(market.get_ticker())
