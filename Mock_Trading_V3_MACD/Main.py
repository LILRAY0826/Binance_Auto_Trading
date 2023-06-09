from Config import Functions
import pandas as pd

# Account & Password
api_key = 'Nsw6xqsnHbfLyF8YExEfeVVJz4Jn3F4c4VHCr5L5sl8n8KUKzsPazLx4IX4dMaPD'
api_secret = '5ggLxtySNfzAE64bRgXz6IYHxDtaIDx399FTG1FE9IBd4332AxNBAazeKOCW9HHv'

# Klines Parameter
start_date = "1 Jan, 2022"
end_date = "1 Jan, 2023"

# Mock Trading Parameter
initial_property = 10000
buy = 2000
leverage = 10
afford_range = 200
direction_choppy = 250
anti_direction_choppy = 800

if __name__ == '__main__':
    print("System Initializing...")
    functions = Functions(api_key, api_secret)

    print("Digging Klines Data...")
    functions.get_klines(start_date, end_date)

    print("Reading Mock Trading From Trading View...")
    mock_trading_dataframe = pd.read_excel("Mock Trading List.xlsx")
    mock_trading_dataframe['日期/時間'] = pd.to_datetime(mock_trading_dataframe['日期/時間'], format="%Y/%m/%d")

    print("Reading Klines.csv...")
    klines_dataframe = pd.read_csv("Klines.csv")

    # Normalize Date Format
    try:
        klines_dataframe['Open Time'] = pd.to_datetime(klines_dataframe['Open Time'], format="%Y-%m-%d %H:%M:%S")
    except Exception:
        klines_dataframe['Open Time'] = pd.to_datetime(klines_dataframe['Open Time'], format="%/-%m/%d %H:%M")

    print("Get Entry Data...")
    entry_data = functions.get_entry_time_price(klines_dataframe, mock_trading_dataframe)

    print("Stimulate Mock Trading...")
    functions.mock_trading(entry_data=entry_data,
                           klines_dataframe=klines_dataframe,
                           start_property=initial_property,
                           buy=buy,
                           leverage=leverage,
                           afford_range=afford_range,
                           direction_choppy=direction_choppy,
                           anti_direction_choppy=anti_direction_choppy)
    print("Done!")




