__author__ = 'alex'


 # This function is terrible don't use it
def triangular_arbitrage(self):
    self.prices.pop('current', None)
    self.prices.pop('last_updated', None)
    for pair1 in self.prices:
        pair1_name = pair1
        if pair1_name[1] != 'BTC':
            continue
        for pair2 in self.prices:
            if pair1 == pair2:
                continue
            pair2_name = pair2
            if pair2_name[0] == pair1_name[0]:
                trade2 = 'sell'
            elif pair2_name[1] == pair1_name[0]:
                trade2 = 'buy'
            else:
                continue
            for pair3 in self.prices:
                pair3_name = pair3
                if trade2 == 'sell':
                    if pair2_name[1] == pair3_name[0] and pair3_name[1] == 'BTC':
                        trade3 = 'sell'
                    elif pair2_name[1] == pair3_name[1] and pair3_name[0] == 'BTC':
                        trade3 = 'buy'
                    else:
                        continue
                elif trade2 == 'buy':
                    if pair2_name[0] == pair3_name[0] and pair3_name[1] == 'BTC':
                        trade3 = 'sell'
                    elif pair2_name[0] == pair3_name[1] and pair3_name[0] == 'BTC':
                        trade3 = 'buy'
                    else:
                        continue

                if trade2 == 'buy' and trade3 == 'buy':
                    profit = self.prices[pair1]['ask'] * self.prices[pair2]['ask'] * self.prices[pair3]['ask']
                elif trade2 == 'buy' and trade3 == 'sell':
                    profit = self.prices[pair1]['ask'] * self.prices[pair2]['ask'] / self.prices[pair3]['bid']
                elif trade2 == 'sell' and trade3 == 'sell':
                    profit = self.prices[pair1]['ask'] / self.prices[pair2]['bid'] / self.prices[pair3]['bid']
                elif trade2 == 'sell' and trade3 == 'buy':
                    profit = self.prices[pair1]['ask'] / self.prices[pair2]['bid'] * self.prices[pair3]['ask']

                profit = 1 / profit # Screwed up, quick fix

                if profit > 1.006:
                    print("%s -> %s -> %s profit = %f" % (pair1, pair2, pair3, profit))