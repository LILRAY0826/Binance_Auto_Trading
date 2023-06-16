from Config import Functions
import pandas as pd

# Account & Password
api_key = 'Nsw6xqsnHbfLyF8YExEfeVVJz4Jn3F4c4VHCr5L5sl8n8KUKzsPazLx4IX4dMaPD'
api_secret = '5ggLxtySNfzAE64bRgXz6IYHxDtaIDx399FTG1FE9IBd4332AxNBAazeKOCW9HHv'

# Klines Parameter
start_date = "15 May, 2023"
end_date = "15 Jun, 2023"
interval = "30m"  # 30m, 1hr, 4hr, 1day
csv_path = "Trading_View_30m.csv"

# Mock Trading Parameter
initial_property = 8000
buy = 800
leverage = 25
profit_loss_ratio = 1.5  # 盈虧比
profit_rate = 0.5
choppy_rate = 0.1

if __name__ == '__main__':
    print("System Initializing...")
    functions = Functions(api_key, api_secret)

    print("Digging Klines Data...")
    functions.get_klines(start_date, end_date, interval)

    print("Reading Mock Trading From Trading View...")
    mock_trading_dataframe = pd.read_csv(csv_path)

    # Normalize Date Format
    try:
        mock_trading_dataframe['日期/時間'] = pd.to_datetime(mock_trading_dataframe['日期/時間'], format="%Y-%m-%d %H:%M")
    except:
        mock_trading_dataframe['日期/時間'] = pd.to_datetime(mock_trading_dataframe['日期/時間'], format="%Y-%m-%d")

    print("Get Entry Data...")
    functions.get_entry_time_price(mock_trading_dataframe)

    print("Stimulate Mock Trading...")



