__author__ = 'alex'

import requests
from .market import Market

base_url = 'https://bter.com/api/1/depth/'


class Bter(Market):
    def __init__(self):
        super(Bter, self).__init__()
        self.update_rate = 60
        self.url = base_url + self.p_coin.lower() + '_' + self.s_coin.lower()

    def update_depth(self):
        res = requests.get(self.url)
        depth = res.json()
        self.depth = self.format_depth(depth['bids'], depth['asks'], 0, 1)

if __name__ == "__main__":
    market = Bter()
    print(market.get_ticker())
