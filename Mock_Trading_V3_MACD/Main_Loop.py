from Config_Loop import Functions
from tqdm import tqdm
import pandas as pd
import numpy as np

# Account & Password
api_key = 'Nsw6xqsnHbfLyF8YExEfeVVJz4Jn3F4c4VHCr5L5sl8n8KUKzsPazLx4IX4dMaPD'
api_secret = '5ggLxtySNfzAE64bRgXz6IYHxDtaIDx399FTG1FE9IBd4332AxNBAazeKOCW9HHv'

# Klines Parameter
start_date = "12 May, 2023"
end_date = "12 Jun, 2023"
interval = "1hr"  # 1hr, 4hr, 1day
csv_path = "Trading_View_1hr.csv"

# Mock Trading Parameter
initial_property = 8000
buy = 900

start = 1
stop = 30
step = 1
leverage_list = np.arange(start=start, stop=stop + step, step=step)

start = 0.1
stop = 1
step = 0.1
profit_rate_list = np.arange(start=start, stop=stop + step, step=step)

start = 0.1
stop = 1
step = 0.1
choppy_rate_list = np.arange(start=start, stop=stop + step, step=step)

if __name__ == '__main__':
    print("System Initializing...")
    functions = Functions(api_key, api_secret)

    print("Digging Klines Data...")
    functions.get_klines(start_date, end_date, interval)

    print("Reading Mock Trading From Trading View...")
    mock_trading_dataframe = pd.read_csv(csv_path)

    try:
        mock_trading_dataframe['日期/時間'] = pd.to_datetime(mock_trading_dataframe['日期/時間'], format="%Y-%m-%d %H:%M")
    except:
        mock_trading_dataframe['日期/時間'] = pd.to_datetime(mock_trading_dataframe['日期/時間'], format="%Y-%m-%d")

    print("Reading Klines.csv...")
    klines_dataframe = pd.read_csv("Klines.csv")

    # Normalize Date Format
    try:
        klines_dataframe['Open Time'] = pd.to_datetime(klines_dataframe['Open Time'], format="%Y-%m-%d")
    except Exception:
        klines_dataframe['Open Time'] = pd.to_datetime(klines_dataframe['Open Time'], format="%Y-%m-%d %H:%M:%S")

    print("Get Entry Data...")
    entry_data = functions.get_entry_time_price(klines_dataframe, mock_trading_dataframe)

    print("Stimulate Mock Trading...")
    max_winning_percentage = 0
    max_property = 0
    max_leverage = None
    max_profit_rate = None
    max_uncertain_number = 0
    max_choppy_rate = 0
    max_position_history = pd.DataFrame()
    progress = tqdm(total=(len(leverage_list)*len(profit_rate_list)*len(choppy_rate_list)))

    for i, leverage in enumerate(leverage_list):
        for j, profit_rate in enumerate(profit_rate_list):
            for a, choppy_rate in enumerate(choppy_rate_list):
                end_property, winning_percentage, uncertain_number, position_history = functions.mock_trading(entry_data=entry_data,
                                                                                                              klines_dataframe=klines_dataframe,
                                                                                                              start_property=initial_property,
                                                                                                              buy=buy,
                                                                                                              leverage=leverage,
                                                                                                              profit_rate=profit_rate,
                                                                                                              choppy_rate=choppy_rate)
                progress.update(1)
                if end_property > max_property:
                    max_property = end_property
                    max_winning_percentage = winning_percentage
                    max_leverage = leverage
                    max_profit_rate = profit_rate
                    max_choppy_rate = choppy_rate
                    max_uncertain_number = uncertain_number
                    max_position_history = position_history

    print("=======================================")
    max_position_history.to_csv("Position History.csv", encoding="utf_8_sig")
    print("Uncertain = {}".format(max_uncertain_number))
    print("Winning Percentage = {}%\nProperty = {}".format(max_winning_percentage, max_property))
    print("Leverage : {}, Profit Rate : {}, Choppy Rate : {}".format(max_leverage, max_profit_rate, max_choppy_rate))
    print("Done!")
