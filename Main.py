from Config import Functions
import pandas as pd

# Account & Password
api_key = 'Nsw6xqsnHbfLyF8YExEfeVVJz4Jn3F4c4VHCr5L5sl8n8KUKzsPazLx4IX4dMaPD'
api_secret = '5ggLxtySNfzAE64bRgXz6IYHxDtaIDx399FTG1FE9IBd4332AxNBAazeKOCW9HHv'

print("System Initializing...")
functions = Functions(api_key, api_secret)

print("Digging Klines Data...")
open_klines = functions.get_klines()

print("Analyzing Direction...")
last_direction, direction = functions.get_direction(open_klines)

print("Done!")

