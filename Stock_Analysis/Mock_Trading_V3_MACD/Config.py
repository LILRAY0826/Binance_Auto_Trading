from binance.client import Client
from binance.um_futures import UMFutures
from tqdm import tqdm
import pandas as pd

pd.set_option('mode.chained_assignment', None)


class Functions:

    def __init__(self, api_key: str, api_secret: str):
        super(Functions, self).__init__()
        self.client = Client(api_key, api_secret)  # Assign binance client object
        self.futures_client = UMFutures()  # Assign Futures object

    # Main function for Mock Trading
    def mock_trading(self, entry_data: list, klines_dataframe: pd.DataFrame, start_property, buy, leverage, profit_rate, choppy_rate):

        long_position = [[None, None, None, None, None, None]]
        short_position = [[None, None, None, None, None, None]]
        long_result = None
        short_result = None
        trading_number = 0
        win_number = 0
        uncertain_number = 0
        long_position_accumulate = 0
        short_position_accumulate = 0
        long_position_buy_accumulate = 0
        short_position_buy_accumulate = 0

        position_history = pd.DataFrame(columns=["klines_open_time", "klines_open_price", "klines_high_price", "klines_low_price", "klines_close_price", "space 1",
                                                 "order_entry_time", "order_entry_direction", "order_price", "order_quantity", "space 2",
                                                 "long_position_entry_time", "long_position_entry_direction", "long_position_price", "long_position_quantity", "long_position_afford_range", "long_position_liquidation", "space 3",
                                                 "short_position_entry_time", "short_position_entry_direction", "short_position_price", "short_position_quantity", "short_position_afford_range", "short_position_liquidation", "space 4",
                                                 "LONG_Result", "SHORT_Result", "Property"])

        # Iterate klines to simulate the market
        progress = tqdm(total=len(klines_dataframe))
        for index, row in klines_dataframe.iterrows():

            progress.update(1)
            if long_result != None:
                long_position = [[None, None, None, None, None, None]]

            if short_result != None:
                short_position = [[None, None, None, None, None, None]]

            open_time = str(row['Open Time'])
            open_price = row['open']
            high_price = row['high']
            low_price = row['low']
            close_price = row['close']
            boolean, entry_time, entry_price, entry_direction = self.open_time_is_entry_time(open_time, entry_data)

            if entry_price == None:
                quantity = None
            else:
                if "多" in entry_direction:
                    if long_position[0][0] != None:
                        quantity = long_position[0][3]
                    else:
                        quantity = round((buy * leverage) / entry_price, 3)
                        if quantity < 0.001:
                            quantity = 0.001
                else:
                    if short_position[0][0] != None:
                        quantity = short_position[0][3]
                    else:
                        quantity = round((buy * leverage) / entry_price, 3)
                        if quantity < 0.001:
                            quantity = 0.001

            # Create Position
            if boolean and start_property > (quantity / leverage) * entry_price:

                # Long Position
                if "多" in entry_direction:
                    if long_position[0][0] == None:
                        trading_number += 1
                        liquidation = round(entry_price * (1 - (100 / leverage) / 100), 2)
                        afford_range = entry_price * (profit_rate / leverage)
                        long_position = [[entry_time, entry_direction, entry_price, quantity, entry_price + afford_range, liquidation]]
                        start_property -= (quantity / leverage) * entry_price
                        long_position_buy_accumulate += (quantity / leverage) * entry_price
                    else:
                        afford_range = long_position[0][2] * (profit_rate / leverage)
                        if long_position[0][2] - ((long_position[0][2] - long_position[0][5]) * choppy_rate) <= entry_price <= long_position[0][2] + afford_range + 20:
                            entry_time, entry_price, entry_direction, quantity = None, None, None, None
                            pass
                        else:
                            trading_number += 1
                            long_position_accumulate += 1
                            long_position[0][0] = entry_time
                            times = long_position[0][3] / quantity
                            long_position[0][2] = (long_position[0][2] * times + entry_price) / (times + 1)
                            long_position[0][3] += quantity
                            afford_range = long_position[0][2] * (profit_rate / leverage)
                            long_position[0][4] = long_position[0][2] + afford_range
                            long_position[0][5] = round(long_position[0][2] * (1 - (100 / leverage) / 100), 2)
                            start_property -= (quantity / leverage) * entry_price
                            long_position_buy_accumulate += (quantity / leverage) * entry_price

                # Short Position
                elif "空" in entry_direction:

                    if short_position[0][0] == None:
                        trading_number += 1
                        liquidation = round(entry_price * (1 + (100 / leverage) / 100), 2)
                        afford_range = entry_price * (profit_rate / leverage)
                        short_position = [[entry_time, entry_direction, entry_price, quantity, entry_price - afford_range, liquidation]]
                        start_property -= (quantity / leverage) * entry_price
                        short_position_buy_accumulate += (quantity / leverage) * entry_price
                    else:
                        afford_range = short_position[0][2] * (profit_rate / leverage)
                        if short_position[0][2] - afford_range - 20 <= entry_price <= short_position[0][2] + ((short_position[0][5] - short_position[0][2]) * choppy_rate):
                            entry_time, entry_price, entry_direction, quantity = None, None, None, None
                            pass
                        else:
                            trading_number += 1
                            short_position_accumulate += 1
                            short_position[0][0] = entry_time
                            times = short_position[0][3] / quantity
                            short_position[0][2] = (short_position[0][2] * times + entry_price) / (times + 1)
                            short_position[0][3] += quantity
                            afford_range = short_position[0][2] * (profit_rate / leverage)
                            short_position[0][4] = short_position[0][2] - afford_range
                            short_position[0][5] = round(short_position[0][2] * (1 + (100 / leverage) / 100), 2)
                            start_property -= (quantity / leverage) * entry_price
                            short_position_buy_accumulate += (quantity / leverage) * entry_price

            # Observe Exit Signal
            if long_position[0][0] != None:
                if low_price < long_position[0][4] < high_price and long_position[0][5] < low_price:
                    start_property += ((long_position[0][4] / long_position[0][2] - 1) * leverage + 1) * long_position_buy_accumulate
                    long_result = "LONG Win"
                    win_number += 1 + long_position_accumulate
                    long_position_accumulate = 0
                    long_position_buy_accumulate = 0
                elif low_price < long_position[0][4] < high_price and long_position[0][5] > low_price:
                    long_result = "Uncertain"
                    long_position_accumulate = 0
                    uncertain_number += 1
                    long_position_buy_accumulate = 0
                elif long_position[0][5] > low_price:
                    long_result = "LONG Lose"
                    long_position_accumulate = 0
                    long_position_buy_accumulate = 0
                else:
                    long_result = None
            else:
                long_result = None

            if short_position[0][0] != None:
                if low_price < short_position[0][4] < high_price and short_position[0][5] > high_price:
                    start_property += (1 + (1 - (short_position[0][4] / short_position[0][2])) * leverage) * short_position_buy_accumulate
                    short_result = "SHORT Win"
                    win_number += 1 + short_position_accumulate
                    short_position_accumulate = 0
                    short_position_buy_accumulate = 0
                elif low_price < short_position[0][4] < high_price and short_position[0][5] < high_price:
                    short_result = "Uncertain"
                    short_position_accumulate = 0
                    uncertain_number += 1
                    short_position_buy_accumulate = 0
                elif short_position[0][5] < high_price:
                    short_result = "SHORT Lose"
                    short_position_accumulate = 0
                    short_position_buy_accumulate = 0
                else:
                    short_result = None
            else:
                short_result = None

            # Record Position Situation
            list = [[open_time, open_price, high_price, low_price, close_price, None,
                    entry_time, entry_direction, entry_price, quantity, None,
                    long_position[0][0], long_position[0][1], long_position[0][2], long_position[0][3], long_position[0][4], long_position[0][5], None,
                    short_position[0][0], short_position[0][1], short_position[0][2], short_position[0][3], short_position[0][4], short_position[0][5],
                    long_result, short_result, start_property]]

            if index == 0:
                position_history = pd.DataFrame(list, columns=["klines_open_time", "klines_open_price", "klines_high_price", "klines_low_price", "klines_close_price", "space 1",
                                                               "order_entry_time", "order_entry_direction", "order_price", "order_quantity", "space 2",
                                                               "long_position_entry_time", "long_position_entry_direction", "long_position_price", "long_position_quantity", "long_position_afford_range", "long_position_liquidation", "space 3",
                                                               "short_position_entry_time", "short_position_entry_direction", "short_position_price", "short_position_quantity", "short_position_afford_range", "short_position_liquidation",
                                                               "LONG_Result", "SHORT_Result", "Property"])
            else:
                temp_dataframe = pd.DataFrame(list, columns=["klines_open_time", "klines_open_price", "klines_high_price", "klines_low_price", "klines_close_price", "space 1",
                                                             "order_entry_time", "order_entry_direction", "order_price", "order_quantity", "space 2",
                                                             "long_position_entry_time", "long_position_entry_direction", "long_position_price", "long_position_quantity", "long_position_afford_range", "long_position_liquidation", "space 3",
                                                             "short_position_entry_time", "short_position_entry_direction", "short_position_price", "short_position_quantity", "short_position_afford_range", "short_position_liquidation",
                                                             "LONG_Result", "SHORT_Result", "Property"])
                position_history = pd.concat([position_history, temp_dataframe])

        position_history.to_csv("Position History.csv", encoding='utf_8_sig')
        print("Uncertain = {}".format(uncertain_number))

        revise_value = 0
        if long_position[0][0] != None:
            revise_value += 1
        if short_position[0][0] != None:
            revise_value += 1

        try:
            return list[0][-1], round(win_number/(trading_number - short_position_accumulate - long_position_accumulate - revise_value), 2) * 100
        except:
            return list[0][-1], "No Trading"

    # About Market's information
    # Get 300 pass klines data
    def get_klines(self, start_date, end_date, interval):

        # Get klines dataframe
        if interval == "1hr":
            interval = Client.KLINE_INTERVAL_1HOUR
        elif interval == "4hr":
            interval = Client.KLINE_INTERVAL_4HOUR
        elif interval == "1day":
            interval = Client.KLINE_INTERVAL_1DAY
        dataframe = pd.DataFrame(self.client.get_historical_klines(symbol="BTCUSDT",
                                                                   interval=interval,
                                                                   start_str=start_date,
                                                                   end_str=end_date)).drop(columns=[5, 7, 8, 9, 10, 11])
        dataframe.columns = ['Open Time', 'open', 'high', 'low', 'close', 'Close Time']

        # Convert timestamp to datetime
        dataframe['Open Time'] = pd.to_datetime((dataframe['Open Time']) / 1000, unit='s')
        dataframe['Close Time'] = pd.to_datetime((dataframe['Close Time']) / 1000, unit='s')  # 288e5

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
        process = tqdm(total=len(mock_trading_dataframe))
        for index, kind in enumerate(mock_trading_dataframe["種類"]):
            process.update(1)
            # Get Entry Time
            if "進場" in kind:
                for index_, open_time in enumerate(klines_dataframe["Open Time"]):
                    if str(mock_trading_dataframe["日期/時間"][index]) == str(open_time):
                        entry_data.append([str(open_time), float(klines_dataframe['open'][index_]), kind, index_])
                        break
                    else:
                        pass
            else:
                pass

        entry_data.reverse()
        return entry_data

    def open_time_is_entry_time(self, open_time: str, entry_data):

        for index, data in enumerate(entry_data):
            entry_time = data[0]
            entry_price = data[1]
            entry_direction = data[2]

            if open_time == entry_time:
                return True, entry_time, entry_price, entry_direction

        return False, None, None, None
