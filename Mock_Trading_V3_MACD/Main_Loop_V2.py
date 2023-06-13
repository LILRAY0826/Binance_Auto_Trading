from Config_Loop_V2 import Functions
from tqdm import tqdm
import pandas as pd
import numpy as np

# Account & Password
api_key = 'Nsw6xqsnHbfLyF8YExEfeVVJz4Jn3F4c4VHCr5L5sl8n8KUKzsPazLx4IX4dMaPD'
api_secret = '5ggLxtySNfzAE64bRgXz6IYHxDtaIDx399FTG1FE9IBd4332AxNBAazeKOCW9HHv'

# Klines Parameter
start_date = "1 May, 2023"
end_date = "1 Jun, 2023"
interval = "1hr"  # 1hr, 4hr, 1day
csv_path = "Trading_View_1hr.csv"

# Mock Trading Parameter
initial_property = 8000
buy = 900
leverage = 25

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
