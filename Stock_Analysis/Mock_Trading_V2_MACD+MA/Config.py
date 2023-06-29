from binance.client import Client
import pandas as pd
import math
import talib
pd.set_option('mode.chained_assignment', None)


class Function:
    def __init__(self):
        super(Function, self).__init__()
        self.direction = "null"
        self.kline_interval = ""

    # Compute Initial Direction
    def compute_initial_direction(self, dif: pd.Series,  macd: pd.Series):
        start_index = -1
        for i, j in zip(dif, macd):
            start_index += 1
            if math.isnan(i) or math.isnan(j):
                continue
            else:
                self.direction = float(i) - float(j)
                if self.direction <= 0:
                    self.direction = 'down'
                else:
                    self.direction = 'up'
                break
        return self.direction, start_index  # start_index means the data index that show up number

    # Get history data
    def get_history_data(self, api_key: str, api_secret: str, crypto: str, start_date: str, end_date: str):
        # 請求權限
        client = Client(api_key, api_secret)

        # 抓取數據 (日期時間和價量相差８小時)
        if end_date == "Now":
            klines = client.get_historical_klines(crypto, Client.KLINE_INTERVAL_1HOUR, start_date)
        else:
            klines = client.get_historical_klines(crypto, Client.KLINE_INTERVAL_1HOUR, start_date, end_date)

        # 數據存入 Dataframe
        whole_df = pd.DataFrame(klines)
        whole_df.columns = ['Open_time', 'open', 'high', 'low', 'close', 'volume', 'Close_time',
                            'Quote asset volume', 'number of trades', 'Taker buy base asset volume',
                            'Taker buy quote asset volume', 'Ignore']

        # 刪除重複資料
        whole_df = whole_df.drop_duplicates(subset=['Open_time'], keep=False)

        # 刪除不要的資料
        whole_df = whole_df.drop(columns=['Quote asset volume',
                                          'number of trades',
                                          'Taker buy base asset volume',
                                          'Taker buy quote asset volume',
                                          'Ignore'])

        # 調整時間誤差
        whole_df['Open_time'] = whole_df['Open_time'] + 288e5
        whole_df['Close_time'] = whole_df['Close_time'] + 288e5

        # 更改時間的 Data Type
        whole_df['Open_time'] = pd.to_datetime(whole_df['Open_time'] / 1000, unit='s')
        whole_df['Close_time'] = pd.to_datetime(whole_df['Close_time'] / 1000, unit='s')

        # 輸出成csv檔
        whole_df.to_csv('/Users/rayching/Desktop/PyCharm/Stock_Analysis/Python File/Mock Trading/BTCUSDT_data.csv',
                        encoding='utf-8-sig')

    # Compute DIF & MACD
    def compute_dif_and_macd(self):
        dataframe = pd.read_csv("/Users/rayching/Desktop/PyCharm/Stock_Analysis/Python File/Mock Trading/BTCUSDT_data.csv", index_col=0)
        ema12 = talib.EMA(dataframe["close"], timeperiod=12)
        ema26 = talib.EMA(dataframe["close"], timeperiod=26)
        dataframe["DIF"] = ema12 - ema26
        dataframe["DIF"], dataframe["MACD"], dataframe["DIF-MACD"] = talib.MACD(dataframe['close'],
                                                                                fastperiod=12,
                                                                                slowperiod=26,
                                                                                signalperiod=9)
        dataframe["short_ma"] = talib.MA(dataframe["open"], timeperiod=13)
        dataframe["long_ma"] = talib.MA(dataframe["close"], timeperiod=9)

        dataframe.to_csv("/Users/rayching/Desktop/PyCharm/Stock_Analysis/Python File/Mock Trading/MACD.csv")

    # Compute Winning Percentage
    def compute_winning_percentage(self, start_property: int, buy: float, times: int, afford_range: int):
        # Assign Variable
        dataframe = pd.read_csv("/Users/rayching/Desktop/PyCharm/Stock_Analysis/Python File/Mock Trading/MACD.csv", index_col=0)
        dif = dataframe["DIF"]
        macd = dataframe["MACD"]
        open_time = dataframe["Open_time"]
        open_price = dataframe["open"]
        high_price = dataframe["high"]
        low_price = dataframe["low"]
        short_ma = dataframe["short_ma"]
        long_ma = dataframe["long_ma"]

        cross_times = 0  # 總交易次數
        max_order_number = start_property // buy  # 初始可容納最大持倉數
        maximum = max_order_number  # 最大持倉數
        order_number = 0  # 目前持倉數
        accmulation = 0  # 累積開倉數

        # Create empty dataframe to store statistical data
        statistical_dataframe = pd.DataFrame(columns=["開倉時間",
                                                      "方向",
                                                      "開倉價格",
                                                      "槓桿倍數",
                                                      "爆倉價格",
                                                      "掛單價格",
                                                      "結果",
                                                      "平倉時間",
                                                      "獲利金額"])

        # Get initial direction
        direction, start_index = Function().compute_initial_direction(dif=dif, macd=macd)

        # Compute Cross times (總交易次數), 開多少的多空倉等資料，匯總成dataframe
        for i in range(start_index, len(dif)):

            diff = dif[i] - macd[i]
            if diff <= 0:
                _direction = 'down'
            else:
                _direction = 'up'

            # Win Condition
            try:
                for index, j in enumerate(statistical_dataframe["掛單價格"]):
                    if float(high_price[i - 1]) > float(j) > float(low_price[i - 1]) and \
                            statistical_dataframe["結果"][index] == "None":

                        statistical_dataframe["結果"][index] = "Win"
                        statistical_dataframe["平倉時間"][index] = open_time[i - 1]
                        statistical_dataframe["獲利金額"][index] = round((buy * (1 + (times * (afford_range / float(
                            statistical_dataframe["開倉價格"][index]))))) - buy, 2)

                        start_property += statistical_dataframe["獲利金額"][index] + buy - (statistical_dataframe["獲利金額"][index]*0.001)
                        max_order_number += 1
                        order_number -= 1
                        if max_order_number > maximum:
                            maximum = max_order_number

            # Lose Condition
                for (index, j), k in zip(enumerate(statistical_dataframe["爆倉價格"]), statistical_dataframe["方向"]):
                    lose_condition_1 = k == "down" and float(j) < high_price[i - 1]
                    lose_condition_2 = k == "up" and float(j) > low_price[i - 1]
                    if (lose_condition_2 or lose_condition_1) and statistical_dataframe["結果"][index] == "None":
                        statistical_dataframe["結果"][index] = "Lose"
                        statistical_dataframe["平倉時間"][index] = open_time[i - 1]
                        statistical_dataframe["獲利金額"][index] = 0

                        start_property += 0
                        max_order_number += 1
                        order_number -= 1
                        if max_order_number > maximum:
                            maximum = max_order_number
            except:
                pass

            # 交叉時機點
            if _direction != direction:

                if _direction == "down" and max_order_number > 0 and start_property >= buy and open_price[i] < short_ma[i]:
                    explode_price = round(float(open_price[i]) + float(open_price[i]) * (1 / times), 2)
                    send_price = float(open_price[i]) - afford_range

                    start_property -= buy + buy*0.001
                    max_order_number -= 1
                    order_number += 1
                    accmulation += 1

                    if max_order_number > maximum:
                        maximum = max_order_number

                    statistical_dataframe.loc[accmulation-1] = [open_time[i],
                                                                _direction,
                                                                open_price[i],
                                                                times,
                                                                explode_price,
                                                                send_price,
                                                                "None",
                                                                "None",
                                                                "None"]

                if _direction == "up" and max_order_number > 0 and start_property >= buy and open_price[i] > long_ma[i]:
                    explode_price = round(float(open_price[i]) - float(open_price[i]) * (1 / times), 2)
                    send_price = float(open_price[i]) + afford_range

                    start_property -= buy + buy*0.001
                    max_order_number -= 1
                    order_number += 1
                    accmulation += 1

                    if max_order_number > maximum:
                        maximum = max_order_number

                    statistical_dataframe.loc[accmulation-1] = [open_time[i],
                                                                _direction,
                                                                open_price[i],
                                                                times,
                                                                explode_price,
                                                                send_price,
                                                                "None",
                                                                "None",
                                                                "None"]

                if start_property < buy and order_number == 0:
                    break

                direction = _direction
                cross_times += 1

        # Compute Winning Percentage
        win_times = 0
        for i in statistical_dataframe["結果"]:
            if i == "Win":
                win_times += 1

        if accmulation == 0:
            print("No any orders.")
        else:
            print("Winning Percentage : ", round((win_times / accmulation) * 100, 2), "%")
        print("總共交易次數：", accmulation)

        print("總資產為 : ", round(start_property, 2))

        statistical_dataframe.to_csv("/Users/rayching/Desktop/PyCharm/Stock_Analysis/Python File/Mock Trading/Trading List.csv")
