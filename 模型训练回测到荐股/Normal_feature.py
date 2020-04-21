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

def main(startdate, enddate, save_path1, save_path2):
    base_path = 'stock'
    
    market_map = {'主板':0, '中小板':1}
    exchange_map = {'SZSE':0, 'SSE':1}
    is_hs_map = {'S':0, 'N':1, 'H':2}
    
    area_map = {'深圳': 0, '北京': 1, '吉林': 2, '江苏': 3, '辽宁': 4, '广东': 5, '安徽': 6, '四川': 7, '浙江': 8,
                '湖南': 9, '河北': 10, '新疆': 11, '山东': 12, '河南': 13, '山西': 14, '江西': 15, '青海': 16, 
                '湖北': 17, '内蒙': 18, '海南': 19, '重庆': 20, '陕西': 21, '福建': 22, '广西': 23, '天津': 24, 
                '云南': 25, '贵州': 26, '甘肃': 27, '宁夏': 28, '黑龙江': 29, '上海': 30, '西藏': 31}
    
    industry_map = {'银行': 0, '全国地产': 1, '生物制药': 2, '环境保护': 3, '区域地产': 4, '酒店餐饮': 5, '运输设备': 6, 
     '综合类': 7, '建筑工程': 8, '玻璃': 9, '家用电器': 10, '文教休闲': 11, '其他商业': 12, '元器件': 13, 
     'IT设备': 14, '其他建材': 15, '汽车服务': 16, '火力发电': 17, '医药商业': 18, '汽车配件': 19, '广告包装': 20, 
     '轻工机械': 21, '新型电力': 22, '饲料': 23, '电气设备': 24, '房产服务': 25, '石油加工': 26, '铅锌': 27, '农业综合': 28,
     '批发业': 29, '通信设备': 30, '旅游景点': 31, '港口': 32, '机场': 33, '石油贸易': 34, '空运': 35, '医疗保健': 36,
     '商贸代理': 37, '化学制药': 38, '影视音像': 39, '工程机械': 40, '软件服务': 41, '证券': 42, '化纤': 43, '水泥': 44, 
     '专用机械': 45, '供气供热': 46, '农药化肥': 47, '机床制造': 48, '多元金融': 49, '百货': 50, '中成药': 51, '路桥': 52, 
     '造纸': 53, '食品': 54, '黄金': 55, '化工原料': 56, '矿物制品': 57, '水运': 58, '日用化工': 59, '机械基件': 60, 
     '汽车整车': 61, '煤炭开采': 62, '铁路': 63, '染料涂料': 64, '白酒': 65, '林业': 66, '水务': 67, '水力发电': 68, 
     '互联网': 69, '旅游服务': 70, '纺织': 71, '铝': 72, '保险': 73, '园区开发': 74, '小金属': 75, '铜': 76, '普钢': 77, 
     '航空': 78, '特种钢': 79, '种植业': 80, '出版业': 81, '焦炭加工': 82, '啤酒': 83, '公路': 84, '超市连锁': 85, 
     '钢加工': 86, '渔业': 87, '农用机械': 88, '软饮料': 89, '化工机械': 90, '塑料': 91, '红黄酒': 92, '橡胶': 93, '家居用品': 94,
     '摩托车': 95, '电器仪表': 96, '服饰': 97, '仓储物流': 98, '纺织机械': 99, '电器连锁': 100, '装修装饰': 101, '半导体': 102, 
     '电信运营': 103, '石油开采': 104, '乳制品': 105, '商品城': 106, '公共交通': 107, '船舶': 108, '陶瓷': 109}
    
    def JudgeST(x):
        if 'ST' in x:
            return 1
        else:
            return 0
    
    def GetMA(df, col_name, rolling_day):
        tmp_array = df[col_name].values.reshape(-1)
        df.loc[ rolling_day:, col_name + '_'+str(rolling_day)] = (tmp_array[0:-rolling_day] - 
                                                                  tmp_array[rolling_day:]) / tmp_array[0:-rolling_day]
        return df
    
    col = ['ma'+str(i) for i in [5, 10, 13, 21, 30]] + ['ma_v_'+str(i) for i in [5, 10, 13, 21, 30]]
    
    company_info = pd.read_csv(os.path.join(base_path, 'company_info.csv'), encoding='utf-8')
    company_info['is_ST'] = company_info['name'].apply(JudgeST)
    # 丢弃一些多余的信息
    company_info.drop(['index', 'symbol', 'fullname'], axis=1, inplace=True)
    company_info.dropna(inplace=True)
    company_info['market'] = company_info['market'].map(market_map)
    company_info['exchange'] = company_info['exchange'].map(exchange_map)
    company_info['is_hs'] = company_info['is_hs'].map(is_hs_map)
    
    
    # 读取指数信息
    stock_index_info = pd.DataFrame()
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
        
        # for day in [5, 10, 13, 21]:
        #     tmp_df['turnover_rate_'+str(day)] = tmp_df['turnover_rate'].rolling(day).mean()
            
        for tmp_col in col:
            for rolling_day in [5]:
                tmp_df = GetMA(tmp_df, tmp_col, rolling_day)
        tmp_list.append(tmp_df)
        
    stock_info = pd.concat(tmp_list)
    stock_info = stock_info.reset_index(drop=True)
    ts_code_map = dict(zip(list(company_info['ts_code']), range(len(company_info))))
    
    
    stock_info = stock_info.reset_index(drop=True)
    stock_info['ts_code_id'] = stock_info['ts_code'].map(ts_code_map)
    
    stock_info['trade_date_id'] = stock_info['trade_date'].map(date_map)
    stock_info['ts_date_id'] = (10000 + stock_info['ts_code_id']) * 10000 + stock_info['trade_date_id']
    stock_info = stock_info.merge(company_info, how='left', on='ts_code')
    stock_info_copy = stock_info.copy()
    
    stock_info_copy.to_csv(save_path2, index=None)
    
    stock_info = stock_info.drop_duplicates(subset=['ts_date_id'])
    
    # -----------------------特征工程
    feature_col = []
    # 获取月份 和 星期几
    def get_weekday(x):
        x = str(x)
        return datetime.datetime.fromtimestamp(time.mktime(time.strptime(x, "%Y%m%d"))).weekday()
    stock_info['month'] = stock_info['trade_date'].apply(lambda x: int(str(x)[4:6]))
    stock_info['weekday'] = stock_info['trade_date'].apply(get_weekday)
    feature_col.append('month')
    feature_col.append('weekday')
    
    
    # 求相对的vol 这里与21均线比较
    stock_info['vol'] = (stock_info['vol'] - stock_info['ma_v_21']) / stock_info['ma_v_21']
    feature_col.append('vol')
    
    
    #转换low colse等
    col = ['open', 'high', 'low', 'high', 'close']
    for tmp_col in col:
        stock_info[tmp_col+'_transform'] = (stock_info[tmp_col] - stock_info['ma21']) / stock_info['ma21']
        feature_col.append(tmp_col+'_transform')
    
    
    # 添加大盘指数信息
    tmp_df = pd.read_csv(os.path.join(base_path,  'OldData', '000001.SH' + '_NormalData.csv'))
    for tmp_col in ['amount', 'close']:
        tmp_df = tmp_df.rename(columns={tmp_col: tmp_col + '_index_000001'})
        stock_info = stock_info.merge(tmp_df[['trade_date', tmp_col + '_index_000001']], on='trade_date', how='left')
    
    for tmp_col in ['amount_index_000001', 'close_index_000001', 'amount', 'close']:
        print(tmp_col)
        for i in range(5):
            tmp_df = stock_info[['ts_date_id', tmp_col]]
            new_col_name = tmp_col + '_shift_{}'.format(i+1)
            tmp_df = tmp_df.rename(columns={tmp_col:new_col_name})
            feature_col.append(new_col_name)
            tmp_df['ts_date_id'] = tmp_df['ts_date_id'] + i + 1
            stock_info = stock_info.merge(tmp_df, how='left', on='ts_date_id')
        for i in range(5):
            new_col_name = tmp_col + '_shift_{}'.format(i+1)
            stock_info[new_col_name] = (stock_info[tmp_col] - stock_info[new_col_name]) / stock_info[new_col_name]
    
    
    feature_col.append('turnover_rate')
    other_col = ['trade_date', 'ts_code', 'open', 'high', 'low', 'close', 'ts_date_id']
    col = feature_col + other_col
    stock_info = stock_info[col]
    stock_info.to_csv(save_path1, index=None)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise Exception('error.')
    # name = 'update'
    name = sys.argv[1]
    enddate = int(sys.argv[2])
    if name == 'all':
        save_path1 = 'stock/features/feature0.csv'
        save_path2 = 'stock/features/stock_info.csv'
        startdate = 20150101
        # enddate = 20200306
        main(startdate, enddate, save_path1, save_path2)
    elif name == 'update':
        save_path1 = 'stock/features_update/feature0.csv'
        save_path2 = 'stock/features_update/stock_info.csv'
        startdate = 20191201
        # enddate = 20200306
        main(startdate, enddate, save_path1, save_path2)       
    