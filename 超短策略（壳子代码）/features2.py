# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 19:06:38 2020

@author: hcb
"""

# 模型训练
import numpy as np
import pandas as pd
import os
import tqdm
import datetime
import time
import sys

def main(startdate, enddate, save_path1):
    base_path = '../stock' 
    company_info = pd.read_csv(os.path.join(base_path, 'company_info.csv'), encoding='gbk')
    # 丢弃一些多余的信息
    company_info.drop(['index', 'symbol', 'fullname'], axis=1, inplace=True)
    company_info.dropna(inplace=True)
    
    
    tmp_df = pd.read_csv(os.path.join(base_path, 'OldData', '000001.SH_NormalData.csv'))
    tmp_list = list(tmp_df['trade_date'].sort_values())
    date_map = dict(zip(tmp_list, range(len(tmp_list))))
    
    base_path = 'F:\\code\\stock' # 未复权数据
    # 读取股票交易信息
    stock_info = pd.DataFrame()
    remove_stock = []
    tmp_list = []
    for ts_code in tqdm.tqdm(company_info['ts_code']):
        try:
            tmp_df = pd.read_csv(os.path.join(base_path,  ts_code + '_NormalData.csv')) 
        except:
            continue
            pass
        # 还需要去除一些停牌时间很久的企业，后期加
        if len(tmp_df) < 100:  # 去除一些上市不久的企业
            remove_stock.append(ts_code)
            continue
        # break
        tmp_df = tmp_df[(tmp_df['trade_date']>=startdate)&(tmp_df['trade_date']<=enddate)].reset_index(drop=True)
        
        tmp_df = tmp_df.sort_values('trade_date', ascending=True).reset_index(drop=True)
        
        # 明天收盘
        tmp_df['next_close'] = tmp_df['close'].shift(-1)
        
        
        # 开盘价等特征
        tmp_df['open_transform'] = tmp_df['open'] / tmp_df['pre_close']
        tmp_df['close_transform'] = tmp_df['close'] / tmp_df['pre_close']
        tmp_df['high_transform'] = tmp_df['high'] / tmp_df['pre_close']
        tmp_df['low_transform'] = tmp_df['low'] / tmp_df['pre_close']
        tmp_df['zhenfu'] = tmp_df['high_transform'] - tmp_df['low_transform']
        
        tmp_df['open_transform_3'] = tmp_df['open_transform'].rolling(3).mean()
        # tmp_df['open_transform_5'] = tmp_df['open_transform'].rolling(5).mean()
        tmp_df['close_3'] = tmp_df['close'].rolling(3).mean()
        tmp_df['close_3'] = tmp_df['close'] / tmp_df['close_3']
        
        # 是否涨停
        tmp_df['limit_price1'] = tmp_df['pre_close'] * 1.1
        tmp_df['limit_price2'] = tmp_df['pre_close'] * 1.05
        tmp_df['limit_price1'] = tmp_df['limit_price1'].apply(lambda x: round(x+0.0000001,2))
        tmp_df['limit_price2'] = tmp_df['limit_price2'].apply(lambda x: round(x+0.0000001,2))
        tmp_df['zhangting'] = ((tmp_df['limit_price1'] <= tmp_df['close']) | \
                                (tmp_df['limit_price2'] == tmp_df['close'])) & (tmp_df['close']==tmp_df['high']) \
            
        

        col = ['open_transform', 'close_transform', 'high_transform', 'low_transform',
               'zhenfu', 'zhangting']
        for tmp_col in col:
            for day in range(2):
                tmp_df[tmp_col+'_'+str(day+1)] = tmp_df[tmp_col].shift(day+1)
                
        tmp_list.append(tmp_df)
        # break
        
    stock_info = pd.concat(tmp_list)
    stock_info = stock_info.reset_index(drop=True)
    
    # -----------------------特征工程
    feature_col = ['turnover_rate'] + col
    
    for tmp_col in col:
        for day in range(2):
            feature_col.append(tmp_col+'_'+str(day+1))
            
    # 获取月份 和 星期几
    def get_weekday(x):
        x = str(x)
        return datetime.datetime.fromtimestamp(time.mktime(time.strptime(x, "%Y%m%d"))).weekday()
    stock_info['month'] = stock_info['trade_date'].apply(lambda x: int(str(x)[4:6]))
    stock_info['weekday'] = stock_info['trade_date'].apply(get_weekday)
    feature_col.append('month')
    feature_col.append('weekday')
    
    
    # feature_col.append('turnover_rate')
    other_col = ['trade_date', 'ts_code', ] # 'open', 'high', 'low', 'close', 'next_close'
    col = feature_col + other_col
    stock_info = stock_info[col]
    stock_info.to_csv(save_path1, index=None)

if __name__ == '__main__':
    # if len(sys.argv) != 3:
    #     raise Exception('error.')
    # name = 'update'
    # name = sys.argv[1]
    # enddate = int(sys.argv[2])
    name='all'
    enddate = 20200402
    if name == 'all':
        save_path1 = 'feature_stock1.csv'
        startdate = 20150101
        # enddate = 20200306
        main(startdate, enddate, save_path1)
    elif name == 'update':
        save_path1 = 'feature_stock1.csv'
        startdate = 20191201
        # enddate = 20200306
        main(startdate, enddate, save_path1)       
    