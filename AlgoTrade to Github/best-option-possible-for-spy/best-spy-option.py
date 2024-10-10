import requests
import datetime
from decimal import Decimal
import json
# ALPACA API KEYS
api_key = ''
api_secret = ''

# Function to get the current price of SPY
def get_current_price(symbol):
    url = f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest"
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return Decimal(data['quote']['ap'])

# Function to calculate the future value based on a 7% annual return
def calculate_future_value(current_value, years):
    return current_value * ((1 + Decimal('0.07')) ** years)

# Function to generate option symbols
def generate_option_symbols(symbol, start_date, end_date, strike_prices):
    option_symbols = []
    current_date = start_date

    while current_date <= end_date:
        for strike in strike_prices:
            option_symbols.append(f"{symbol}{current_date.strftime('%y%m%d')}C{strike:08d}")
        current_date += datetime.timedelta(days=7)  # Increment by 7 days for weekly options

    return option_symbols

# Function to fetch quotes in batches
def fetch_option_quotes(symbols):
    url = "https://data.alpaca.markets/v1beta1/options/quotes/latest"
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret
    }
    params = {
        "symbols": ",".join(symbols),
        "feed": "indicative"
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if 'quotes' in data:
        return data['quotes']
    else:
        raise KeyError("The key 'quotes' was not found in the response.")

# Function to find the best ROI call option
def find_best_roi_call_option(symbol):
    current_price = get_current_price(symbol)
    start_date = datetime.datetime.now() + datetime.timedelta(days=365)
    end_date = start_date + datetime.timedelta(days=365)  # One year range
    strike_prices = range(30000, 40000, 500)  # Example range from 300.00 to 400.00 in increments of 5.00

    all_symbols = generate_option_symbols(symbol, start_date, end_date, strike_prices)
    batch_size = 100
    best_roi = None
    best_option = None

    # Process symbols in batches
    for i in range(0, len(all_symbols), batch_size):
        batch_symbols = all_symbols[i:i + batch_size]
        try:
            quotes = fetch_option_quotes(batch_symbols)
            for option_symbol, option_data in quotes.items():
                if 'ap' in option_data and option_data['ap'] is not None:
                    ask_price = Decimal(option_data['ap'])
                    expiration_date_str = option_symbol[3:9]  # Extract date from symbol
                    expiration_date = datetime.datetime.strptime(expiration_date_str, '%y%m%d')
                    days_to_expiry = (expiration_date - datetime.datetime.now()).days
                    years_to_expiry = days_to_expiry / 365.0
                    future_value = calculate_future_value(current_price, years_to_expiry)
                    strike_price = Decimal(option_symbol[10:18]) / 100
                    intrinsic_value = max(future_value - strike_price, Decimal('0'))
                    roi = intrinsic_value / ask_price

                    if best_roi is None or roi > best_roi:
                        best_roi = roi
                        best_option = {
                            "symbol": option_symbol,
                            "expiration_date": expiration_date_str,
                            "strike_price": strike_price,
                            "ask_price": ask_price,
                            "roi": roi
                        }
        except KeyError as e:
            print(f"KeyError: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    return best_option

# Display the best ROI call option
try:
    best_option = find_best_roi_call_option('SPY')
    if best_option:
        print(f"Best ROI Call Option: {best_option['symbol']}")
        print(f"Expiration Date: {best_option['expiration_date']}")
        print(f"Strike Price: {best_option['strike_price']}")
        print(f"Ask Price: {best_option['ask_price']}")
        print(f"ROI: {best_option['roi']:.2f}")
    else:
        print("No suitable call option found.")
except KeyError as e:
    print(f"KeyError: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
