from binance.um_futures import UMFutures
from binance.client import Client
import pandas as pd
import talib
import math


class Function:

    def __init__(self, api_key: str, api_secret: str):
        super(Function, self).__init__()
        self.api_key = api_key
        self.api_secret = api_secret
        self.futures_client = UMFutures()
        self.client = Client(api_key=api_key, api_secret=api_secret)
        self.direction = 'up'

        # Check the margin and times is correct
        try:
            self.client.futures_change_margin_type(symbol='BTCUSDT', marginType='ISOLATED')
        except:
            pass

    def get_real_time_price(self, buy: float, leverage: int):

        # Get real time price
        price = float(self.futures_client.ticker_price("BTCUSDT")['price'])
        quantity = round(((buy / price) * leverage), 3)

        return price, quantity

    def get_real_time_macd(self):
        # Get futures klines data
        dataframe = pd.DataFrame(self.client.get_historical_klines(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_4HOUR, limit=300)).drop(columns=[5, 7, 8, 9, 10, 11])
        dataframe.columns = ['Open Time', 'open', 'high', 'low', 'close', 'Close Time']

        # Convert timestamp to datetime
        dataframe['Open Time'] = pd.to_datetime((dataframe['Open Time'] + 288e5) / 1000, unit='s')
        dataframe['Close Time'] = pd.to_datetime((dataframe['Close Time'] + 288e5) / 1000, unit='s')

        # Compute macd
        ema12 = talib.EMA(dataframe["close"], timeperiod=12)
        ema26 = talib.EMA(dataframe["close"], timeperiod=26)
        dataframe["DIF"] = ema12 - ema26
        dataframe["DIF"], dataframe["DEA"], dataframe["MACD"] = talib.MACD(dataframe['close'],
                                                                           fastperiod=12,
                                                                           slowperiod=26,
                                                                           signalperiod=9)

        # Get lasted dif and dea
        dea = round(list(dataframe["DEA"])[-1], 2)
        dif = round(list(dataframe["DIF"])[-1], 2)
        macd = round(list(dataframe["MACD"])[-1], 2)
        open_time = list(dataframe['Open Time'])[-1]

        return dif, dea, macd, open_time

    def get_margins(self):

        return math.floor(float(self.client.futures_account()['availableBalance'])*100)/100

    def cross_signal(self, dif, dea, initial_direction):
        # Check if cross
        if dif - dea > 0:
            self.direction = 'LONG'
        elif dif - dea < 0:
            self.direction = 'SHORT'
        else:
            self.direction = 'equal'

        # If cross
        if initial_direction != self.direction:
            initial_direction = self.direction  # Data recover
            return "Cross", initial_direction
        else:
            return "Waiting for cross event", initial_direction

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

    def reset_order(self, previous_orders, afford_range):
        open_orders = self.client.futures_get_open_orders(symbol="BTCUSDT")
        if len(open_orders) < len(previous_orders):
            self.set_profit_stop(afford_range=afford_range)
            return self.client.futures_get_open_orders(symbol="BTCUSDT")

        return open_orders

