from binance.client import Client
from binance.um_futures import UMFutures
from datetime import datetime
from tqdm import tqdm
import pandas_ta as pta
import pandas as pd
import time
pd.set_option('mode.chained_assignment', None)


class Functions:

    def __init__(self, api_key: str, api_secret: str):
        super(Functions, self).__init__()
        self.client = Client(api_key, api_secret)  # Assign binance client object
        self.futures_client = UMFutures()  # Assign Futures object
        self.entry_data = []
        self.kline_dataframe = pd.DataFrame()
        self.position_history = pd.DataFrame()
        self.BBL_name = ""
        self.BBM_name = ""
        self.BBU_name = ""
        self.initial_buy = 0

    def get_klines(self, start_date, end_date, interval, ema, std):

        # Get klines dataframe
        if interval == "1hr":
            interval = Client.KLINE_INTERVAL_1HOUR
        elif interval == "4hr":
            interval = Client.KLINE_INTERVAL_4HOUR
        elif interval == "1day":
            interval = Client.KLINE_INTERVAL_1DAY
        elif interval == "30m":
            interval = Client.KLINE_INTERVAL_30MINUTE
        self.kline_dataframe = pd.DataFrame(self.client.get_historical_klines(symbol="BTCUSDT",
                                                                   interval=interval,
                                                                   start_str="1 Jan, 2015",
                                                                   end_str=end_date)).drop(columns=[5, 7, 8, 9, 10, 11])
        self.kline_dataframe.columns = ['Open Time', 'open', 'high', 'low', 'close', 'Close Time']

        # Convert timestamp to datetime
        self.kline_dataframe['Open Time'] = pd.to_datetime((self.kline_dataframe['Open Time']) / 1000, unit='s')
        self.kline_dataframe['Close Time'] = pd.to_datetime((self.kline_dataframe['Close Time']) / 1000, unit='s')  # 288e5

        # self.kline_dataframe['EMA'] = self.kline_dataframe['open'].ewm(span=ema, adjust=False, min_periods=ema).mean()
        self.kline_dataframe['RSI'] = pta.rsi(self.kline_dataframe['open'], length=12)

        try:
            self.kline_dataframe['Open Time'] = pd.to_datetime(self.kline_dataframe['Open Time'], format="%Y-%m-%d")
        except Exception:
            self.kline_dataframe['Open Time'] = pd.to_datetime(self.kline_dataframe['Open Time'], format="%Y-%m-%d %H:%M:%S")

        # Change Data Type in Dataframe
        for column in self.kline_dataframe.columns:
            for index, item in enumerate(self.kline_dataframe[column]):
                try:
                    self.kline_dataframe[column][index] = round(float(item), 2)
                except:
                    pass

        bbands_dataframe = pta.bbands(self.kline_dataframe['open'], length=ema, std=std)
        self.kline_dataframe = pd.concat([self.kline_dataframe, bbands_dataframe], axis=1)
        self.BBL_name = "BBL_" + str(ema) + "_" + str(std)
        self.BBM_name = "BBM_" + str(ema) + "_" + str(std)
        self.BBU_name = "BBU_" + str(ema) + "_" + str(std)

        start_date = pd.to_datetime(start_date, format="%Y-%m-%d %H:%M:%S")
        for index, open_time in enumerate(self.kline_dataframe['Open Time']):
            if start_date == open_time:
                self.kline_dataframe = self.kline_dataframe.iloc[index:].reset_index()
                break

        self.kline_dataframe.to_csv("Klines.csv", encoding="utf_8_sig")

    def get_entry_time_price(self, mock_trading_dataframe):

        self.entry_data = []

        process = tqdm(total=len(mock_trading_dataframe))
        for index, kind in enumerate(mock_trading_dataframe["種類"]):
            process.update(1)
            # Get Entry Time
            if "進場" in kind:
                for index_, open_time in enumerate(self.kline_dataframe["Open Time"]):
                    if str(mock_trading_dataframe["日期/時間"][index]) == str(open_time):
                        self.entry_data.append([str(open_time), float(self.kline_dataframe['open'][index_]), kind, index_])
                        break
                    else:
                        pass
            else:
                pass

        self.entry_data.reverse()

    def open_time_is_entry_time(self, open_time: str):

        for index, data in enumerate(self.entry_data):
            entry_time = data[0]
            entry_price = data[1]
            entry_direction = data[2]

            if open_time == entry_time:
                return True, entry_time, entry_price, entry_direction

        return False, None, None, None

    # Main function for Mock Trading
    def mock_trading(self, start_property: float, buy: float, leverage: int,  profit_rate: float, max_number_of_position, add_klines, add_property, add_buy):

        long_position = []
        short_position = []
        uncertain_number = 0
        win_number = 0
        trading_number = 0
        number_of_add_property = 0
        self.initial_buy = buy

        progress = tqdm(total=len(self.kline_dataframe))
        for index, row in self.kline_dataframe.iterrows():
            if index % add_klines == 0 and index != 0:
                number_of_add_property += 1
                start_property += add_property
                buy += add_buy
                self.initial_buy += add_buy

            progress.update(1)

            open_time = str(row['Open Time'])
            open_price = row['open']
            high_price = row['high']
            low_price = row['low']
            close_price = row['close']
            ema_price = row['EMA']
            rsi_value = row["RSI"]
            bbu = row[self.BBU_name]
            bbl = row[self.BBL_name]
            profit_price = None
            liquidation = None

            boolean, entry_time, entry_price, entry_direction = self.open_time_is_entry_time(open_time)

            # Create Position
            if boolean and start_property > buy:

                # Compute quantity
                quantity = round((buy * leverage) / entry_price, 3)

                # Compute profit loss price
                profit_range = entry_price * (profit_rate / leverage)

                # Long Position
                if "多" in entry_direction and len(long_position) < max_number_of_position:
                    liquidation = round(entry_price * (1 - (100 / leverage) / 100), 2)
                    profit_price = entry_price+profit_range
                    if bbu > entry_price > ema_price and 70 > rsi_value > 50:
                        trading_number += 1
                        start_property -= buy
                        long_position.append([entry_time, entry_direction, entry_price, quantity, profit_price, liquidation])
                    else:
                        entry_time, entry_direction, entry_price, quantity, profit_price, loss_price, liquidation = None, None, None, None, None, None, None

                # Short Position
                elif "空" in entry_direction and len(short_position) < max_number_of_position:
                    liquidation = round(entry_price * (1 + (100 / leverage) / 100), 2)
                    profit_price = entry_price - profit_range
                    if bbl < entry_price < ema_price and 30 < rsi_value < 50:
                        trading_number += 1
                        start_property -= buy
                        short_position.append([entry_time, entry_direction, entry_price, quantity, profit_price, liquidation])
                    else:
                        entry_time, entry_direction, entry_price, quantity, profit_price, loss_price, liquidation = None, None, None, None, None, None, None
            else:
                entry_time, entry_direction, entry_price, quantity, profit_price, loss_price, liquidation = None, None, None, None, None, None, None

            # Observe Exit Signal
            # Long Position
            if len(long_position) == 0:  # Empty Long Position
                long_result = None
            else:
                win_number_temp = 0  # Record the number of win order in same klines
                uncertain_number_temp = 0
                loss_number_temp = 0  # Record the number of loss order in same klines
                nothing_number_temp = 0
                position_temp = long_position
                for i, order in enumerate(long_position):
                    if high_price > order[4] > low_price > order[5]:
                        start_property += ((order[4] / order[2] - 1) * leverage + 1) * buy
                        win_number += 1
                        win_number_temp += 1
                        position_temp.remove(long_position[i])
                        buy = self.initial_buy
                    elif low_price < order[4] < high_price and order[5] > low_price:
                        buy *= (1 / profit_rate)
                        uncertain_number += 1
                        uncertain_number_temp += 1
                        position_temp.remove(long_position[i])
                    elif order[5] > low_price:
                        buy *= (1 / profit_rate)
                        loss_number_temp += 1
                        position_temp.remove(long_position[i])
                    else:
                        nothing_number_temp += 1

                long_position = position_temp

                long_result = "Long Win : {}\nLong Lose : {}\nUncertain : {}\nNothing : {}"\
                              .format(win_number_temp, loss_number_temp, uncertain_number_temp, nothing_number_temp)

            # Short Position
            if len(short_position) == 0:  # Empty Long Position
                short_result = None
            else:
                win_number_temp = 0  # Record the number of win order in same klines
                uncertain_number_temp = 0
                loss_number_temp = 0  # Record the number of loss order in same klines
                nothing_number_temp = 0
                position_temp = short_position
                for i, order in enumerate(short_position):
                    if order[5] > high_price > order[4] > low_price:
                        start_property += ((1 - order[4] / order[2]) * leverage + 1) * buy
                        win_number += 1
                        win_number_temp += 1
                        position_temp.remove(short_position[i])
                        buy = self.initial_buy
                    elif low_price < order[4] < high_price and order[5] < high_price:
                        buy *= (1 / profit_rate)
                        uncertain_number += 1
                        uncertain_number_temp += 1
                        position_temp.remove(short_position[i])
                    elif order[5] < high_price:
                        buy *= (1 / profit_rate)
                        loss_number_temp += 1
                        position_temp.remove(short_position[i])
                    else:
                        nothing_number_temp += 1

                short_position = position_temp
                short_result = "Short Win : {}\nShort Lose : {}\nUncertain : {}\nNothing : {}" \
                               .format(win_number_temp, loss_number_temp, uncertain_number_temp, nothing_number_temp)

            statistic_list = [[open_time, open_price, high_price, low_price, close_price, ema_price, rsi_value, None,
                              entry_time, entry_direction, entry_price, buy, quantity, profit_price, liquidation,  None,
                              long_result, short_result, start_property]]
            if index == 0:
                self.position_history = pd.DataFrame(statistic_list,
                    columns=["klines_open_time", "klines_open_price", "klines_high_price", "klines_low_price", "klines_close_price", "klines_EMA", "RSI", "space 1",
                             "order_entry_time", "order_entry_direction", "order_price", "order_buy", "order_quantity", "order_profit", "order_liquidation", "space 2",
                             "Long Result", "Short Result", "Property"])
            else:
                temp_dataframe = pd.DataFrame(statistic_list,
                    columns=["klines_open_time", "klines_open_price", "klines_high_price", "klines_low_price", "klines_close_price", "klines_EMA", "RSI", "space 1",
                             "order_entry_time", "order_entry_direction", "order_price", "order_buy", "order_quantity", "order_profit", "order_liquidation", "space 2",
                             "Long Result", "Short Result", "Property"])
                self.position_history = pd.concat([self.position_history, temp_dataframe])

        # Winning Percentage error revise
        revise_value = len(long_position) + len(short_position)

        print("Number of add property :", number_of_add_property)
        try:
            return round(statistic_list[0][-1], 2), round(win_number/(trading_number), 2)*100, trading_number
        except:
            return round(statistic_list[0][-1], 2), "No Trading", trading_number
