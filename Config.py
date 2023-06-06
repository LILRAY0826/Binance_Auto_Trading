from binance.client import Client
from binance.um_futures import UMFutures
from datetime import datetime
import pandas as pd
import math
import time
import os
pd.set_option('mode.chained_assignment', None)


class Functions:

    def __init__(self, api_key: str, api_secret: str):
        super(Functions, self).__init__()
        self.client = Client(api_key, api_secret)  # Assign binance client object
        self.futures_client = UMFutures()  # Assign Futures object

        # Check the margin and leverage is correct
        try:
            self.client.futures_change_margin_type(symbol='BTCUSDT', marginType='ISOLATED')
        except:
            pass

    def auto_order(self, last_direction: str, direction: str, buy: float, leverage: int, direction_choppy: float, anti_direction_choppy: float, afford_range: float):
        if last_direction != direction and self.get_margins() > buy:

            # How many quantity would be ordered.
            quantity = self.get_quantity(buy=buy, leverage=leverage)

            # Create Position
            self.set_order(leverage=leverage,
                           direction=direction,
                           quantity=quantity,
                           direction_choppy=direction_choppy,
                           anti_direction_choppy=anti_direction_choppy)
            time.sleep(0.5)
            self.set_profit_stop(afford_range=afford_range)
            print("Create New Position : " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        else:
            self.set_profit_stop(afford_range=afford_range)

    # About Market's information
    # Get 300 pass klines data
    def get_klines(self):

        # Get klines dataframe
        dataframe = pd.DataFrame(
            self.client.get_historical_klines(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1DAY,
                                              limit=300)).drop(
            columns=[5, 7, 8, 9, 10, 11])
        dataframe.columns = ['Open Time', 'open', 'high', 'low', 'close', 'Close Time']

        # Convert timestamp to datetime
        dataframe['Open Time'] = pd.to_datetime((dataframe['Open Time'] + 288e5) / 1000, unit='s')
        dataframe['Close Time'] = pd.to_datetime((dataframe['Close Time'] + 288e5) / 1000, unit='s')

        # Compute dif and dea
        dif = dataframe['close'].ewm(span=12, adjust=False, min_periods=12).mean() - dataframe['close'].ewm(span=26,
                                                                                                            adjust=False,
                                                                                                            min_periods=26).mean()
        dea = dif.ewm(span=9, adjust=False, min_periods=9).mean()

        # Compute macd
        macd = dif - dea

        # Add all of our new values for the MACD to the dataframe
        dataframe['DIF'] = dataframe.index.map(dif)
        dataframe['DEA'] = dataframe.index.map(dea)
        dataframe['MACD'] = dataframe.index.map(macd)

        for column in dataframe.columns:
            for index, item in enumerate(dataframe[column]):
                try:
                    dataframe[column][index] = round(float(item), 2)
                except:
                    continue
        dataframe.to_csv("Klines.csv")

        return dataframe.iloc[-1]

    def get_quantity(self, buy: float, leverage: int):
        return round(((buy / (float(self.futures_client.ticker_price("BTCUSDT")['price']))) * leverage), 3)

    # About Account's Information Function
    # Get Available property
    def get_margins(self):
        return math.floor(float(self.client.futures_account()['availableBalance']) * 100) / 100

    # About Order Trading Function
    # Set Order
    def set_order(self, leverage, direction, quantity, direction_choppy, anti_direction_choppy):
        self.client.futures_change_leverage(symbol='BTCUSDT', leverage=leverage)
        # Create Long order
        if direction == "LONG":
            for index, info in enumerate(self.client.futures_position_information()):
                if info['symbol'] == 'BTCUSDT' and info['positionSide'] == 'LONG':
                    entry_price = round(float(info['entryPrice']), 2)
                    # Avoid Choppy trend
                    if entry_price - anti_direction_choppy < float(self.futures_client.ticker_price("BTCUSDT")['price']) < entry_price + direction_choppy:
                        pass
                    else:
                        self.client.futures_create_order(symbol='BTCUSDT',
                                                         side='BUY',
                                                         type='MARKET',
                                                         positionSide=direction,
                                                         quantity=quantity)

        # Create Short order
        elif direction == "SHORT":
            for index, info in enumerate(self.client.futures_position_information()):
                if info['symbol'] == 'BTCUSDT' and info['positionSide'] == 'SHORT':
                    entry_price = round(float(info['entryPrice']), 2)
                    # Avoid Choppy trend
                    if entry_price - direction_choppy < float(self.futures_client.ticker_price("BTCUSDT")['price']) < entry_price + anti_direction_choppy:
                        pass
                    else:
                        self.client.futures_create_order(symbol='BTCUSDT',
                                                         side='SELL',
                                                         type='MARKET',
                                                         positionSide=direction,
                                                         quantity=quantity)

    # Set Profit Stop Limit Order
    def set_profit_stop(self, afford_range):

        self.client.futures_cancel_all_open_orders(symbol='BTCUSDT')
        # Set Short Profit Stop Order
        for index, info in enumerate(self.client.futures_position_information()):
            if info['symbol'] == 'BTCUSDT' and info['positionSide'] == 'SHORT':

                loss_price = round(float(info['liquidationPrice']), 2)
                entry_price = round(float(info['entryPrice']), 2)
                quantity = round(float(info['positionAmt']), 3)

                if abs(quantity) > 0:

                    self.client.futures_create_order(symbol='BTCUSDT',
                                                     side='BUY',
                                                     type='TAKE_PROFIT_MARKET',
                                                     positionSide='SHORT',
                                                     quantity=abs(quantity),
                                                     stopPrice=entry_price - afford_range)

                    self.client.futures_create_order(symbol='BTCUSDT',
                                                     side='BUY',
                                                     type='STOP_MARKET',
                                                     positionSide='SHORT',
                                                     quantity=abs(quantity),
                                                     stopPrice=loss_price - 20)
                break

        # Set Long Profit Stop Order
        for index, info in enumerate(self.client.futures_position_information()):
            if info['symbol'] == 'BTCUSDT' and info['positionSide'] == 'LONG':

                loss_price = round(float(info['liquidationPrice']), 2)
                entry_price = round(float(info['entryPrice']), 2)
                quantity = round(float(info['positionAmt']), 3)

                if abs(quantity) > 0:
                    self.client.futures_create_order(symbol='BTCUSDT',
                                                     side='SELL',
                                                     type='TAKE_PROFIT_MARKET',
                                                     positionSide='LONG',
                                                     quantity=abs(quantity),
                                                     stopPrice=entry_price + afford_range)

                    self.client.futures_create_order(symbol='BTCUSDT',
                                                     side='SELL',
                                                     type='STOP_MARKET',
                                                     positionSide='LONG',
                                                     quantity=abs(quantity),
                                                     stopPrice=loss_price + 20)
                break

    @staticmethod
    def get_direction(klines: pd.Series, txt_path="Last Time Direction.txt"):
        if klines['DIF'] - klines['DEA'] < 0:
            direction = 'short'
        else:
            direction = 'long'

        if os.path.exists(txt_path):
            with open(txt_path, 'r') as w:
                for line in w.readlines():
                    last_direction = line.strip()
        else:
            last_direction = None

        with open(txt_path, 'w+') as w:
            w.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            w.write(direction)

        return last_direction, direction
