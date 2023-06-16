import time
from Config import Function
from binance.client import Client
from datetime import datetime
import sys

# Account & Password
api_key = 'Nsw6xqsnHbfLyF8YExEfeVVJz4Jn3F4c4VHCr5L5sl8n8KUKzsPazLx4IX4dMaPD'
api_secret = '5ggLxtySNfzAE64bRgXz6IYHxDtaIDx399FTG1FE9IBd4332AxNBAazeKOCW9HHv'

# Parameter
buy = 5  # The unit is USDT
leverage = 5  # The leverage
afford_range = 200  # Profit range
direction_choppy = 350  # The critical value of direction of position to avoid choppy trend
anti_direction_choppy = 800  # The critical value of anti direction of position to avoid choppy trend

# Function Call
function = Function(api_key=api_key,
                    api_secret=api_secret)

client = Client(api_key=api_key,
                api_secret=api_secret)

# Get initial direction
initial_dif, initial_dea, initial_macd, initial_open_time = function.get_real_time_macd()
direction = 'LONG' if initial_dif - initial_dea > 0 else 'SHORT'

# Get initial open orders
previous_orders = client.futures_get_open_orders(symbol="BTCUSDT")
open_orders = function.reset_order(previous_orders=previous_orders, afford_range=afford_range)


if __name__ == '__main__':
    print("=======================")
    while True:
        try:
            now_time = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")  # Get now time
            dif, dea, macd, open_time = function.get_real_time_macd()  # Get dif, dea, open_time
            now_price, quantity = function.get_real_time_price(buy=buy, leverage=leverage)  # Get now_price, quantity
            _property = round(function.get_margins(), 2)
            open_orders = function.reset_order(previous_orders=open_orders, afford_range=afford_range)

            if open_time != initial_open_time:  # If next open time
                # Get cross_signal, direction
                cross_signal, direction = function.cross_signal(dif=dif,
                                                                dea=dea,
                                                                initial_direction=direction)
                initial_open_time = open_time  # Data recover

                # If direction is different with last open time, and have enough money
                if cross_signal == 'Cross' and function.get_margins() > buy:
                    function.set_order(leverage=leverage,
                                       direction=direction,
                                       quantity=quantity,
                                       direction_choppy=direction_choppy,
                                       anti_direction_choppy=anti_direction_choppy)
                    time.sleep(0.5)
                    function.set_profit_stop(afford_range=afford_range)
                    pass
            else:
                pass
            sys.stdout.write("\r" + "Now Time : {}:, "
                                    "Open Time : {}, "
                                    "Price : {}, "
                                    "Quantity : {}, "
                                    "DIF : {}, "
                                    "DEA : {}, "
                                    "MACD : {}, "
                                    "Open Direction : {}, "
                                    "Property: {}".format(now_time,
                                                          open_time,
                                                          now_price,
                                                          quantity,
                                                          dif,
                                                          dea,
                                                          macd,
                                                          direction,
                                                          _property, end='', flush=True))
            sys.stdout.flush()
            # Function Call
            function = Function(api_key=api_key,
                                api_secret=api_secret)
        except Exception as e:
            print("\n", e)
            break
