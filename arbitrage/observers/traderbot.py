import decimal
import logging
import config
import time
import concurrent.futures
from .observer import Observer
from .emailer import send_email
from private_markets import cryptsy
from private_markets import vircurex
from private_markets import bter
from private_markets import coinse


class TraderBot(Observer):
    def __init__(self):
        self.clients = {
            "Cryptsy": cryptsy.PrivateCryptsy(),
            "Vircurex": vircurex.PrivateVircurex(),
            "Bter": bter.PrivateBter()}
           # "CoinsE": coinse.PrivateCoinsE()
       # }
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
        if self.potential_trades:
            # Sort trades by profit, most profitable first
            self.potential_trades.sort(key=lambda x: x[0], reverse=True)
            # Execute only the best (more profitable)
            self.execute_trade(*self.potential_trades[0][:])

        time.sleep(1)  # Small pause to not flood API requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            for market_name, market in self.clients.items():
                executor.submit(market.update_order_status())

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

    def opportunity(self, profit, market_volume, buy_price, kask, sell_price, kbid, perc,
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

        # Calculate trade volume
        max_volume_from_balances = self.max_tradable_volume(buy_price, kask, kbid)
        trade_volume = min(market_volume, max_volume_from_balances, config.max_tx_volume)

        # Calculate new profit based on trade_volume
        buy_fee = self.clients[kask].fees["buy"]["fee"]
        sell_fee = self.clients[kbid].fees["sell"]["fee"]
        profit = trade_volume * ((1 - sell_fee)*sell_price - (1 + buy_fee)*buy_price)

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
                                      buy_price, sell_price])

    def watch_balances(self):
        pass

    def execute_trade(self, profit, volume, kask, kbid, weighted_buyprice,
                      weighted_sellprice, buyprice, sellprice):
        self.last_trade = time.time()
        logging.info(" [TraderBot] Buy @%s %f %s and sell @%s for %f %s profit",
                     kask, volume, config.p_coin, kbid, profit, config.s_coin)

        # Put in buy and sell orders at least profitable prices possible so that they have the best
        # chance of executing
        buy_fee = self.clients[kask].fees["buy"]["fee"]
        sell_fee = self.clients[kbid].fees["sell"]["fee"]
        price_diff = (sellprice * (1 - sell_fee) - buyprice * (1 - buy_fee)) / \
            (2 + buy_fee - sell_fee)
        # Round price_diff down to nearest Satoshi
        price_diff = decimal.Decimal(price_diff).quantize(decimal.Decimal('1.00000000'),
                                                          rounding=decimal.ROUND_FLOOR)
        price_diff = float(price_diff)
        buyprice_trade = buyprice + price_diff
        sellprice_trade = sellprice - price_diff
        volume = min(self.max_tradable_volume(buyprice_trade, kask, kbid), volume)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(self.clients[kask].buy, volume, buyprice_trade)
            executor.submit(self.clients[kbid].sell, volume, sellprice_trade)
