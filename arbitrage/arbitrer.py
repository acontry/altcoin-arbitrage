# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import public_markets
import observers
import config
import time
import logging
import json
from concurrent.futures import ThreadPoolExecutor, wait


class Arbitrer(object):
    def __init__(self):
        self.markets = []
        self.observers = []
        self.depths = {}
        self.observer_names = config.observers
        self.init_markets(config.markets)
        self.init_observers()
        self.threadpool = ThreadPoolExecutor(max_workers=10)

    def init_markets(self, markets):
        """Initialize markets by importing public market classes."""
        self.market_names = markets
        for market_name in markets:
            exec('import public_markets.' + market_name.lower())
            market = eval('public_markets.' + market_name.lower() + '.' +
                          market_name + '()')
            self.markets.append(market)

    def init_observers(self):
        """Initialize observers by importing observer classes."""
        for observer_name in self.observer_names:
            exec('import observers.' + observer_name.lower())
            observer = eval('observers.' + observer_name.lower() + '.' +
                            observer_name + '()')
            self.observers.append(observer)

    def check_opportunity(self, kask, kbid):
        """Replacement for arbitrage_depth_opportunity machinery. Returns the
        profit, volume, buy price, sell price, weighted buy/sell prices for a
        potential arbitrage opportunity. Only considers the best bid/ask prices
        and does not go into the depth like the more complicated method."""
        buy_price = self.depths[kask]["asks"][0]["price"]
        sell_price = self.depths[kbid]["bids"][0]["price"]

        ask_vol = self.depths[kask]["asks"][0]["amount"]
        bid_vol = self.depths[kbid]["bids"][0]["amount"]

        trade_vol = min(ask_vol, bid_vol, config.max_tx_volume)
        profit = (sell_price - buy_price) * trade_vol

        # Set weighted prices to the same as prices
        return profit, trade_vol, buy_price, sell_price, buy_price, sell_price

    def arbitrage_opportunity(self, kask, ask, kbid, bid):
        """Calculates arbitrage opportunity for specified bid and ask, and
        presents this opportunity to all observers.

        Keyword arguments:
        kask -- market in depths that contains the relevant asks
        ask  -- lowest ask (in dict form along with amount)
        kbid -- market in depths that contains the relevant bids
        bid  -- highest bid (in dict form along with amount)

        """
        perc = (bid["price"] - ask["price"]) / bid["price"] * 100
        profit, volume, buyprice, sellprice, weighted_buyprice, \
        weighted_sellprice = self.check_opportunity(kask, kbid)
        if volume == 0 or buyprice == 0:
            return
        perc2 = (1 - (volume - (profit / buyprice)) / volume) * 100
        for observer in self.observers:
            observer.opportunity(
                profit, volume, buyprice, kask, sellprice, kbid,
                perc2, weighted_buyprice, weighted_sellprice)

    def __get_market_depth(self, market, depths):
        depths[market.name] = market.get_depth()

    def update_depths(self):
        depths = {}
        futures = []
        for market in self.markets:
            futures.append(self.threadpool.submit(self.__get_market_depth,
                                                  market, depths))
        wait(futures, timeout=20)
        return depths

    def tickers(self):
        """Update markets and print tickers to verbose log."""
        for market in self.markets:
            logging.verbose("ticker: " + market.name + " - " + str(
                market.get_ticker()))

    def replay_history(self, directory):
        import os
        import json
        import pprint

        files = os.listdir(directory)
        files.sort()
        for f in files:
            depths = json.load(open(directory + '/' + f, 'r'))
            self.depths = {}
            for market in self.market_names:
                if market in depths:
                    self.depths[market] = depths[market]
            self.tick()

    def tick(self):
        for observer in self.observers:
            observer.begin_opportunity_finder(self.depths)

        # Iterate over all combinations of different markets
        for kmarket1 in self.depths:
            for kmarket2 in self.depths:
                if kmarket1 == kmarket2:  # same market
                    continue
                # Check that respective markets contain bids and asks.
                market1 = self.depths[kmarket1]
                market2 = self.depths[kmarket2]
                if market1["asks"] and market2["bids"] \
                        and len(market1["asks"]) > 0 \
                        and len(market2["bids"]) > 0:
                    # Check that market pair presents a possible arbitrage
                    # opportunity, and check it in detail if it does.
                    if float(market1["asks"][0]['price']) \
                            < float(market2["bids"][0]['price']):
                        self.arbitrage_opportunity(kmarket1, market1["asks"][0],
                                                   kmarket2, market2["bids"][0])

        for observer in self.observers:
            observer.end_opportunity_finder()

    def loop(self):
        """Main loop."""
        while True:
            self.depths = self.update_depths()
            self.tickers()
            self.tick()
            time.sleep(config.refresh_rate)
