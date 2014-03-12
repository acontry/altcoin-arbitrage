__author__ = 'alex'

import requests
from .market import Market

class Vircurex(Market):
    def __init__(self):
        super(Vircurex, self).__init__()
        self.update_rate = 60

    def update_depth(self):
        url = 'https://api.vircurex.com/api/orderbook.json'
        price_query = {'base': self.p_coin, 'alt': self.s_coin}
        res = requests.get(url, data=price_query)
        depth = res.json()
        self.depth = self.format_depth(depth['bids'], depth['asks'], 0, 1)

if __name__ == "__main__":
    market = Vircurex()
    print(market.get_ticker())
