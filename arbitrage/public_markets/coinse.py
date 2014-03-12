__author__ = 'alex'

import requests
from .market import Market

url_base = 'https://www.coins-e.com/api/v2/market/'


class CoinsE(Market):
    def __init__(self):
        super(CoinsE, self).__init__()
        self.update_rate = 60
        self.url = url_base + self.p_coin + '_' + self.s_coin + '/depth/'

    def update_depth(self):
        res = requests.get(self.url)
        depth = res.json()
        self.depth = self.format_depth(depth['marketdepth']['bids'], depth['marketdepth']['asks'], 'r', 'q')

if __name__ == "__main__":
    market = CoinsE()
    print(market.get_ticker())
