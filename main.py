import pandas as pd
from FetchData import FetchFinancialData
from FetchCurrentPrice import FetchCurrentPrice
import time

# Collect Data
df = pd.read_csv('NOBL-psdlyhld.csv', skiprows=3)
df = df[' Fund Name'][:65]
df = df.reset_index(drop=True)
sample_df = df.sample(1)

ticker_dict = {}

for i in range(len(sample_df)):
    if i % 4 == 0:
        fetch_current_price = FetchCurrentPrice()
        ticker_dict[f'{df[i]}'] = float(fetch_current_price.fetch_current_price(f'{df[i]}'))
        time.sleep(60)
    else:
        fetch_current_price = FetchCurrentPrice()
        ticker_dict[f'{df[i]}'] = float(fetch_current_price.fetch_current_price(f'{df[i]}'))

print(ticker_dict)

for index, key in enumerate(ticker_dict):
    fetch_financial_data = FetchFinancialData(key, ticker_dict[key])
    result = fetch_financial_data.financial_condition()
    time.sleep(65)
