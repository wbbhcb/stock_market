# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 19:06:38 2020

@author: hcb
"""

# 模型训练
import pandas as pd
import os
import tqdm
import datetime
import time


# 未复权数据特征
def main(startdate, enddate, save_path1, basepath):
    
    company_info = pd.read_csv(os.path.join(basepath, 'company_info.csv'))
    # 丢弃一些多余的信息
    company_info.drop(['index', 'symbol', 'fullname'], axis=1, inplace=True)
    company_info.dropna(inplace=True)
    
    base_path = os.path.join(basepath, 'DailyData2')
    # 读取股票交易信息
    remove_stock = []
    tmp_list = []
    for ts_code in tqdm.tqdm(company_info['ts_code']):
        try:
            tmp_df = pd.read_csv(os.path.join(base_path,  ts_code + '.csv'))
        except:
            continue
            pass
        # 还需要去除一些停牌时间很久的企业，后期加
        if len(tmp_df) < 100:  # 去除一些上市不久的企业
            remove_stock.append(ts_code)
            continue

        tmp_df = tmp_df[(tmp_df['trade_date'] >= startdate)&(tmp_df['trade_date'] <= enddate)].reset_index(drop=True)
        # break
        tmp_df = tmp_df.sort_values('trade_date', ascending=True).reset_index(drop=True)

        # 开盘价等特征
        tmp_df['open_transform'] = tmp_df['open'] / tmp_df['pre_close']
        tmp_df['close_transform'] = tmp_df['close'] / tmp_df['pre_close']
        tmp_df['high_transform'] = tmp_df['high'] / tmp_df['pre_close']
        tmp_df['low_transform'] = tmp_df['low'] / tmp_df['pre_close']

        tmp_df['zhenfu'] = tmp_df['high_transform'] - tmp_df['low_transform']
        tmp_df['open_transform_3'] = tmp_df['open_transform'].rolling(3).mean()
        tmp_df['close_3'] = tmp_df['pre_close'].rolling(3).mean()

        # 是否涨停,读取涨停价格
        tmp_df2 = pd.read_csv(os.path.join(basepath, 'LimitPrice', ts_code + '.csv'))
        tmp_df = tmp_df.merge(tmp_df2[['up_limit', 'down_limit', 'trade_date']], on='trade_date', how='left')
        tmp_df['is_limit'] = (tmp_df['close'] == tmp_df['up_limit']) | (tmp_df['close'] == tmp_df['down_limit'])

        # 平均成交价格 和 close相比
        tmp_df['pingjun'] = tmp_df['amount']/tmp_df['vol']*10
        tmp_df['pingjun_3'] = tmp_df['pingjun'].rolling(3).mean()

        tmp_df['pingjun'] = tmp_df['pingjun'] / tmp_df['pre_close']
        tmp_df['pingjun_3'] = tmp_df['pingjun_3'] / tmp_df['close_3']

        tmp_df['close_3'] = tmp_df['close'] / tmp_df['close_3']
        
        col = ['open_transform', 'close_transform', 'high_transform', 'low_transform',
               'zhenfu',  'turnover_rate',]

        for tmp_col in col:
            for day in range(2):
                tmp_df[tmp_col+'_shift_'+str(day+1)] = tmp_df[tmp_col].shift(day+1)
                
        tmp_list.append(tmp_df)
        # break
    stock_info = pd.concat(tmp_list)
    stock_info = stock_info.reset_index(drop=True)
    
    # -----------------------特征工程
    feature_col = ['open_transform_3', 'close_3', 'pingjun_3', 'pingjun'] + col
    
    for tmp_col in col:
        for day in range(2):
            feature_col.append(tmp_col+'_shift_'+str(day+1))
            
    # 获取月份 和 星期几
    def get_weekday(x):
        x = str(x)
        return datetime.datetime.fromtimestamp(time.mktime(time.strptime(x, "%Y%m%d"))).weekday()

    stock_info['month'] = stock_info['trade_date'].apply(lambda x: int(str(x)[4:6]))
    stock_info['weekday'] = stock_info['trade_date'].apply(get_weekday)
    feature_col.append('month')
    feature_col.append('weekday')

    other_col = ['trade_date', 'ts_code', 'is_limit']  # 'open', 'high', 'low', 'close', 'next_close'
    col = feature_col + other_col
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
        save_path1 = 'feature_stock2.csv'
        startdate = 20150101
        # enddate = 20200306
        main(startdate, enddate, save_path1, base_path)