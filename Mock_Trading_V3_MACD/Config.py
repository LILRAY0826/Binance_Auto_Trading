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

    # Main function for Mock Trading
    def mock_trading(self, entry_data: list, klines_dataframe: pd.DataFrame, start_property, buy, leverage, afford_range, direction_choppy, anti_direction_choppy):

        long_position = []
        short_position = []
        position_history = pd.DataFrame(columns=["klines_open time", "klines_open_price", "klines_high_price", "klines_low_price", "klines_close_price", "space 1"
                                                 "order_entry_time", "order_entry_direction", "order_price", "order_quantity", "order_liquidation", "space 2"
                                                 "position_entry_time", "position_entry_direction", "position_price", "position_quantity", "position_liquidation"])

        # Iterate klines to simulate the market
        for index, row in klines_dataframe.iterrows():

            open_time = str(row['Open Time'])[:10]
            open_price = row['open']
            high_price = row['high']
            low_price = row['low']
            close_price = row['close']
            boolean, entry_time, entry_price, entry_direction = self.open_time_is_entry_time(open_time, entry_data)
            quantity = round((buy * leverage) / entry_price, 2)

            # Observe Exit Signal

            # Create Position
            if boolean:
                # Long Position
                if "多" in entry_direction:
                    if len(a) == 0:
                        liquidation = round(entry_price * (1 + (100 / leverage) / 100), 2)
                        long_position.append([entry_time, entry_direction, entry_price, quantity, liquidation])
                    else:
                        long_position[0][0] = entry_time
                        times = long_position[0][3] / quantity
                        long_position[0][2] = (long_position[0][2] * times + entry_price) / (times + 1)
                        long_position[0][3] += quantity
                        long_position[0][4] = round(long_position[0][2] * (1 + (100 / leverage) / 100), 2)

                # Short Position
                if "空" in entry_direction:
                    if len(a) == 0:
                        liquidation = round(entry_price * (1 - (100 / leverage) / 100), 2)
                        short_position.append([entry_time, entry_direction, entry_price, quantity, liquidation])
                    else:
                        short_position[0][0] = entry_time
                        times = short_position[0][3] / quantity
                        short_position[0][2] = (short_position[0][2] * times + entry_price) / (times + 1)
                        short_position[0][3] += quantity
                        short_position[0][4] = round(short_position[0][2] * (1 - (100 / leverage) / 100), 2)

    # About Market's information
    # Get 300 pass klines data
    def get_klines(self, start_date, end_date):

        # Get klines dataframe
        dataframe = pd.DataFrame(self.client.get_historical_klines(symbol="BTCUSDT",
                                                                   interval=Client.KLINE_INTERVAL_1DAY,
                                                                   start_str=start_date,
                                                                   end_str=end_date)).drop(columns=[5, 7, 8, 9, 10, 11])
        dataframe.columns = ['Open Time', 'open', 'high', 'low', 'close', 'Close Time']

        # Convert timestamp to datetime
        dataframe['Open Time'] = pd.to_datetime((dataframe['Open Time'] + 288e5) / 1000, unit='s')
        dataframe['Close Time'] = pd.to_datetime((dataframe['Close Time'] + 288e5) / 1000, unit='s')

        # Change Data Type in Dataframe
        for column in dataframe.columns:
            for index, item in enumerate(dataframe[column]):
                try:
                    dataframe[column][index] = round(float(item), 2)
                except:
                    pass
        dataframe.to_csv("Klines.csv")

    def get_entry_time_price(self, klines_dataframe, mock_trading_dataframe):

        entry_data = []
        for index, kind in enumerate(mock_trading_dataframe["種類"]):
            # Get Entry Time
            if "進場" in kind:
                for index_, open_time in enumerate(klines_dataframe["Open Time"]):
                    if str(mock_trading_dataframe["日期/時間"][index])[:10] == str(open_time)[:10]:
                        entry_data.append([str(open_time)[:10], float(klines_dataframe['open'][index_]), kind, index_])
                        break
                    else:
                        pass
            else:
                pass

        entry_data.reverse()
        return entry_data

    def open_time_is_entry_time(self, open_time: str, entry_data):
        open_time = int(open_time.replace("-", ""))

        for data in entry_data:
            entry_time = data[0]
            entry_price = data[1]
            entry_direction = data[2]
            entry_price_int = int(entry_price.replace("-", ""))

            if open_time == entry_price_int:
                return True, entry_time, entry_price, entry_direction
            elif open_time < entry_price_int:
                return False, entry_time, entry_price, entry_direction
            else:
                return False, entry_time, entry_price, entry_direction