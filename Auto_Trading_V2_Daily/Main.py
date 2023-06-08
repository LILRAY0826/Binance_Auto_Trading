from Config import Functions

# Account & Password
api_key = 'Nsw6xqsnHbfLyF8YExEfeVVJz4Jn3F4c4VHCr5L5sl8n8KUKzsPazLx4IX4dMaPD'
api_secret = '5ggLxtySNfzAE64bRgXz6IYHxDtaIDx399FTG1FE9IBd4332AxNBAazeKOCW9HHv'

# Parameter
buy = 10  # The unit is USDT
leverage = 10  # The leverage
afford_range = 300  # Profit range
direction_choppy = 350  # The critical value of direction of position to avoid choppy trend
anti_direction_choppy = 800  # The critical value of anti direction of position to avoid choppy trend

print("System Initializing...")
functions = Functions(api_key, api_secret)

print("Digging Klines Data...")
open_klines = functions.get_klines()

print("Analyzing Direction...")
last_direction, direction = functions.get_direction(open_klines)

print("Run Main Function...")
functions.auto_order(last_direction=last_direction,
                     direction=direction,
                     buy=buy,
                     leverage=leverage,
                     direction_choppy=direction_choppy,
                     anti_direction_choppy=anti_direction_choppy,
                     afford_range=afford_range)

print("Done!")
