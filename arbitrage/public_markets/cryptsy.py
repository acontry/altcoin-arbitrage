__author__ = 'alex'

import requests
from .market import Market
from private_markets import cryptsy

class Cryptsy(Market):
    def __init__(self):
        super(Cryptsy, self).__init__()
        self.update_rate = 60
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
        # Remove any bids/asks below a volume of 10,000
        r[:] = [d for d in r if d.get('amount') >= 10000.0]
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(
            depth['return']['buy'], True)
        asks = self.sort_and_format(
            depth['return']['sell'], False)
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = Cryptsy()
    print(market.get_ticker())
