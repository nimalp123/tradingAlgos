import datetime as dt
from datetime import timedelta
from pandas_datareader import data as pdr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
import yfinance as yfin
import requests
from bs4 import BeautifulSoup
yf = yfin
yfin.pdr_override()
# %matplotlib inline


def fetch_top_100_stocks():
    # Example: Fetch stocks from the S&P 500 as a proxy for a large set of significant US stocks
    sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
    # Fetch data for these tickers from yfinance
    for ticker in sp500_tickers:
      sp500_tickers[sp500_tickers.index(ticker)] = ticker.replace(".", "-")
    data = yfin.Tickers(sp500_tickers)
    # Placeholder for market cap data
    market_caps = {}
    for ticker in sp500_tickers:
      stock = data.tickers[ticker]
      try:
          # Attempt to fetch market cap and store it

          market_caps[ticker] = stock.info['marketCap']
      except:
          # Handle cases where market cap is unavailable or an error occurs
          qwertyuiopasdfghjklzxcvbnm = 0
    # Sort tickers by market cap, descending, and select top 100
    top_100_tickers = sorted(market_caps, key=market_caps.get, reverse=True)[:100]
    return str(" ".join(top_100_tickers))

def return_risk_free_rate():
    def get_html_data(url):
        response = requests.get(url)

        if response.status_code == 200:
            return response.text
        else:
            print(f"Error {response.status_code}: Unable to fetch the HTML data.")
            return None

    def parse_html_data(html_data):
        soup = BeautifulSoup(html_data, 'html.parser')
        price_meta = soup.find('meta', {'name': 'price'})

        if price_meta:
            return price_meta['content']
        else:
            print("Error: Unable to find the price meta tag.")
            return None

    marketwatch_url = "https://www.marketwatch.com/investing/bond/tmubmusd01m?countrycode=bx"
    marketwatch_html_data = get_html_data(marketwatch_url)

    if marketwatch_html_data:
        risk_free_rate = parse_html_data(marketwatch_html_data)
        risk_free_rate = float(risk_free_rate[:-1])/100
        return risk_free_rate
class optimalPortfolio:

  p_ret = [] # Define an empty array for portfolio returns
  p_vol = [] # Define an empty array for portfolio volatility
  p_weights = [] # Define an empty array for asset weights

  def __init__(self, stocklist, numOfPortfolios): #takes a list of stocks and a number of random portfolio combinations to create
    self.end = dt.datetime.now()
    self.start = self.end - timedelta(days=100)
    self.p_ret = [] # Define an empty array for portfolio returns
    self.p_vol = [] # Define an empty array for portfolio volatility
    self.p_weights = [] # Define an empty array for asset weights
    self.numOfPortfolios = int(numOfPortfolios)
    df=pdr.get_data_yahoo(stocklist, self.start, self.end)
    df= df.Close
    num_assets = len(df.columns)
    ind_er = df.resample('Y').last().pct_change().mean() #Expected yearly returns for individual companies
    self.ind_er = ind_er
    covariance_matrix = df.pct_change().apply(lambda x: np.log(1+x)).cov()

    for portfolio in range(self.numOfPortfolios):
      weights = np.random.random(num_assets)
      weights = weights/np.sum(weights) #make sure weight = 1 by diviing by the cumulative sum
      self.p_weights.append(weights)
      returns = np.dot(weights, self.ind_er)
      self.p_ret.append(returns)
      var = covariance_matrix.mul(weights, axis=0).mul(weights, axis=1).sum().sum()# Portfolio Variance
      sd = np.sqrt(var) # Daily standard deviation
      annual_sd = sd*np.sqrt(250) # Annual standard deviation AKA volatility
      self.p_vol.append(annual_sd)

    data = {'Returns':self.p_ret, 'Volatility':self.p_vol}

    for counter, symbol in enumerate(df.columns.tolist()):
      data[symbol+' weight'] = [w[counter] for w in self.p_weights]
    portfolios  = pd.DataFrame(data)
    self.portfolios = portfolios

  def minVolPort(self):  #find the #find the portfolio with the least volatility
    min_vol_port = self.portfolios.iloc[self.portfolios['Volatility'].idxmin()]
    print(min_vol_port)

  def optRiskyPort(self, riskFactor): #find the optimal risky portfolio by using the sharpe ratio
    rf = riskFactor  #risk factor AKA risk-free rate of 1%
    optimalRiskyPort = self.portfolios.iloc[((self.portfolios['Returns']-rf)/self.portfolios['Volatility']).idxmax()]
    return optimalRiskyPort
#@title Index 100 { form-width: "300px" }
# AAPL GOOGL GOOG MSFT AMZN META NVDA
#
input_string = "AAPL GOOGL GOOG MSFT AMZN META NVDA"
stocklist = input_string.split()
# print(stocklist)
numOfRandPort = 2000 # of runs
# 2000000000
# BRK-B AAPL MSFT AMZN TSLA PEP COST GOOGL NVDA JPM
steve = optimalPortfolio(stocklist, numOfRandPort)
print(steve.optRiskyPort(return_risk_free_rate()))
  # def graphOfEF(self, riskFactor): #graph both portfolio with the least volatility(red star) and the the optimal risky portfolio(green star)
  #   min_vol_port = self.portfolios.iloc[self.portfolios['Volatility'].idxmin()]
  #   rf = riskFactor
  #   optimalRiskyPort = self.portfolios.iloc[((self.portfolios['Returns']-rf)/self.portfolios['Volatility']).idxmax()]
  #   plt.subplots(figsize=(10, 10))
  #   plt.scatter(self.portfolios['Volatility'], self.portfolios['Returns'],marker='o', s=10, alpha=0.3)
  #   plt.scatter(min_vol_port[1], min_vol_port[0], color='r', marker='*', s=500)
  #   plt.scatter(optimalRiskyPort[1], optimalRiskyPort[0], color='g', marker='*', s=500)