from binance.client import Client
from binance.um_futures import UMFutures
from datetime import datetime
import pandas_ta as pta
import configparser
import pandas as pd
import math
import time

pd.set_option('mode.chained_assignment', None)


class Functions:

    def __init__(self):
        super(Functions, self).__init__()
        self.parameter = configparser.ConfigParser()
        self.parameter.read("Parameter.ini")
        self.api_key = self.parameter["Account_Info"]["api_key"]
        self.api_secret = self.parameter["Account_Info"]["api_secret"]

        self.client = Client(self.api_key, self.api_secret)  # Assign binance client object
        self.futures_client = UMFutures()  # Assign Futures object

        # Klines Parameter
        self.ema = int(self.parameter["Klines_Parameter"]["ema"])
        self.rsi = int(self.parameter["Klines_Parameter"]["rsi"])
        self.bband_ema = int(self.parameter["Klines_Parameter"]["bband_ema"])
        self.bband_std = float(self.parameter["Klines_Parameter"]["bband_std"])

        # Order Parameter
        self.leverage = int(self.parameter["Order_Parameter"]["leverage"])
        self.profit_rate = float(self.parameter["Order_Parameter"]["profit_rate"])
        self.buy = float(self.parameter["Order_Parameter"]["initial_buy"])
        self.currently_buy = float(self.parameter["Order_Parameter"]["currently_buy"])
        self.long_max_position = int(self.parameter["Order_Parameter"]["long_max_position"])
        self.short_max_position = int(self.parameter["Order_Parameter"]["short_max_position"])

        # BBand Column Name
        self.BBL_name = "BBL_" + str(self.bband_ema) + "_" + str(self.bband_std)
        self.BBM_name = "BBM_" + str(self.bband_ema) + "_" + str(self.bband_std)
        self.BBU_name = "BBU_" + str(self.bband_ema) + "_" + str(self.bband_std)

        # Check the margin and leverage is correct
        self.client.futures_change_leverage(symbol='BTCUSDT', leverage=self.leverage)
        try:
            self.client.futures_change_margin_type(symbol='BTCUSDT', marginType='ISOLATED')
        except:
            pass

    # The main function for trading
    def auto_trading(self, last_klines, open_klines):
        long = last_klines['MACD'] < 0 < open_klines['MACD']
        short = last_klines['MACD'] > 0 > open_klines['MACD']
        self.monitor_open_orders()
        """
        1. Available Balance must be higher than Buy.
        """
        if self.get_margins() > self.currently_buy:
            """
            Long:
            2. Entry Price must be higher than EMA.
            3. Entry Price is in the Interval of RSI Value [50~70].
            4. Entry Price must be lower than BBand Upper.
            5. Long Max Position > 0.

            Short:
            2. Entry Price must be lower than EMA.
            3. Entry Price is in the Interval of RSI Value [30~50].
            4. Entry Price must be higher than BBand Lower.
            5. Short Max Position > 0.
            """
            if long and open_klines[self.BBU_name] > open_klines['open'] > open_klines['EMA'] and 50 < open_klines['RSI'] < 70 and self.long_max_position > 0:
                quantity = self.get_quantity()
                self.client.futures_create_order(symbol='BTCUSDT',
                                                 side='BUY',
                                                 type='MARKET',
                                                 positionSide="LONG",
                                                 quantity=quantity)
                self.long_max_position -= 1
                self.parameter.set("Log", str(datetime.now().strftime("%Y-%m-%d %H-%M-%S")), "Create Long Position")

            elif short and open_klines["EMA"] > open_klines['open'] > open_klines[self.BBL_name] and 30 < open_klines['RSI'] < 50 and self.short_max_position > 0:
                quantity = self.get_quantity()
                self.client.futures_create_order(symbol='BTCUSDT',
                                                 side='SELL',
                                                 type='MARKET',
                                                 positionSide="SHORT",
                                                 quantity=quantity)
                self.short_max_position -= 1
                self.parameter.set("Log", str(datetime.now().strftime("%Y-%m-%d %H-%M-%S")), "Create Short Position")

            else:
                self.parameter.set("Log", str(datetime.now().strftime("%Y-%m-%d %H-%M-%S")), "No Trading")
                pass

        time.sleep(0.5)
        self.set_profit_stop()
        self.write_ini()

    """
    About Market's information
    """
    # Get 500 pass klines data
    def get_klines(self):

        # Get klines dataframe
        dataframe = pd.DataFrame(
            self.client.get_historical_klines(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1DAY,
                                              limit=500)).drop(columns=[5, 7, 8, 9, 10, 11])
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

        # Compute EMA
        dataframe["EMA"] = dataframe['open'].ewm(span=self.ema, adjust=False, min_periods=self.ema).mean()

        # Compute RSI
        dataframe["RSI"] = pta.rsi(dataframe['open'], length=self.rsi)

        # Change Data Type in Dataframe
        for column in dataframe.columns:
            for index, item in enumerate(dataframe[column]):
                try:
                    dataframe[column][index] = round(float(item), 2)
                except:
                    pass

        # Compute BBands
        bbands_dataframe = pta.bbands(dataframe['open'], length=self.bband_ema, std=self.bband_std)
        dataframe = pd.concat([dataframe, bbands_dataframe], axis=1)

        for column in dataframe.columns:
            for index, item in enumerate(dataframe[column]):
                try:
                    dataframe[column][index] = round(float(item), 2)
                except:
                    continue
        dataframe.to_csv("Klines.csv", encoding="utf_8_sig")

        return dataframe.iloc[-2], dataframe.iloc[-1]

    def get_quantity(self):
        return round(((self.currently_buy / (float(self.futures_client.ticker_price("BTCUSDT")['price']))) * self.leverage), 3)

    """
     About Account's Information Function
    """
    # Get Available property
    def get_margins(self):
        return math.floor(float(self.client.futures_account()['availableBalance']) * 100) / 100

    # Set Profit Stop Limit Order
    def set_profit_stop(self):

        self.client.futures_cancel_all_open_orders(symbol='BTCUSDT')
        # Set Short Profit Stop Order
        for index, info in enumerate(self.client.futures_position_information()):
            if info['symbol'] == 'BTCUSDT' and info['positionSide'] == 'SHORT':

                entry_price = round(float(info['entryPrice']), 2)

                if abs(round(float(info['positionAmt']), 3)) > 0:
                    self.client.futures_create_order(symbol='BTCUSDT',
                                                     side='BUY',
                                                     type='TAKE_PROFIT_MARKET',
                                                     positionSide='SHORT',
                                                     quantity=abs(round(float(info['positionAmt']), 3)),
                                                     stopPrice=entry_price - entry_price * (
                                                                 self.profit_rate / self.leverage))

                    self.client.futures_create_order(symbol='BTCUSDT',
                                                     side='BUY',
                                                     type='STOP_MARKET',
                                                     positionSide='SHORT',
                                                     quantity=abs(round(float(info['positionAmt']), 3)),
                                                     stopPrice=round(float(info['liquidationPrice']), 2) - 20)
                break

        # Set Long Profit Stop Order
        for index, info in enumerate(self.client.futures_position_information()):
            if info['symbol'] == 'BTCUSDT' and info['positionSide'] == 'LONG':

                entry_price = round(float(info['entryPrice']), 2)

                if abs(round(float(info['positionAmt']), 3)) > 0:
                    self.client.futures_create_order(symbol='BTCUSDT',
                                                     side='SELL',
                                                     type='TAKE_PROFIT_MARKET',
                                                     positionSide='LONG',
                                                     quantity=abs(round(float(info['positionAmt']), 3)),
                                                     stopPrice=entry_price + entry_price * (
                                                                 self.profit_rate / self.leverage))

                    self.client.futures_create_order(symbol='BTCUSDT',
                                                     side='SELL',
                                                     type='STOP_MARKET',
                                                     positionSide='LONG',
                                                     quantity=abs(round(float(info['positionAmt']), 3)),
                                                     stopPrice=round(float(info['liquidationPrice']), 2) + 20)
                break

    # Monitor Open Orders
    def monitor_open_orders(self):
        order_list = self.client.futures_get_open_orders(symbol='BTCUSDT')
        take_profit_counter = 0
        stop_counter = 0
        long_counter = 0
        short_counter = 0

        # Exist open orders
        if len(order_list) > 0:
            for order in order_list:
                if order["type"] == "TAKE_PROFIT_MARKET":
                    take_profit_counter += 1
                elif order["type"] == "STOP_MARKET":
                    stop_counter += 1

                if order["positionSide"] == 'SHORT':
                    short_counter += 1
                elif order["positionSide"] == 'LONG':
                    long_counter += 1

            # Nothing
            if take_profit_counter == stop_counter:
                pass

            # Win
            elif take_profit_counter < stop_counter:
                self.currently_buy = float(self.buy)

                if long_counter > short_counter:
                    self.short_max_position += 1
                else:
                    self.long_max_position += 1

            # Lose
            elif take_profit_counter > stop_counter:
                self.currently_buy = float(self.buy) * (1 / self.profit_rate)

                if long_counter > short_counter:
                    self.short_max_position += 1
                else:
                    self.long_max_position += 1

            else:
                pass
        else:
            pass

    """
    Record Trading Info
    """
    def write_ini(self):

        # Account_Info
        self.parameter.set("Account_Info", "api_key", self.api_key)
        self.parameter.set("Account_Info", "api_secret", self.api_secret)

        # Order_Parameter
        self.parameter.set("Order_Parameter", "leverage", str(self.leverage))
        self.parameter.set("Order_Parameter", "profit_rate", str(self.profit_rate))
        self.parameter.set("Order_Parameter", "initial_buy", str(self.buy))
        self.parameter.set("Order_Parameter", "currently_buy", str(self.currently_buy))
        self.parameter.set("Order_Parameter", "long_max_position", str(self.long_max_position))
        self.parameter.set("Order_Parameter", "short_max_position", str(self.short_max_position))

        # Klines_Parameter
        self.parameter.set("Klines_Parameter", "ema", str(self.ema))
        self.parameter.set("Klines_Parameter", "rsi", str(self.rsi))
        self.parameter.set("Klines_Parameter", "bband_ema", str(self.bband_ema))
        self.parameter.set("Klines_Parameter", "bband_std", str(self.bband_std))

        with open('Parameter.ini', 'w') as configfile:  # Save as ini file
            self.parameter.write(configfile)


if __name__ == '__main__':

    functions = Functions()

    last_kline, open_kline = functions.get_klines()

    functions.auto_trading(last_kline, open_kline)
