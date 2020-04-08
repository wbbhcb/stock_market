# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 17:14:00 2020

@author: hcb
"""
import pandas as pd
import numpy as np
import os
import tushare as ts
from mootdx.quotes import Quotes
import datetime
mytoken = '6e23da5efe6c72a37b1536eb7a5c0a8d0bc0ff02b08e834d6102a8bd' # ***是tushare的api,大家可以自己到tushare上注册获取api,（免费的）
ts.set_token(mytoken)
ts.set_token(mytoken)
save_path = 'stock'
pro = ts.pro_api()

def compute_score(index_df, i):
    score = 0
    tmp_rate = (index_df['close'][i]-index_df['ma3'][i]) / index_df['ma3'][i]
    if tmp_rate>=0:
        score += 1
        
    tmp_rate = (index_df['close'][i]-index_df['ma10'][i]) / index_df['ma10'][i]
    if tmp_rate>=0:
        score += 2

    tmp_rate = (index_df['close'][i]-index_df['ma20'][i]) / index_df['ma20'][i]
    if tmp_rate>=0:
        score += 2

    tmp_rate = (index_df['close'][i]-index_df['ma30'][i]) / index_df['ma30'][i]
    if tmp_rate>=0:
        score += 1
    
    if index_df['ma3_trend'][i] == 1:
        score += 1
    
    if index_df['ma10_trend'][i] == 1:
        score += 2
    elif index_df['ma10_trend'][i] == 0:
        score += 1

    if index_df['ma20_trend'][i] == 1:
        score += 2
    elif index_df['ma20_trend'][i] == 0:
        score += 1

    if index_df['Collapse_sum'][i] > 0:
        score = score - 2
    
    if index_df['rate'][i] > 0.01:
        score = score + 2

    if (index_df['close'][i] - index_df['low'][i])/index_df['low'][i] > 0.015:
        if abs((index_df['close'][i]-index_df['min'][i])/index_df['min'][i])<0.03:
            score = score + 3

    if score < 0:
        score = 0

    if score > 10:
        score=10  
    return score
    

def compute_score2(df, i):
    score = 0
    tmp_rate = (df['close'][i]-df['ma3'][i]) / df['ma3'][i]
    if tmp_rate>=0:
        score += 1
        
    tmp_rate = (df['close'][i]-df['ma10'][i]) / df['ma10'][i]
    if tmp_rate>=0:
        score += 2

    tmp_rate = (df['close'][i]-df['ma20'][i]) / df['ma20'][i]
    if tmp_rate>=0:
        score += 2

    tmp_rate = (df['close'][i]-df['ma30'][i]) / df['ma30'][i]
    if tmp_rate>=0:
        score += 1
    
    if df['ma3_trend'][i] == 1:
        score += 1
    
    if df['ma10_trend'][i] == 1:
        score += 2
    elif df['ma10_trend'][i] == 0:
        score += 1

    if df['ma20_trend'][i] == 1:
        score += 2
    elif df['ma20_trend'][i] == 0:
        score += 1
    
    if df['ma30_trend'][i] == 1:
        score += 1

    if score < 0:
        score = 0

    if score > 10:
        score=10  
    return score


def comput_space(startdate=20040101, enddate=20200407):
    index_df = pro.index_daily(ts_code='000001.SH',
                         start_date=startdate,
                         end_date=enddate,
                         fields='ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, '
                                'vol, amount')
    index_df = index_df.sort_values('trade_date', ascending=True).reset_index(drop=True)
    
    index_df['rate'] = (index_df['close'] - index_df['pre_close']) / index_df['pre_close']
    index_df['Collapse'] = index_df['rate'] < -0.02
    index_df['Collapse_sum'] = index_df['Collapse'].rolling(4).sum()
    
    index_df['min'] = index_df['close'].rolling(180).min()
    index_df['max'] = index_df['close'].rolling(180).max()
    index_df = index_df.sort_values('trade_date', ascending=True).reset_index(drop=True)
    
    # 计算均线
    for day in [3, 10, 20, 30]:
        index_df['ma'+str(day)] = index_df.close.rolling(day).mean()
    col = ['ma3', 'ma10', 'ma20', 'ma30']
    tmp_df2 = index_df[col].shift(1)
    tmp_df3 = index_df[col].shift(2)
    for tmp_col in col:
        index_df[tmp_col + '_trend'] = 0
        # tmp_df[tmp_col + '_shift_1'] = tmp_df2[tmp_col]
        # tmp_df[tmp_col _ 'shift_2'] = tmp_df3[tmp_col]
        index_df['rate1'] = (tmp_df2[tmp_col] - tmp_df3[tmp_col]) / (tmp_df3[tmp_col] + 0.00001)
        index_df['rate2'] = (index_df[tmp_col] - tmp_df2[tmp_col]) / (tmp_df2[tmp_col] + 0.00001)
        idx = (index_df['rate1'] > 0.002) #& (index_df['rate2'] > 0.006)
        index_df.loc[idx, tmp_col + '_trend'] = 1 # 趋势向上
    
        idx = (index_df['rate1'] < -0.004) #& (index_df['rate2'] < -0.003)
        index_df.loc[idx, tmp_col + '_trend'] = 2 # 趋势向下
        
    index_df = index_df.loc[31:].reset_index(drop=True)
    score_list = []
    for i in range(len(index_df)):
        score = compute_score(index_df, i) / 10
        score_list.append(score)
    return score_list, list(index_df['trade_date'])

def get_data(symbol='510300', start_date=datetime.date(2012,4,1), 
             end_date=datetime.date(2020,4,3), save=False):
    
    # now = start_date
    df_list = []
    client = Quotes.factory(market='std')
    s_idx = 0
    while True:
        # t = str(now.year)+str(now.month).zfill(2)+str(now.day).zfill(2)
        df = client.bars(symbol=symbol, start=s_idx, frequency=0, offset=800)
        if df is None:
            break
        df_list.append(df)
        s_idx += 800
        # now = now + datetime.timedelta(1)
    df_list = pd.concat(df_list)
    if save:
        df_list.to_csv(symbol+'.csv', index=None)
    return df_list
    
        
if __name__ == '__main__':
    score_list, date_list = comput_space()