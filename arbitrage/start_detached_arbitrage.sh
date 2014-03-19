script -f arbitrage.log
screen -d -m -S trader python3 ~/altcoin-arbitrage/arbitrage/arbitrage.py
screen -ls