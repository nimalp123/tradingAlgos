import alpaca
from alpaca.trading.client import TradingClient
from datetime import datetime
import time
import requests
import json
from decimal import Decimal
import asyncio
import aiohttp

# ALPACA API KEYS
api_key = ''
api_secret = ''

ticker = "SPY"

PriceFetchURL = f"https://data.alpaca.markets/v2/stocks/{ticker}/trades/latest?feed=iex&currency=USD"
PriceFetchHeaders = {
    "accept": "application/json",
    "APCA-API-KEY-ID": api_key,
    "APCA-API-SECRET-KEY": api_secret
}

trading_client = TradingClient(api_key, api_secret, paper=True)

status = "active"
expiration_date_gte = "2025-06-20"
expiration_date_lte = "2030-06-20"
root_symbol = ticker
optionType = "call"
optionStyle = "american"
strike_price_gte = 200
strike_price_lte = 700
resultsQuantityLimit = 20
annualReturnRateInput = 0.10

async def fetch_last_traded_price():
    async with aiohttp.ClientSession() as session:
        async with session.get(PriceFetchURL, headers=PriceFetchHeaders) as response:
            PriceFetchData = await response.json()
            return Decimal(str(PriceFetchData['trade']['p']))

async def fetch_options_contracts():
    url = (f"https://paper-api.alpaca.markets/v2/options/contracts?underlying_symbols={root_symbol}"
           f"&status={status}&expiration_date_gte={expiration_date_gte}&expiration_date_lte={expiration_date_lte}"
           f"&root_symbol={root_symbol}&type={optionType}&style={optionStyle}&strike_price_gte={strike_price_gte}"
           f"&strike_price_lte={strike_price_lte}&limit={resultsQuantityLimit}")
    
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()

async def fetch_option_quote(trade_symbol):
    quoteFeed = "indicative"
    quoteUrl = f"https://data.alpaca.markets/v1beta1/options/quotes/latest?symbols={trade_symbol}&feed={quoteFeed}"
    quoteHeaders = {
        "accept": "application/json",
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(quoteUrl, headers=quoteHeaders) as response:
            return await response.json()

async def bestOption(resultsQuantityLimit, annualReturnRateInput, status, expiration_date_gte, expiration_date_lte, root_symbol, optionType, optionStyle, strike_price_gte, strike_price_lte):
    lastTradedPrice = await fetch_last_traded_price()
    print(lastTradedPrice)

    options_contracts = await fetch_options_contracts()
    
    noneHolder = None
    leader = 0.00
    
    leadingPredictedProfitPercent = None
    leadingFinalPrice = None
    leadingAskPrice = None
    leadingExpiryDate = None
    leadingPredictedPriceAtExpiry = None
    leadingPredictedProfit = None

    async def process_option_contract(contract):
        nonlocal leader, leadingPredictedProfitPercent, leadingFinalPrice, leadingAskPrice, leadingExpiryDate, leadingPredictedPriceAtExpiry, leadingPredictedProfit
        tradeSymbol = contract["symbol"]
        quoteResponse = await fetch_option_quote(tradeSymbol)
        if tradeSymbol in quoteResponse["quotes"] and quoteResponse["quotes"][tradeSymbol]["ap"] is not noneHolder:
            askPrice = float(quoteResponse["quotes"][tradeSymbol]["ap"])
            strike_price = float(contract["strike_price"])
            final_price = round((askPrice + strike_price), 5)
            expiryDate = contract["expiration_date"]
            annualReturnRate = annualReturnRateInput
            predictedPriceAtExpiry = float(lastTradedPrice) * pow((1+annualReturnRate), years_until(expiryDate))
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

    async def process_options_contracts():
        tasks = [process_option_contract(contract) for contract in options_contracts["option_contracts"]]
        await asyncio.gather(*tasks)

    await process_options_contracts()

    print("leader:")
    print(f"strike Price: {leader} final price: {leadingFinalPrice} asking price: {leadingAskPrice} expiry Date: {leadingExpiryDate}")
    print(f"Percent to Breakeven: {(1 - Decimal(lastTradedPrice)/Decimal(leadingFinalPrice))*100}%")
    print(f"Predicted Price at Expiry: {leadingPredictedPriceAtExpiry}")
    print(f"Predicted Profit: {leadingPredictedProfit} Predicted Profit Percentage: {leadingPredictedProfitPercent*100}%")

def years_until(date_string):
    future_date = datetime.strptime(date_string, "%Y-%m-%d")
    today = datetime.today()
    days_until = (future_date - today).days
    years_until = days_until / 365.25
    return years_until

asyncio.run(bestOption(resultsQuantityLimit, annualReturnRateInput, status, expiration_date_gte, expiration_date_lte, root_symbol, optionType, optionStyle, strike_price_gte, strike_price_lte))
