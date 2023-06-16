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
        self.entry_data = []
        self.kline_dataframe = pd.DataFrame
        self.position_history = pd.DataFrame(
            columns=["klines_open_time", "klines_open_price", "klines_high_price", "klines_low_price","klines_close_price", "space 1",
                     "order_entry_time", "order_entry_direction", "order_price", "order_quantity", "space 2",
                     "long_position_entry_time", "long_position_entry_direction", "long_position_price",
                     "long_position_quantity", "long_position_afford_range", "long_position_liquidation", "space 3",
                     "short_position_entry_time", "short_position_entry_direction", "short_position_price",
                     "short_position_quantity", "short_position_afford_range", "short_position_liquidation", "space 4",
                     "LONG_Result", "SHORT_Result", "Property"])

    def get_klines(self, start_date, end_date, interval):

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
                                                                   start_str=start_date,
                                                                   end_str=end_date)).drop(columns=[5, 7, 8, 9, 10, 11])
        self.kline_dataframe.columns = ['Open Time', 'open', 'high', 'low', 'close', 'Close Time']

        # Convert timestamp to datetime
        self.kline_dataframe['Open Time'] = pd.to_datetime((self.kline_dataframe['Open Time']) / 1000, unit='s')
        self.kline_dataframe['Close Time'] = pd.to_datetime((self.kline_dataframe['Close Time']) / 1000, unit='s')  # 288e5

        self.kline_dataframe['EMA200'] = self.kline_dataframe['close'].ewm(span=200).mean()

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
    def mock_trading(self, start_property: float, buy: float, leverage: int, profit_loss_ratio: float, profit_rate: float, choppy_rate: float):

        long_position = [None, None, None, None, None, None]
        short_position = [None, None, None, None, None, None]
        long_result = None
        short_result = None

        progress = tqdm(total=len(self.kline_dataframe))
        for index, row in self.kline_dataframe.iterrows():

            progress.update(1)

            if None != long_result:
                long_position = [None, None, None, None, None, None]

            if None != short_result:
                short_position = [None, None, None, None, None, None]

            open_time = str(row['Open Time'])
            open_price = row['open']
            high_price = row['high']
            low_price = row['low']
            close_price = row['close']
            boolean, entry_time, entry_price, entry_direction = self.open_time_is_entry_time(open_time, self.entry_data)
