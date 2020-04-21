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
    base_path = '../stock' # 前复权数据
    
    company_info = pd.read_csv(os.path.join(base_path, 'company_info.csv'), encoding='gbk')
    # 丢弃一些多余的信息
    company_info.drop(['index', 'symbol', 'fullname'], axis=1, inplace=True)
    company_info.dropna(inplace=True)
    
    
    tmp_df = pd.read_csv(os.path.join(base_path,  'OldData', '000001.SH_NormalData.csv'))
    tmp_list = list(tmp_df['trade_date'].sort_values())
    date_map = dict(zip(tmp_list, range(len(tmp_list))))
    
    # 读取股票交易信息
    stock_info = pd.DataFrame()
    remove_stock = []
    tmp_list = []
    for ts_code in tqdm.tqdm(company_info['ts_code']):
        try:
            tmp_df = pd.read_csv(os.path.join(base_path,  'OldData', ts_code + '_NormalData.csv')) 
        except:
            continue
            pass
        # 还需要去除一些停牌时间很久的企业，后期加
        if len(tmp_df) < 100:  # 去除一些上市不久的企业
            remove_stock.append(ts_code)
            continue
        
        tmp_df = tmp_df[(tmp_df['trade_date']>=startdate)&(tmp_df['trade_date']<=enddate)].reset_index(drop=True)
        tmp_df = tmp_df.sort_values('trade_date', ascending=True).reset_index(drop=True)
        
        # 明天收盘
        tmp_df['next_close'] = tmp_df['close'].shift(-1)
        tmp_list.append(tmp_df)
        # break
    stock_info = pd.concat(tmp_list)
    stock_info = stock_info.reset_index(drop=True)
    
    other_col = ['trade_date', 'ts_code', 'open', 'high', 'low', 'close', 'pre_close', 'next_close']
    col = other_col
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
        save_path1 = 'feature_stock2.csv'
        startdate = 20150101
        # enddate = 20200306
        main(startdate, enddate, save_path1)
    elif name == 'update':
        save_path1 = 'feature_stock2.csv'
        startdate = 20191201
        # enddate = 20200306
        main(startdate, enddate, save_path1)       
    