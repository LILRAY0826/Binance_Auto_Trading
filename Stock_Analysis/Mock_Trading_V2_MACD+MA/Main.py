from Config import Function

# Parameter Configuration
# Account & Password
api_key = 'Nsw6xqsnHbfLyF8YExEfeVVJz4Jn3F4c4VHCr5L5sl8n8KUKzsPazLx4IX4dMaPD'
api_secret = '5ggLxtySNfzAE64bRgXz6IYHxDtaIDx399FTG1FE9IBd4332AxNBAazeKOCW9HHv'

# Variable
start_property = 300  # 起始資產
buy = 30  # 買入金額
times = 10  # 槓桿
afford_range = 200  # 獲利範圍
crypto = 'BTCUSDT'  # Trading Item
start_date = "1 Jan, 2022"  # 資料起始日期
end_date = '1 Jan, 2023'  # 資料結束日期 Now --> until now

if __name__ == '__main__':
    print("--------------------------------")
    # Get BTC/USDT history data and output CSV file (BTCUSDT_data.csv)
    
    print("Getting BTC history data....")
    Function().get_history_data(api_key=api_key,
                                api_secret=api_secret,
                                crypto=crypto,
                                start_date=start_date,
                                end_date=end_date)

    # Compute DIF MACD and output CSV file(MACD.csv)
    print("Computing DIF & MACD....")
    Function().compute_dif_and_macd()

    # Computing Winning Percentage
    print("Computing Winning Percentage....")
    print("--------------------------------")
    print("起始資金：{}, 買入金額：{}, 槓桿：{}, 獲利範圍：{}".format(start_property, buy, times, afford_range))
    print("資料起始日期：{}".format(start_date))
    print("--------------------------------")
    Function().compute_winning_percentage(start_property=start_property,
                                          buy=buy,
                                          times=times,
                                          afford_range=afford_range)
    print("================================")
    print("Done!")
