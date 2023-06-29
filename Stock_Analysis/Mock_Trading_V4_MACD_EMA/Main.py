from Config_BBand import Functions
# from Config import Functions
import pandas as pd
import numpy as np

# Account & Password
api_key = 'Nsw6xqsnHbfLyF8YExEfeVVJz4Jn3F4c4VHCr5L5sl8n8KUKzsPazLx4IX4dMaPD'
api_secret = '5ggLxtySNfzAE64bRgXz6IYHxDtaIDx399FTG1FE9IBd4332AxNBAazeKOCW9HHv'

# Mock Trading Parameter
start_date = "2020-07-01 00:00:00"
initial_property = 1000000
buy = 200000
leverage = 25
profit_rate = 0.5
max_number_of_position = 1
add_klines = 30
add_property = 5000
add_buy = 1500
ema = 70
std = 1.3
mode = "single"  # single, loop

# Klines Parameter
end_date = "1 Jul, 2022"
interval = "1day"  # 30m, 1hr, 4hr, 1day
csv_path = "Trading_View_1Day.csv"

start = 1
stop = 30
step = 1
leverage_list = np.arange(start=start, stop=stop + step, step=step)

start = 0.1
stop = 1
step = 0.1
profit_rate_list = np.arange(start=start, stop=stop + step, step=step)

if __name__ == '__main__':
    print("System Initializing...")
    functions = Functions(api_key, api_secret)

    print("Digging Klines Data...")
    functions.get_klines(start_date, end_date, interval, ema, std)

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
    if mode == "single":
        end_property, winning_percentage, trading_number = functions.mock_trading(start_property=initial_property,
                                                                                  buy=buy,
                                                                                  leverage=leverage,
                                                                                  profit_rate=profit_rate,
                                                                                  max_number_of_position=max_number_of_position,
                                                                                  add_klines=add_klines,
                                                                                  add_property=add_property,
                                                                                  add_buy=add_buy)

        functions.position_history.to_csv("Position History.csv", encoding="utf_8_sig")
        print("Leverage : {}, Profit Rate : {}, Trading : {}".format(leverage, profit_rate, trading_number))
        print("Winning Percentage = {}%\nProperty = {}".format(winning_percentage, end_property))
        print("Done!")

    else:
        max_winning_percentage = 0
        max_property = 0
        max_trading_number = 0
        max_leverage = None
        max_profit_rate = None
        max_position_history = pd.DataFrame()
        counter = 1
        for i, leverage in enumerate(leverage_list):
            for j, profit_rate in enumerate(profit_rate_list):
                print(counter)
                counter += 1
                end_property, winning_percentage, trading_number = functions.mock_trading(start_property=initial_property,
                                                                                          buy=buy,
                                                                                          leverage=leverage,
                                                                                          profit_rate=profit_rate,
                                                                                          max_number_of_position=max_number_of_position,
                                                                                          add_property=add_property,
                                                                                          add_buy=add_buy)
                if end_property > max_property:
                    max_property = end_property
                    max_winning_percentage = winning_percentage
                    max_leverage = leverage
                    max_profit_rate = profit_rate
                    max_position_history = functions.position_history
                    max_trading_number = trading_number
        max_position_history.to_csv("Position History.csv", encoding="utf_8_sig")

        print("Leverage : {}, Profit Rate : {}, Trading : {}".format(max_leverage, max_profit_rate, max_trading_number))
        print("Winning Percentage = {}%\nProperty = {}".format(max_winning_percentage, max_property))
        print("Done!")
