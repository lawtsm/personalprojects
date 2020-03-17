# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 16:23:37 2020

@author: lolen
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import os, warnings
warnings.filterwarnings("ignore")
import seaborn as sns
import matplotlib.pyplot as plt

import plotly
print("plotly version: {}".format(plotly.__version__))
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot

import datetime
from datetime import date

today = date.today()
print("Today's date:", today)

print("Current Working Directory " , os.getcwd())

try:
    # Change the current working Directory    
    os.chdir("C:/Users/lolen/Desktop/personalprojects")
    print('Directory changed')
except OSError:
    print("Can't change the Current Working Directory") 

'''Extract page source from url'''
stocksummaryurl = 'https://finance.yahoo.com/quote/AMD?p=AMD'
r_summary = requests.get(stocksummaryurl)
s_summary = BeautifulSoup(r_summary.text, 'html.parser')

stockpriceurl = 'https://finance.yahoo.com/quote/AMD/history?p=AMD'
r_price = requests.get(stockpriceurl)
s_price = BeautifulSoup(r_price.text, 'html.parser')

stock = stocksummaryurl[-3:]
'''Print to text file for browsing'''
'''
txtfile = open("source.txt", "w")
txtfile.write(str(s_price.prettify()))
txtfile.close()

txtfile = open("source0.txt", "w")
txtfile.write(str(s_summary.prettify()))
txtfile.close()
'''

dates = []
'''open, high, low, close, adj close, volume'''
p_open = []
p_high = []
p_low = []
p_close = []
p_adjclose = []
p_volume = []

for price in s_price.find_all('tbody'):
    for daily in price.find_all('tr'):
        n = 0
        for dt in daily.find_all('td', attrs={'class': 'Py(10px) Ta(start) Pend(10px)'}):
            if datetime.datetime.strptime(dt.text, '%b %d, %Y').date() != today:
                dates.append(dt.text)
                for price in daily.find_all('td', attrs={'class': 'Py(10px) Pstart(10px)'}):
                    n = n + 1
                    for item in price.find('span'):
                        if n == 1:
                            p_open.append(float(item))
                        elif n == 2:
                            p_high.append(float(item))
                        elif n == 3:
                            p_low.append(float(item))
                        elif n == 4:
                            p_close.append(float(item))
                        elif n == 5:
                            p_adjclose.append(float(item))
                        else:
                            p_volume.append(item)

previousclose = s_summary.find('td', attrs={'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'PREV_CLOSE-value'})
openprice = s_summary.find('td', attrs={'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'OPEN-value'})
bid = s_summary.find('td', attrs={'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'BID-value'})
ask = s_summary.find('td', attrs={'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'ASK-value'})
dayrange = s_summary.find('td', attrs={'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'DAYS_RANGE-value'})
yearrange = s_summary.find('td', attrs={'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'FIFTY_TWO_WK_RANGE-value'})
volume = s_summary.find('td', attrs={'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'TD_VOLUME-value'})
avgvolume = s_summary.find('td', attrs={'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'AVERAGE_VOLUME_3MONTH-value'})
marketcap = s_summary.find('td', attrs={'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'MARKET_CAP-value'})
beta = s_summary.find('td', attrs={'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'BETA_5Y-value'})
peratio = s_summary.find('td', attrs={'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'PE_RATIO-value'})
epsratio = s_summary.find('td', attrs={'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'EPS_RATIO-value'})
earningsdate = s_summary.find('td', attrs={'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'EARNINGS_DATE-value'})
targetprice = s_summary.find('td', attrs={'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'ONE_YEAR_TARGET_PRICE-value'})



pricedf = pd.DataFrame({'X': np.arange(len(dates)-1,-1,-1), 'Date': dates,
                        'P_open': p_open, 'P_high': p_high, 'P_low': p_low,
                        'P_close': p_close, 'P_adjclose': p_adjclose,
                        'P_volume': p_volume})

pricedf = pricedf.iloc[::-1]
pricedf.reset_index(drop=True, inplace=True)
pricedf.Date = pricedf.Date.apply(lambda x: datetime.datetime.strptime(x, '%b %d, %Y').date())

pricedf_m = pd.melt(pricedf, id_vars=['X'],
                    value_vars=['P_open', 'P_high', 'P_low', 'P_close'], 
                    var_name='Type', value_name='Price')
pricedf_m.Price = pricedf_m.Price.astype('float')


#Using Seaborn
#ax = sns.lineplot(x='X', y='Price', hue='Type', data=pricedf_m)
#ax.set_title('Most recent {} days'.format(len(dates)))
#ax.legend(('Open', 'Day high', 'Day low', 'Closing'))

fig = go.Figure()
template = "<b>Day</b>: %{x}<br>" + "<b>%{text}</b>: %{y:$}<br>" + "<extra></extra>"
l = pricedf.shape[0]
fig.add_trace(go.Scatter(x=list(pricedf.Date), y=list(pricedf.P_open), mode='lines', name='Opening', text=["Opening"]*l, hovertemplate=template, line_color='deepskyblue', showlegend=True))
fig.add_trace(go.Scatter(x=list(pricedf.Date), y=list(pricedf.P_low), mode='lines', name='Day low', text=["Day low"]*l, hovertemplate=template, line_color='violet', showlegend=True))
fig.add_trace(go.Scatter(x=list(pricedf.Date), y=list(pricedf.P_high), mode='lines', name='Day high', text=["Day high"]*l, hovertemplate=template, line_color='black', showlegend=True))
fig.add_trace(go.Scatter(x=list(pricedf.Date), y=list(pricedf.P_close), mode='lines', name='Closing', text=["Closing"]*l, hovertemplate=template, line_color='red', showlegend=True))

fig.update_layout(title_text=stock, xaxis_title='Date', yaxis_title='Price (USD)',
                  xaxis=dict(rangeselector=dict(buttons=list([dict(count=14,label='14d',step='day',stepmode='backward'), 
                                                              dict(count=30,label='30d',step='day',stepmode='backward'),
                                                              dict(step="all")])), 
                             rangeslider=dict(visible=True), type='date'))
#fig.update_xaxes(nticks=10)
plot(fig, auto_open=True)

#https://plot.ly/python/selection-events/
