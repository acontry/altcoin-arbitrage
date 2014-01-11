import logging
from .observer import Observer


class Logger(Observer):
    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc,
                    weighted_buyprice, weighted_sellprice):
        logging.info("profit: %f USD with volume: %f BTC - buy at %i (%s) sell at %i (%s) ~%.2f%%" %
                     (profit, volume, buyprice * 100000000, kask, sellprice * 100000000, kbid, perc))
