import logging
import config
from .observer import Observer
from private_markets import mtgox
from private_markets import bitcoincentral
from .traderbot import TraderBot
import json


class MockMarket(object):
    def __init__(self, name, fee=0, s_coin_balance=0.05, p_coin_balance=50000., persistent=True):
        self.name = name
        self.filename = "traderbot-sim-" + name + ".json"
        self.s_coin_balance = s_coin_balance
        self.p_coin_balance = p_coin_balance
        self.fee = fee
        self.persistent = persistent
        if self.persistent:
            try:
                self.load()
            except IOError:
                pass

    def buy(self, volume, price):
        logging.info("[TraderBotSim] Execute buy %f %s @ %f on %s" %
                     (volume, config.p_coin, price * 10**8, self.name))
        self.s_coin_balance -= price * volume
        self.p_coin_balance += volume - volume * self.fee
        if self.persistent:
            self.save()

    def sell(self, volume, price):
        logging.info("[TraderBotSim] Execute sell %f %s @ %f on %s" %
                     (volume, config.p_coin, price*10**8, self.name))
        self.p_coin_balance -= volume
        self.s_coin_balance += price * volume - price * volume * self.fee
        if self.persistent:
            self.save()

    def load(self):
        data = json.load(open(self.filename, "r"))
        self.s_coin_balance = data[config.s_coin]
        self.p_coin_balance = data[config.p_coin]

    def save(self):
        data = {config.s_coin: self.s_coin_balance, config.p_coin: self.p_coin_balance}
        json.dump(data, open(self.filename, "w"))

    def balance_total(self, price):
        return self.s_coin_balance + self.p_coin_balance * price

    def get_balances(self):
        pass


class TraderBotSim(TraderBot):
    def __init__(self):
        self.cryptsy = MockMarket("cryptsy", 0.002)  # 0.2% fee
        self.bterdogetobtc = MockMarket("bterdogetobtc", 0.002)
        self.vircurex = MockMarket("vircurex", 0.002)
        self.clients = {
            "Cryptsy": self.cryptsy,
            "BterDOGEtoBTC": self.bterdogetobtc,
            "Vircurex": self.vircurex,
        }
        self.profit_thresh = 0  # in EUR
        self.perc_thresh = 0.6  # in %
        self.trade_wait = 120
        self.last_trade = 0

    def max_tradable_volume(self, buy_price, kask, kbid):
        # We're buying primary coins from the market with kask at buy_price
        min1 = float(self.clients[kask].s_coin_balance) * (1 - config.balance_margin) / buy_price
        # We're selling primary coins to the market with kbid
        min2 = float(self.clients[kbid].p_coin_balance) * (1 - config.balance_margin)
        return min(min1, min2)

    def total_balance(self, price):
        market_balances = [i.balance_total(
            price) for i in set(self.clients.values())]
        return sum(market_balances)

    def execute_trade(self, volume, kask, kbid, 
                      weighted_buyprice, weighted_sellprice,
                      buyprice, sellprice):
        self.clients[kask].buy(volume, buyprice)
        self.clients[kbid].sell(volume, sellprice)
        logging.info("[TraderBotSim] Profit: %f %s", (sellprice-buyprice)*volume, config.s_coin)

if __name__ == "__main__":
    t = TraderBotSim()
    print(t.total_balance(33))
