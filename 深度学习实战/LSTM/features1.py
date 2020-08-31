# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 19:06:38 2020

@author: hcb
"""

# 模型训练
import pandas as pd
import os
import tqdm


def main(startdate, enddate, save_path1, basepath):
    # base_path # 前复权数据
    
    company_info = pd.read_csv(os.path.join(basepath, 'company_info.csv'))
    # 丢弃一些多余的信息
    company_info.drop(['index', 'symbol', 'fullname'], axis=1, inplace=True)
    company_info.dropna(inplace=True)
    
    # 读取股票交易信息
    remove_stock = []
    tmp_list = []
    for ts_code in tqdm.tqdm(company_info['ts_code']):
        try:
            tmp_df = pd.read_csv(os.path.join(basepath,  'DailyData', ts_code + '.csv'))
        except:
            continue
            pass
        # 还需要去除一些停牌时间很久的企业，后期加
        if len(tmp_df) < 100:  # 去除一些上市不久的企业
            remove_stock.append(ts_code)
            continue
        
        tmp_df = tmp_df[(tmp_df['trade_date'] >= startdate) & (tmp_df['trade_date'] <= enddate)].reset_index(drop=True)
        tmp_df = tmp_df.sort_values('trade_date', ascending=True).reset_index(drop=True)
        
        # 明天收盘
        tmp_df['next_close'] = tmp_df['close'].shift(-1)

        tmp_df['high_10'] = (tmp_df['close'] - tmp_df['high'].rolling(10).max().shift(1)) / tmp_df['high'].rolling(10).max().shift(1)
        tmp_df['high_20'] = (tmp_df['close'] - tmp_df['high'].rolling(20).max().shift(1)) / tmp_df['high'].rolling(20).max().shift(1)

        tmp_df['low_10'] = (tmp_df['close'] - tmp_df['low'].rolling(10).max().shift(1)) / tmp_df['low'].rolling(10).min().shift(1)
        tmp_df['low_20'] = (tmp_df['close'] - tmp_df['low'].rolling(20).max().shift(1)) / tmp_df['low'].rolling(20).min().shift(1)

        tmp_list.append(tmp_df)
        # break

    stock_info = pd.concat(tmp_list)
    stock_info = stock_info.reset_index(drop=True)
    
    other_col = ['trade_date', 'ts_code', 'open', 'high', 'low', 'close', 'pre_close', 'next_close', 'high_10', 'high_20',
                 'low_10', 'low_20']

    col = other_col
    stock_info = stock_info[col]
    stock_info.to_csv(save_path1, index=None)


if __name__ == '__main__':
    # if len(sys.argv) != 3:
    #     raise Exception('error.')
    # name = 'update'
    # name = sys.argv[1]
    # enddate = int(sys.argv[2])
    name = 'all'
    enddate = 20200809
    base_path = 'F:\stock'
    if name == 'all':
        save_path1 = 'feature_stock1.csv'
        startdate = 20140101
        # enddate = 20200306
        main(startdate, enddate, save_path1, base_path)
    elif name == 'update':
        save_path1 = 'feature_stock1.csv'
        startdate = 20200601
        # enddate = 20200306
        main(startdate, enddate, save_path1, base_path)
