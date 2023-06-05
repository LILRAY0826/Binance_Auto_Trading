from binance.client import Client
import pandas as pd
import talib
import math
import os
pd.set_option('mode.chained_assignment', None)


class Functions:

    def __init__(self, api_key: str, api_secret: str):
        super(Functions, self).__init__()
        self.client = Client(api_key, api_secret)  # Assign binance client object

    # Get 300 pass klines data
    def get_klines(self):

        # Get klines dataframe
        dataframe = pd.DataFrame(
            self.client.get_historical_klines(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1DAY, limit=300)).drop(
            columns=[5, 7, 8, 9, 10, 11])
        dataframe.columns = ['Open Time', 'open', 'high', 'low', 'close', 'Close Time']

        # Convert timestamp to datetime
        dataframe['Open Time'] = pd.to_datetime((dataframe['Open Time'] + 288e5) / 1000, unit='s')
        dataframe['Close Time'] = pd.to_datetime((dataframe['Close Time'] + 288e5) / 1000, unit='s')

        # Compute macd
        dataframe["DIF"], dataframe["DEA"], dataframe["MACD"] = talib.MACD(dataframe['close'],
                                                                           fastperiod=12,
                                                                           slowperiod=26,
                                                                           signalperiod=9)
        for column in dataframe.columns:
            for index, item in enumerate(dataframe[column]):
                try:
                    dataframe[column][index] = round(float(item), 2)
                except:
                    continue
        dataframe.to_csv("Klines.csv")

        return dataframe.iloc[-1]

    @staticmethod
    def get_direction(klines: pd.Series, txt_path="Last Time Direction.txt"):
        if klines['DIF'] - klines['DEA'] < 0:
            direction = 'short'
        else:
            direction = 'long'

        if os.path.exists(txt_path):
            with open(txt_path, 'r') as w:
                last_direction = w.read()
        else:
            last_direction = None

        with open(txt_path, 'w+') as w:
            w.write(direction)

        return last_direction, direction
