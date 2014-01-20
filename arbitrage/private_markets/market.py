# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import logging
import config

class TradeException(Exception):
    pass

class Market:
    def __init__(self):
        self.name = self.__class__.__name__
        self.p_coin = config.p_coin
        self.s_coin = config.s_coin
        self.p_coin_balance = 0.0
        self.s_coin_balance = 0.0

    def __str__(self):
        return "%s: %s" % (self.name,
                           str({self.p_coin+" balance": self.p_coin_balance,
                                self.s_coin+" balance": self.s_coin_balance}))

    def buy(self, amount, price):
        """Orders are always priced in secondary coin"""
        logging.info("Buy %.8f %s at %.8f %s @%s" % (amount, self.p_coin, price,
                                                 self.s_coin, self.name))
        self._buy(amount, price)


    def sell(self, amount, price):
        """Orders are always priced in secondary coin"""
        logging.info("Sell %.8f %s at %.8f %s @%s" % (amount, self.p_coin, price,
                                                  self.s_coin, self.name))
        self._sell(amount, price)

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
