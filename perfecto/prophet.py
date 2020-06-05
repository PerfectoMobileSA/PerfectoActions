import html
import base64
import json 
from easydict import EasyDict as edict
from collections import Counter
import tzlocal
import pandas
import datetime as dt
import time
from IPython.display import HTML
import glob
import os
import re
import numpy as np
from perfecto.perfectoactions import fig_to_base64


import pandas as pd
from fbprophet import Prophet
df = pd.read_excel('final.xlsx')
# df = df[(df['job/name'] == "VN-Phoenix/SG_BB_RETIREREADYPLUS_RP_INTEGRATED_2")]
df['startDate'] = pandas.to_datetime(pandas.to_datetime(df['startTime']).dt.strftime("%d/%m/%Y"), format='%d/%m/%Y')
df = df.groupby(['startDate']).size().reset_index(name='#status').sort_values('#status', ascending=True)
df = df.rename(columns={'startDate': 'ds', '#status' : 'y'})
print(df.tail())
df['cap'] = 1000
df['floor'] = 0
m = Prophet(seasonality_mode='additive',growth='logistic')
m.fit(df)
future = m.make_future_dataframe(periods=365)
future['cap'] = 1000
future['floor'] = 0
# future.tail()
forecast = m.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

from fbprophet.plot import plot_plotly
import plotly.offline as py
# py.init_notebook_mode()
  
fig = plot_plotly(m, forecast)  # This returns a plotly Figure
py.iplot(fig)
with open("test.html", 'w') as f:
          f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))