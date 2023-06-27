from Config import Functions

# Account & Password
api_key = 'Nsw6xqsnHbfLyF8YExEfeVVJz4Jn3F4c4VHCr5L5sl8n8KUKzsPazLx4IX4dMaPD'
api_secret = '5ggLxtySNfzAE64bRgXz6IYHxDtaIDx399FTG1FE9IBd4332AxNBAazeKOCW9HHv'

# Parameter
buy = 5  # The unit is USDT
leverage = 5  # The leverage

print("System Initializing...")
functions = Functions(api_key, api_secret)

print("Digging Klines Data...")
last_klines, open_klines = functions.get_klines()
