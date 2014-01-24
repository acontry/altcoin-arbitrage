import logging
import config
import time
from .observer import Observer
from .emailer import send_email
from private_markets import cryptsy
from private_markets import vircurex
from private_markets import bter
import concurrent.futures

class TraderBot(Observer):
    def __init__(self):
        self.clients = {
            "Cryptsy": cryptsy.PrivateCryptsy(),
            "Vircurex": vircurex.PrivateVircurex(),
            "Bter": bter.PrivateBter()
        }
        self.trade_wait = 120  # in seconds
        self.last_trade = 0
        self.potential_trades = []

    def begin_opportunity_finder(self, depths):
        """Begin with no potential trades and update market balances."""
        self.potential_trades = []
        self.update_balances()

    def end_opportunity_finder(self):
        """Sort potential trades by profit, then execute the most profitable
        one."""
        if not self.potential_trades:
            return
        # Sort trades by profit, most profitable first
        self.potential_trades.sort(key=lambda x: x[0], reverse=True)
        # Execute only the best (more profitable)
        self.execute_trade(*self.potential_trades[0][1:])

    def max_tradable_volume(self, buy_price, kask, kbid):
        # We're buying primary coins from the market with kask at buy_price
        min1 = float(self.clients[kask].s_coin_balance) * (1 - config.balance_margin) / buy_price
        # We're selling primary coins to the market with kbid
        min2 = float(self.clients[kbid].p_coin_balance) * (1 - config.balance_margin)
        return min(min1, min2)

    def update_balances(self):
        for client in self.clients:
            try:
                self.clients[client].get_balances()
            except:
                self.clients[client].p_coin_balance = 0
                self.clients[client].s_coin_balance = 0

    def opportunity(self, profit, market_volume, buyprice, kask, sellprice, kbid, perc,
                    weighted_buyprice, weighted_sellprice):
        if profit < config.profit_thresh or perc < config.perc_thresh:
            logging.verbose("[TraderBot] Profit or profit percentage lower than"
                            " thresholds")
            return
        if kask not in self.clients:
            logging.warning("[TraderBot] Can't automate this trade, client not"
                            " available: %s", kask)
            return
        if kbid not in self.clients:
            logging.warning("[TraderBot] Can't automate this trade, client not"
                            " available: %s", kbid)
            return

        # Used to update client balance here, now do it in begin_opportunity_finder()

        max_volume_from_balances = self.max_tradable_volume(buyprice, kask, kbid)
        trade_volume = min(market_volume, max_volume_from_balances, config.max_tx_volume)
        if trade_volume < config.min_tx_volume:
            logging.verbose("[TraderBot] Can't automate this trade, minimum volume "
                            "transaction not reached %f/%f" % (trade_volume, config.min_tx_volume))
            logging.verbose("[TraderBot] Balance on %s: %.8f %s - Balance on %s: %f %s" %
                            (kask, self.clients[kask].s_coin_balance, config.s_coin, kbid,
                            self.clients[kbid].p_coin_balance, config.p_coin))
            return
        current_time = time.time()
        if current_time - self.last_trade < self.trade_wait:
            logging.verbose("[TraderBot] Can't automate this trade, last trade"
                            " occurred %.2f seconds ago" % (current_time - self.last_trade))
            return
        self.potential_trades.append([profit, trade_volume, kask, kbid,
                                      weighted_buyprice, weighted_sellprice,
                                      buyprice, sellprice])

    def watch_balances(self):
        pass

    def execute_trade(self, volume, kask, kbid, weighted_buyprice,
                      weighted_sellprice, buyprice, sellprice):
        self.last_trade = time.time()
        logging.info(" [TraderBot] Buy @%s %f %s and sell @%s for %f %s profit",
                     kask, volume, config.p_coin, kbid, (sellprice-buyprice)*volume, config.s_coin)
        #self.clients[kask].buy(volume, buyprice)
        #self.clients[kbid].sell(volume, sellprice)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(self.clients[kask].buy, volume, buyprice)
            executor.submit(self.clients[kbid].sell, volume, sellprice)
