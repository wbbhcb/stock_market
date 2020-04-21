# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 20:29:34 2020

@author: hcb
"""

import numpy as np
import pandas as pd
import os
import tqdm
import sys
import pickle


def main(startdate, enddate):

    base_path1 = 'stock/features_update'
    base_path2 = 'stock/features'
    
    # startdate = 20200309
    # enddate = 20200309
    
    stock_info_copy = pd.read_csv(os.path.join(base_path1, 'stock_info.csv'))
    stock_info = pd.read_csv(os.path.join(base_path1, 'feature0.csv'))
    stock_info.drop(['open', 'high', 'low', 'close'], axis=1, inplace=True)
    stock_info = stock_info[(stock_info['trade_date']>=startdate)&(stock_info['trade_date']<=enddate)].reset_index(drop=True)
    stock_info_copy = stock_info_copy[(stock_info_copy['trade_date']>=startdate)&(stock_info_copy['trade_date']<=enddate)].reset_index(drop=True)
    
    stock_info['high-close'] = stock_info['high_transform'] - stock_info['close_transform']
    stock_info['close-low'] = stock_info['close_transform'] - stock_info['low_transform']
    stock_info['close-open'] = stock_info['close_transform'] - stock_info['open_transform']
    
    tmp_df = stock_info_copy[['name', 'ts_code']].drop_duplicates()
    dict_name = dict(zip(tmp_df['ts_code'], tmp_df['name']))
    stock_info['name'] = stock_info['ts_code'].map(dict_name)
    
    
    # 添加涨跌停信息
    limit_info = pd.read_csv(os.path.join(base_path2, 'limit.csv'))
    limit_info['U-D'] = limit_info['U'] - limit_info['D']
    limit_info.drop(['U', 'D'], axis=1, inplace=True)
    limit_info = limit_info.rename(columns={'date':'trade_date'})
    stock_info = stock_info.merge(limit_info, on='trade_date', how='left')
    del limit_info
    
    feature_col = ['month', 'weekday', 'vol', 'open_transform', 'high_transform',
           'low_transform', 'close_transform',
           'amount_index_000001_shift_1', 'amount_index_000001_shift_3', 
           'amount_index_000001_shift_5', 'close_index_000001_shift_1',
           'close_index_000001_shift_3','close_index_000001_shift_5',
           'amount_shift_1', 'amount_shift_3', 'amount_shift_5', 'close_shift_1', 'close_shift_3',
            'close_shift_5', 'turnover_rate', 'U-D']
    
    stock_info.dropna(inplace=True)
    stock_info = stock_info.reset_index(drop=True)
    # stock_info = stock_info[stock_info['trade_date']==20200309].reset_index(drop=True)
    stock_info.to_csv('tmp.csv', index=None)
    val_data = stock_info[feature_col]
    
    with open('model.pickle', 'rb+') as f:
        clf = pickle.load(f)
        
    pred = clf.predict(val_data, num_iteration=clf.best_iteration)
    df_result = pd.DataFrame(pred)
    df_result['trade_date'] = stock_info['trade_date']
    df_result['ts_code'] = stock_info['ts_code']
    df_result['label'] = np.round((pred > 0.5))
    tmp_df = df_result[df_result['label'] == 1].sort_values(['trade_date', 0],
                                                            ascending=[True, False])
    tmp_df.to_csv('stock.csv', index=None)
# tmp_df[tmp_df['trade_date']==20200304]

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise Exception('error.')
    # name = 'update'
    startdate = int(sys.argv[1])
    enddate = int(sys.argv[2])
    main(startdate, enddate)