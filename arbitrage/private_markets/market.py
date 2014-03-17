# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import logging
import config
import time
import datetime
import database


class TradeException(Exception):
    pass


class Market:
    def __init__(self):
        self.name = self.__class__.__name__
        self.p_coin = config.p_coin
        self.s_coin = config.s_coin
        self.p_coin_balance = 0.0
        self.s_coin_balance = 0.0
        self.open_orders = []
        self.fees = {"buy": {"fee": 0.002, "coin": "p_coin"}, "sell": {"fee": 0.002, "coin": "s_coin"}}
        self.min_tx_volume = 0  # In secondary coin

    def __str__(self):
        return "%s: %s" % (self.name,
                           str({self.p_coin+" balance": self.p_coin_balance,
                                self.s_coin+" balance": self.s_coin_balance}))

    def buy(self, amount, price):
        """Orders are always priced in secondary coin"""
        logging.info("Buy %.8f %s at %.8f %s @%s" % (amount, self.p_coin, price,
                                                     self.s_coin, self.name))
        order_id = self._buy(amount, price)
        self.open_orders.append({'time_placed': time.time(), 'order_id': order_id})
        # Record to database
        database.place_order(order_id, self.name, datetime.datetime.now(), "buy", price, amount)

    def sell(self, amount, price):
        """Orders are always priced in secondary coin"""
        logging.info("Sell %.8f %s at %.8f %s @%s" % (amount, self.p_coin, price,
                                                      self.s_coin, self.name))
        order_id = self._sell(amount, price)
        self.open_orders.append({'time_placed': time.time(), 'order_id': order_id})
        # Record to database
        database.place_order(order_id, self.name, datetime.datetime.now(), "sell", price, amount)

    def update_order_status(self):
        pass

    def _buy(self, amount, price):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def _sell(self, amount, price):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def deposit(self):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def withdraw(self, amount, address):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def get_balances(self):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)
