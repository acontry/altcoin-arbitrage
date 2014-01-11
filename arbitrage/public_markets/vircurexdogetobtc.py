__author__ = 'alex'

import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market

class VircurexDOGEtoBTC(Market):
    def __init__(self):
        super(VircurexDOGEtoBTC, self).__init__("USD")
        self.update_rate = 60

    def update_depth(self):
        url = 'https://vircurex.com/api/orderbook.json'
        price_query = [('base', 'DOGE'), ('alt', 'BTC')]
        data = urllib.parse.urlencode(price_query)
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = { 'User-Agent' : user_agent }
        full_url = url + '?' + data
        req = urllib.request.Request(full_url, None, headers)
        res = urllib.request.urlopen(req)
        depth = json.loads(res.read().decode('utf8'))
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
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = VircurexDOGEtoBTC()
    print(market.get_ticker())
