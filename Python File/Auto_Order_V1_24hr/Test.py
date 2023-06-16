from binance.client import Client
from binance.um_futures import UMFutures
import pandas as pd
import talib
import math

api_key = 'dGpm78xWKGPzgbTZntqrfaAGGWzxam7awweyHImxyTTWxa4HPPGnKZTRZbz34TNV'
api_secret = 'jTIsMOCMvGrRCmfVSLsITdcOErR7xg3IuexviGtAfdeeOiojiswEPIFS5iuRGDz5'

client = Client(api_key=api_key,
                api_secret=api_secret)
while True:
    print(client.futures_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_4HOUR, limit=1)[0][4])