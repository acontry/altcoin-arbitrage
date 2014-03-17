__author__ = 'alex'

import requests
from .market import Market


class Vircurex(Market):
    def __init__(self):
        super(Vircurex, self).__init__()
        self.update_rate = 60
        self.update_prices()
       # self.triangular_arbitrage()

    def update_depth(self):
        url = 'https://api.vircurex.com/api/orderbook.json'
        price_query = {'base': self.p_coin, 'alt': self.s_coin}
        res = requests.get(url, data=price_query)
        depth = res.json()
        self.depth = self.format_depth(depth['bids'], depth['asks'], 0, 1)

    def update_prices(self):
        url = 'https://api.vircurex.com/api/get_info_for_currency.json'
        res = requests.get(url)
        prices = res.json()
        self.prices = self.format_prices(prices)

    def format_prices(self, prices):
        prices.pop('status', None)
        for p_coin in prices:
            if p_coin == 'BTC':
                continue
            for s_coin in prices[p_coin]:
                if (s_coin, p_coin) in self.prices.keys():
                    continue
                pair_key = (p_coin, s_coin)
                bid = float(prices[p_coin][s_coin]['highest_bid'])
                ask = float(prices[p_coin][s_coin]['lowest_ask'])
                if bid != 0 and ask != 0:
                    self.prices[pair_key] = {'bid': bid, 'ask': ask}
        return self.prices


if __name__ == "__main__":
    market = Vircurex()
    print(market.get_ticker())
