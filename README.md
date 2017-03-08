# altcoin-arbitrage - opportunity detector and automated trading

This project is based on the github project
https://github.com/maxme/bitcoin-arbitrage

The original project was designed for arbitrage between Bitcoin and US dollars/
Euros, but the focus of this project is arbitrage between coins, such as
Dogecoin and Bitcoin. It supports arbitrary pairs of currencies.

It gets order books from supported exchanges and calculates arbitrage
opportunities between each market pair. Depth of the market orderbooks is taken
into account when looking for opportunities - an important improvement since many
altcoin orderbooks are quite shallow, limiting the total trade quantity.

When an arbitrage opportunity is found the opportunity is logged and if the traderbot
is configured and enabled, orders are places and logged in a database. An example trading
scenario would be holding DOGE in Vircurex and BTC in Bter. If the DOGE/BTC price in 
Vircurex rises enough over the price at Bter to cover the bid/ask spread and trading fees,
DOGE is sold for BTC in Vircurex and and DOGE is bought from BTC in Bter, profiting from the
price imbalance. Ideally the next step would be to transfer currencies between exchanges to 
reset the process and repeat the trades if the price imbalance still exists, but automated
withdrawal isn't supported at all exchanges, plus withdrawal fees make it harder to be 
profitable.

Currently supported exchanges for data collection and trading:
 - Cryptsy (now defunct)
 - Vircurex 
 - Coins-e (now defunct)
 - Bter 

# WARNING

**Real trading bots are included. Don't put your API keys in config.py
  if you don't know what you are doing.**

# Installation And Configuration

    cp arbitrage/config.py-example arbitrage/config.py

Then edit config.py file to setup your preferences: watched markets
and observers

You need Python3 to run this program. To install on Debian, Ubuntu, or
variants of them, use:

    $ sudo apt-get install python3 python3-pip python-nose

The requests package is required. To install:

    $ pip3 install requests

# Run

To run the opportunity watcher:

    $ python3 arbitrage/arbitrage.py
    2013-03-12 03:52:14,341 [INFO] profit: 30.539722 EUR with volume: 10 BTC - buy at 29.3410 (MtGoxEUR) sell at 29.4670 (Bitcoin24EUR) ~10.41%
    2013-03-12 03:52:14,356 [INFO] profit: 66.283642 EUR with volume: 10 BTC - buy at 29.3410 (MtGoxEUR) sell at 30.0000 (BitcoinCentralEUR) ~22.59%
    2013-03-12 03:52:14,357 [INFO] profit: 31.811390 EUR with volume: 10 BTC - buy at 29.3410 (MtGoxEUR) sell at 30.0000 (IntersangoEUR) ~10.84%
    2013-03-12 03:52:45,090 [INFO] profit: 9.774324 EUR with volume: 10 BTC - buy at 35.3630 (Bitcoin24EUR) sell at 35.4300 (BitcoinCentralEUR) ~2.76%

Note, this example is real, it has happened when the blockchain
forked. MtGox is a very reactive market, price dropped significally in
1 hour, this kind of situation opens very good arbitrage
opportunities with slower exchanges.

To check your balance on an exchange (also a good way to check your accounts configuration):

    $ python3 arbitrage.py -m MtGoxEUR get-balance
    $ python3 arbitrage.py -m MtGoxEUR,MtGoxUSD,BitstampUSD get-balance

Run tests

    $ nosetests arbitrage/

# TODO

 * Tests
 * Improve documentation
 * Update order books with a WebSocket client for supported exchanges
 * Better history handling for observer "HistoryDumper" (Redis ?)
 * Move currency from one market to another
