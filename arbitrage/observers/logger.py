import logging
from .observer import Observer
import config


class Logger(Observer):
    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc,
                    weighted_buyprice, weighted_sellprice):
        logging.info("profit: %f %s with volume: %f %s - buy at %i (%s) sell at %i (%s) ~%.2f%%" %
                     (profit, config.s_coin, volume, config.p_coin, buyprice * 100000000, kask, sellprice * 100000000, kbid, perc))
