import requests
import os


class FetchCurrentPrice:

    def __init__(self):
        self.API_KEY = f"{os.environ.get('API_KEY')}"

    def fetch_current_price(self, symbol):

        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": f"{symbol}",
            "apikey": self.API_KEY
        }
        response = requests.get("https://www.alphavantage.co/query?", params=params)
        response = response.json()['Time Series (Daily)']
        date = next(iter(response))
        response = response[date]

        current_price = response['4. close']
        return current_price


