# Binance Futures Auto Trading System in GCP
## Abstarct

- This is an auto trading system with binance api and build in GCP.
- Concept in algorithm include MACD, EMA, RSI, BBands.

  
## GCP Setting
- Initial Setting
```
sudo apt-get install wget
wget http://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```
- Python Module Installing
```
pip install pandas
pip install pandas_ta
pip install configparser
pip install python-binance
pip install binance-futures-connector
```
- Crontab
```
which python
0 0 * * * /home/lilray0826/yes/bin/python Main.py >> output.txt
```
- Other Useful Command
```
nano Parameter.ini
nano Main.py
crontab -e
```
