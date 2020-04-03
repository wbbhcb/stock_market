import easyquotation
import tushare as ts
import os
from tqdm import tqdm
import pandas as pd
import numpy as np


def get_feature(stock_info, df):
    """
    stock_info:字典形式输入
    df:股票历史信息 dataframe
    """
    feature = []
    
    # 计算20日收盘价 ma
    tmp_list = list(df.iloc[-19:]['close'])
    tmp_list.append(stock_info['now'])
    feature.append(np.mean(tmp_list))
    return feature
    

# 涨跌停统计
def count_limit(tmp_dict):
    up = 0
    down = 0
    for tmp_keys in tqdm(tmp_dict.keys()):
        stock_info = tmp_dict[tmp_keys]
        if 'ST' in stock_info['name']:
            if stock_info['now'] >= round(stock_info['close'] * 1.05, 2):
                up += 1
            elif stock_info['now'] <= round(stock_info['close'] * 0.95, 2):
                down += 1
        else:
            if stock_info['now'] >= round(stock_info['close'] * 1.1, 2):
                up += 1
            elif stock_info['now'] <= round(stock_info['close'] * 0.9, 2):
                down += 1            
    return up, down 


def handle_history(base_path, tmp_dict):

    company_info = pd.read_csv(os.path.join(base_path, 'company_info.csv'), encoding='gbk')
    company_info['is_ST'] = company_info['name'].apply(JudgeST)
    col = ['trade_date', 'ts_code', 'open', 'high', 'low', 'close',
           'change', 'pct_chg', 'vol', 'amount', 'turnover_rate', 'volume_ratio']
    df_list = []
    features = []
    ts_codes = []
    for tmp_name in tqdm(company_info['ts_code']):
        file_path = os.path.join(base_path, 'OldData', tmp_name + '_NormalData.csv')
        df = pd.read_csv(file_path)
        df = df.sort_values('trade_date', ascending=True).reset_index(drop=True)
        
        try:
            if 'SH' in tmp_name:
                stock_info = tmp_dict['sh' + tmp_name[:6]]
            elif 'SZ' in tmp_name:
                stock_info = tmp_dict['sz' + tmp_name[:6]]
            else:
                print(tmp_name)
        except:
            # 可能有一些停牌企业
            continue
            
        feature = get_feature(stock_info, df)
        features.append(feature)
        ts_codes.append(tmp_name)
        # break
    
    return features, ts_codes


quotation = easyquotation.use('tencent') # 新浪 ['sina'] 腾讯 ['tencent', 'qq']
tmp_dict = quotation.market_snapshot(prefix=True) # prefix 参数指定返回的行情字典中的股票代码 key 是否带 sz/sh 前缀
base_path = 'stock'
features, ts_codes = handle_history(base_path, tmp_dict)

up, down = count_limit(tmp_dict)
