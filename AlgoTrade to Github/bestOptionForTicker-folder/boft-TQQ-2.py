import alpaca
from alpaca.trading.client import TradingClient
from datetime import datetime
import time
import requests
import json
from decimal import Decimal

# ALPACA API KEYS

api_key = ''
api_secret = ''

ticker = "TQQQ"

PriceFetchURL = "https://data.alpaca.markets/v2/stocks/" + ticker + "/trades/latest?feed=iex&currency=USD"
PriceFetchHeaders = {
    "accept": "application/json",
    "APCA-API-KEY-ID": api_key,
    "APCA-API-SECRET-KEY": api_secret
}

trading_client = TradingClient(api_key, api_secret, paper=True)

status = "active"
expiration_date_gte = "2024-09-20"
expiration_date_lte = "2024-10-26"
root_symbol = ticker
optionType = "call"
optionStyle = "american"
strike_price_gte = 45
strike_price_lte = 70
resultsQuantityLimit = 2000
annualReturnRateInput = 0.10 

def bestOption(resultsQuantityLimit, annualReturnRateInput, status, expiration_date_gte, expiration_date_lte, root_symbol, optionType, optionStyle, strike_price_gte, strike_price_lte):
    def get_trading_account():
        MAX_RETRIES = 5
        RETRY_DELAY = 1
        num_retries = 0
        while num_retries < MAX_RETRIES:
            try:
                return trading_client.get_account()
            except alpaca.common.exceptions.APIError as e:
                if num_retries < MAX_RETRIES:
                    num_retries += 1
                    print(f"Error {e.status_code}: {e.message}. Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    raise e
            except Exception as e:
                if num_retries < MAX_RETRIES:
                    num_retries += 1
                    print(f"Error . Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    raise e

    def getLastTradedPrice():
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
    
    lastTradedPrice = getLastTradedPrice()
    print(lastTradedPrice)

    url = f"https://paper-api.alpaca.markets/v2/options/contracts?underlying_symbols={root_symbol}&status={status}&expiration_date_gte={expiration_date_gte}&expiration_date_lte={expiration_date_lte}&root_symbol={root_symbol}&type={optionType}&style={optionStyle}&strike_price_gte={strike_price_gte}&strike_price_lte={strike_price_lte}&limit={resultsQuantityLimit}"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret
    }

    response = requests.get(url, headers=headers)
    
    def years_until(date_string):
        future_date = datetime.strptime(date_string, "%Y-%m-%d")
        today = datetime.today()
        days_until = (future_date - today).days
        years_until = days_until / 365.25
        return years_until

    json_object = json.loads(response.text)

    noneHolder = None
    leader = 0.00
    quoteFeed = "indicative"
    quoteHeaders = {
        "accept": "application/json",
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret
    }

    for i in range(resultsQuantityLimit):
        tradeSymbol = json_object["option_contracts"][i]["symbol"]
        quoteUrl = f"https://data.alpaca.markets/v1beta1/options/quotes/latest?symbols={tradeSymbol}&feed={quoteFeed}"
        quoteResponse = json.loads(requests.get(quoteUrl, headers=quoteHeaders).text)
        if type(quoteResponse["quotes"][tradeSymbol]["ap"]) != type(noneHolder):
            askPrice = float(quoteResponse["quotes"][tradeSymbol]["ap"])
            strike_price = float(json_object["option_contracts"][i]["strike_price"])
            final_price = round((askPrice + strike_price), 5)
            expiryDate = json_object["option_contracts"][i]["expiration_date"]
            annualReturnRate = annualReturnRateInput
            predictedPriceAtExpiry = 65
            predictedProfit = (predictedPriceAtExpiry - float(lastTradedPrice)) * 100
            predictedProfitPercent = (predictedPriceAtExpiry - float(lastTradedPrice)) / float(lastTradedPrice)
            if leader != 0.00 and leadingPredictedProfitPercent < predictedProfitPercent:
                leader = strike_price
                leadingFinalPrice = final_price
                leadingAskPrice = askPrice
                leadingExpiryDate = expiryDate
                leadingPredictedProfitPercent = predictedProfitPercent
                leadingPredictedPriceAtExpiry = predictedPriceAtExpiry
                leadingPredictedProfit = predictedProfit
            elif leader == 0:
                leader = strike_price
                leadingFinalPrice = final_price
                leadingAskPrice = askPrice
                leadingExpiryDate = expiryDate
                leadingPredictedProfitPercent = predictedProfitPercent
                leadingPredictedPriceAtExpiry = predictedPriceAtExpiry
                leadingPredictedProfit = predictedProfit

    print("leader:")
    print(f"strike Price: {leader} final price: {leadingFinalPrice} asking price: {leadingAskPrice} expiry Date: {leadingExpiryDate}")
    print(f"Percent to Breakeven: {(1 - Decimal(lastTradedPrice)/Decimal(leadingFinalPrice))*100}%")
    print(f"Predicted Price at Expiry: {leadingPredictedPriceAtExpiry}")
    print(f"Predicted Profit: {leadingPredictedProfit} Predicted Profit Percentage: {leadingPredictedProfitPercent*100}%")

bestOption(resultsQuantityLimit, annualReturnRateInput, status, expiration_date_gte, expiration_date_lte, root_symbol, optionType, optionStyle, strike_price_gte, strike_price_lte)
