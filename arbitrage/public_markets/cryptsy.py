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
        self.depth = self.format_depth(depth['return']['buy'], depth['return']['sell'], 0, 1)

    def update_prices(self):
        url = 'http://pubapi.cryptsy.com/api.php?method=orderdatav2'
        res = requests.get(url)
        prices = res.json()
        self.prices = self.format_prices(prices)

    def format_prices(self, prices):
        for pair in prices['return']:
            pair_depth = prices['return'][pair]
            pair_name = (pair_depth['primarycode'], pair_depth['secondarycode'])
            pair_depth = self.format_depth(pair_depth['buyorders'],
                                           pair_depth['sellorders'], 'price', 'quantity')
            self.prices[pair_name] = {'bid': pair_depth['bids'][0]['price'],
                                      'ask': pair_depth['asks'][0]['price']}
        return self.prices


    if __name__ == "__main__":
        market = Cryptsy()
        print(market.get_ticker())
