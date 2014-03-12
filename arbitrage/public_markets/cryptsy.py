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
        #url = 'http://pubapi.cryptsy.com/api.php?method=singleorderdata&marketid=132'
        #res = requests.get(url)
        #depth = res.json()

        depth = self.a.query("depth", {"marketid": 132})
        self.depth = self.format_depth(depth['return']['buy'], depth['return']['sell'], 0, 1)

if __name__ == "__main__":
    market = Cryptsy()
    print(market.get_ticker())
