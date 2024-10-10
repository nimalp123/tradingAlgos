import alpaca
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
import datetime
import calendar
import pytz
import requests
import time
import json
from decimal import Decimal, ROUND_DOWN

# Alpaca API credentials
api_key = ''
api_secret = ''

# API endpoints and headers
PriceFetchURL = "https://data.alpaca.markets/v2/stocks/SGOV/trades/latest?feed=iex&currency=USD"
PriceFetchHeaders = {
    "accept": "application/json",
    "APCA-API-KEY-ID": api_key,
    "APCA-API-SECRET-KEY": api_secret
}

# Initialize the Alpaca trading client
trading_client = TradingClient(api_key, api_secret, paper=True)

# Function to get the current price of SGOV
def get_current_price():
    MAX_RETRIES = 5
    RETRY_DELAY = 1
    num_retries = 0
    while num_retries < MAX_RETRIES:
        try:
            PriceFetchResponse = requests.get(PriceFetchURL, headers=PriceFetchHeaders)
            PriceFetchData = json.loads(PriceFetchResponse.text)
            return Decimal(str(PriceFetchData['trade']['p']))
        except requests.RequestException as e:
            if num_retries < MAX_RETRIES:
                num_retries += 1
                print(f"Error: {e}. Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                raise e

# Main function to record price changes
def record_price_changes():
    price_changes = []
    last_price = None
    
    while True:
        current_price = get_current_price()
        
        if last_price is None or current_price != last_price:
            price_changes.append(current_price)
            last_price = current_price
            print(f"Price changed to: {current_price}")
        
        # Print the current list of price changes
        print(f"Recorded price changes: {price_changes}")
        
        # Wait for a short interval before checking the price again
        time.sleep(5)

# Run the function to start recording price changes
record_price_changes()
