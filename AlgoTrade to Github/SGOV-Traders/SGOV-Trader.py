# import subprocess
# import sys
# def install(package):
#     subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# install("alpca-py")  
# install("pytz")
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

# ALPACA API KEYS

api_key = ''
api_secret = ''


OrdersURL = "https://paper-api.alpaca.markets/v2/orders?status=open&symbols=SGOV"

OrdersHeaders = {
    "accept": "application/json",
    "APCA-API-KEY-ID": api_key,
    "APCA-API-SECRET-KEY": api_secret
}

PriceFetchURL = "https://data.alpaca.markets/v2/stocks/SGOV/trades/latest?feed=iex&currency=USD"

PriceFetchHeaders = {
    "accept": "application/json",
    "APCA-API-KEY-ID": "PKMU9W1CEZFAAQVRMBKF",
    "APCA-API-SECRET-KEY": "QaogM7twwSNwo3JQ7ewncTorarm7AivZmdyVJzAj"
}

trading_client = TradingClient(api_key, api_secret, paper=True)

# Get our account information.
account = trading_client.get_account()

# Check if our account is restricted from trading.
if account.trading_blocked:
    print('Account is currently restricted from trading.')

account = trading_client.get_account()

ntnal = int(float(account.non_marginable_buying_power))

# multi symbol request - single symbol is similar
request_params = StockLatestQuoteRequest(symbol_or_symbols=["SGOV"])
MAX_RETRIES = 5
RETRY_DELAY = 1

def get_current_price():
    num_retries = 0
    while num_retries < MAX_RETRIES:
        try:
            #last trade price
            PriceFetchResponse = requests.get(PriceFetchURL, headers=PriceFetchHeaders)
            PriceFetchData = json.loads(PriceFetchResponse.text)
            return PriceFetchData['trade']['p']
        except alpaca.common.exceptions.APIError as e:
            if e.status_code == 500 and num_retries < MAX_RETRIES:
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

def trade_sgov():
    milk = None
    recent_price = None
    rhianna = 0 
    continuityChecker = 0
    buy_sell_QtyList_index = 1
    buy_sell_QtyList = []
    while True:
        #identify final 15 minutes of the market for the month
        current_time = datetime.datetime.now(datetime.timezone.utc).astimezone(pytz.timezone('US/Eastern'))
        ham = ((current_time.hour == 15 or current_time.hour == 16) and current_time.minute == 45 and (current_time.day == calendar.monthrange(current_time.year, current_time.month)[1] and current_time.month not in [3, 6, 8]) or
       (current_time.hour == 15 or current_time.hour == 16) and current_time.minute == 45 and current_time.day == 28 and current_time.month in [3, 6] or
       (current_time.hour == 15 or current_time.hour == 16) and current_time.minute == 45 and current_time.day == 30 and current_time.month == 8 or
       (current_time.hour == 12 or current_time.hour == 13) and current_time.minute == 45 and current_time.day == 29 and current_time.month == 11)
        
        #get current price
        current_price = get_current_price()

        print(f'Recent Price: {recent_price} Milk: {milk} Current Price: {current_price}')
        sellQty = int((float(account.portfolio_value)-float(account.cash))/float(current_price))
        buyQty = int(float(account.cash)/float(current_price))
        if ham:
            OrdersResponse = requests.get(OrdersURL, headers=OrdersHeaders)
            if sellQty > 0 and (OrdersResponse.text == "[]"):
                limit_order_data = LimitOrderRequest(
                            symbol="SGOV",
                            limit_price=current_price,
                            qty=sellQty,
                            side=OrderSide.SELL,
                            time_in_force=TimeInForce.IOC
                        )
                limit_order = trading_client.submit_order(
                    order_data=limit_order_data
                )
                print(f'Ham Sell Order placed: {sellQty} shares at ${current_price}')
                buy_sell_QtyList_newAddition = str(buy_sell_QtyList_index) + str(f'Ham Sell Order placed: {sellQty} shares at ${current_price}')
                buy_sell_QtyList_index +=1
                buy_sell_QtyList.append(buy_sell_QtyList_newAddition)
        elif not ham:
            if recent_price is not None:
                if current_price <= recent_price - 0.01:
                    OrdersResponse = requests.get(OrdersURL, headers=OrdersHeaders)
                    if buyQty > 0 and (OrdersResponse.text == "[]"):
                        # Place a buy order
                        limit_order_data = LimitOrderRequest(
                            symbol="SGOV",
                            limit_price=current_price,
                            qty= buyQty,
                            side=OrderSide.BUY,
                            time_in_force=TimeInForce.IOC
                        )
                        limit_order = trading_client.submit_order(
                            order_data=limit_order_data
                        )
                        # recent_price = current_price
                        print(f'Buy Order placed: {buyQty} shares at ${current_price}')
                        buy_sell_QtyList_newAddition = str(buy_sell_QtyList_index) + str(f'Buy Order placed: {buyQty} shares at ${current_price}')
                        buy_sell_QtyList_index +=1
                        buy_sell_QtyList.append(buy_sell_QtyList_newAddition)
                elif current_price >= recent_price + 0.01:
                    OrdersResponse = requests.get(OrdersURL, headers=OrdersHeaders)
                    if sellQty > 0 and (OrdersResponse.text == "[]"):
                        # Place a sell order
                        limit_order_data = LimitOrderRequest(
                            symbol="SGOV",
                            limit_price=current_price,
                            qty=sellQty,
                            side=OrderSide.SELL,
                            time_in_force=TimeInForce.IOC
                        )
                        limit_order = trading_client.submit_order(
                            order_data=limit_order_data
                        )
                        # recent_price = current_price
                        print(f'Sell Order placed: {sellQty} shares at ${current_price}')
                        buy_sell_QtyList_newAddition = str(buy_sell_QtyList_index) + str(f'Sell Order placed: {sellQty} shares at ${current_price}')
                        buy_sell_QtyList_index +=1
                        buy_sell_QtyList.append(buy_sell_QtyList_newAddition)
        #if the available trade is still good, it should still try to execute
        if milk != current_price:
            recent_price = milk
            milk = current_price
        balance_change = float(account.equity) - float(account.last_equity)
        print(f'Today\'s portfolio balance change: ${balance_change}')
        for item in buy_sell_QtyList:
            print(item)
        if continuityChecker > 1000:
            continuityChecker = 0
        print(continuityChecker)
        continuityChecker+=1
        if rhianna < 1:
            milk= current_price
            recent_price = current_price
            rhianna += 1

        # if recent_price != current_price:
        #         recent_price = current_price
trade_sgov()
        