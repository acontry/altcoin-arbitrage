import time
import requests
import config
import logging


class Market(object):
    def __init__(self):
        self.name = self.__class__.__name__
        self.p_coin = config.p_coin
        self.s_coin = config.s_coin
        self.depth = {'asks': [], 'bids': [], 'last_updated': 0}
        self.prices = self.get_all_prices()
        # Configurable parameters
        self.update_rate = 60
        self.fees = {"buy": {"fee": 0.002, "coin": "p_coin"}, "sell": {"fee": 0.002, "coin": "s_coin"}}

    def get_depth(self):
        # If the update rate dictates that it is time to update the market, do it
        timediff = time.time() - self.depth['last_updated']
        if timediff > self.update_rate:
            try:
                self.update_depth()
                self.depth['last_updated'] = time.time()
                self.depth['current'] = True
            except requests.HTTPError:
                logging.error("HTTPError, can't update market: %s" % self.name)
            except Exception as e:
                logging.error("Can't update market: %s - %s" % (self.name, str(e)))
        # If the market is expired, mark it as such
        timediff = time.time() - self.depth['last_updated']
        if timediff > config.market_expiration_time:
            logging.warning('Market: %s order book is expired', self.name)
            self.depth['current'] = False
        return self.depth

    def get_all_prices(self):
        """Get bid/ask prices for all currencies from market"""
        timediff = time.time() - self.prices['last_updated']
        if timediff > self.update_rate:
            try:
                self.update_prices()
                self.prices['last_updated'] = time.time()
                self.prices['current'] = True
            except requests.HTTPError:
                logging.error("HTTPError, can't update market: %s" % self.name)
            except Exception as e:
                logging.error("Can't update market: %s - %s" % (self.name, str(e)))
        # If market is expired, mark it as such
        timediff = time.time() - self.prices['last_updated']
        if timediff > config.market_expiration_time:
            logging.warning('Market: %s order book is expired', self.name)
            self.prices['current'] = False
        return self.prices

    def get_ticker(self):
        """Returns bid/ask prices from depth"""
        res = {'ask': 0, 'bid': 0}
        if len(self.depth['asks']) > 0 and len(self.depth['bids']) > 0:
            res = {'ask': self.depth['asks'][0],
                   'bid': self.depth['bids'][0]}
        return res

    def format_depth(self, bids, asks, price_idx, amount_idx):
        bids = self.sort_and_format(bids, price_idx, amount_idx, True)
        asks = self.sort_and_format(asks, price_idx, amount_idx, False)

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

    @staticmethod
    def sort_and_format(orders, price_idx, amount_idx, reverse=False):
        orders.sort(key=lambda x: float(x[price_idx]), reverse=reverse)
        r = []
        for i in orders:
            r.append({'price': float(i[price_idx]), 'amount': float(i[amount_idx])})
        return r

    ## Abstract methods
    def update_depth(self):
        pass

    def update_prices(self):
        pass

    def buy(self, price, amount):
        pass

    def sell(self, price, amount):
        pass
