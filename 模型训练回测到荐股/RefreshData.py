# -*- coding: utf-8 -*-
import tushare as ts
import pandas as pd
import os
import time
import numpy as np
from tqdm import tqdm

"""
获取历史数据
"""

mytoken = 'd5f93a567929568429d17063571985cb4964dd42e515d96f1b515fb7'
ts.set_token(mytoken)
ts.set_token(mytoken)
save_path = 'stock'
pro = ts.pro_api()

def get_mean_data(df):
    for day in [5, 10, 13, 21, 30, 60, 120]:
        df['ma'+str(day)] = df['close'].rolling(day).mean()
        df['ma_v_'+str(day)] = df['vol'].rolling(day).mean()
    return df

def RefreshNoramlData(startdate, enddate):
    #获取基础信息数据，包括股票代码、名称、上市日期、退市日期等
    col = ['trade_date', 'ts_code', 'open', 'high', 'low', 'close', 'pre_close',
       'change', 'pct_chg', 'vol', 'amount', 'turnover_rate', 'volume_ratio',
       'ma5', 'ma_v_5', 'ma10', 'ma_v_10', 'ma13', 'ma_v_13', 'ma21',
       'ma_v_21', 'ma30', 'ma_v_30', 'ma60', 'ma_v_60', 'ma120', 'ma_v_120']
    pool = pro.stock_basic(exchange='',
                           list_status='L',
                           adj='qfq',
                           fields='ts_code,symbol,name,area,industry,fullname,list_date, market,exchange,is_hs')
    # print(pool.head())

    # 因为穷没开通创业板和科创板权限，这里只考虑主板和中心板
    pool = pool[pool['market'].isin(['主板', '中小板'])].reset_index()
    pool.to_csv(os.path.join(save_path, 'company_info.csv'), index=False)
    # print(pool)
    print('获得上市股票总数：', len(pool)-1)
    k = 1
    for i in pool.ts_code:
        print('正在获取第%d家，股票代码%s.' % (k, i))
        path = os.path.join(save_path, 'OldData', i + '_NormalData.csv')
        
        df = ts.pro_bar(ts_code=i, adj='qfq', start_date=startdate, end_date=enddate,
                ma=[5, 10, 13, 21, 30, 60, 120], factors=['tor', 'vr'])
        

        if df is None:
            continue
        if list(df.columns) != col:
            raise Exception('列不一致')
        k += 1
        if len(df) == 0:
            print('no data')
            continue
        df = df.sort_values('trade_date', ascending=True)
        if not os.path.exists(path):
            df.to_csv(path, index=False)
        else:
            df2 = pd.read_csv(path)
            drop_index = []
            for j in range(len(df)):
                if int(df['trade_date'][j]) in list(df2['trade_date']):       
                    drop_index.append(j)
                    print(str(df['trade_date'][j])+'已有')
            
            if len(drop_index) != 0:
                df.drop(drop_index, axis=0, inplace=True)
            if len(df) == 0:
                # df2.drop_duplicates('trade_date', inplace=True)
                # df2.to_csv(path, index=False)
                continue
            df2 = pd.concat((df2, df))
            df2 = get_mean_data(df2)
            df2.to_csv(path, index=False)
            # f = open(path, 'a+', encoding='utf-8')
            # col = list(df.columns)
            # for j in range(len(df)):
            #     write_info = ''
            #     for j2 in range(len(col)):
            #         write_info = write_info + str(df[col[j2]][j])
            #         if j2 != len(col) - 1:
            #             write_info = write_info + ','
            #     f.write(write_info + '\n')
            # f.close()


def RefreshIndexData(startdate, enddate):
    # 上交所指数信息
    df = pro.index_basic(market='SSE')
    df.to_csv(os.path.join(save_path, 'SSE.csv'), index=False, encoding='gbk')

    # 深交所指数信息
    df = pro.index_basic(market='SZSE')
    df.to_csv(os.path.join(save_path, 'SZSE.csv'), index=False, encoding='gbk')

    # 获取指数历史信息
    # 这里获取几个重要的指数 【上证综指，上证50，上证A指，深证成指，深证300，中小300，创业300，中小板综，创业板综】
    index = ['000001.SH', '000016.SH', '000002.SH', '399001.SZ', '399007.SZ', '399008.SZ', '399012.SZ', '399101.SZ',
             '399102.SZ']
    for i in index:
        path = os.path.join(save_path, 'OldData', i + '_NormalData.csv')
        df = pro.index_daily(ts_code=i,
                             start_date=20120101,
                             end_date=enddate,
                             fields='ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, '
                                    'vol, amount')
        df = df.sort_values('trade_date', ascending=True)
        df.to_csv(path, index=False)


def update_up_down(days):
    days = np.sort(days)
    #  统计涨跌停股票
    j = 0
    for tmp_day in tqdm(days):
        j = j + 1
        df = pro.limit_list(trade_date=str(tmp_day))
        path = os.path.join(save_path, 'OhterData', 'limit_list_' + str(tmp_day) + '.csv')
        time.sleep(0.601)
        if len(df) == 0:
            continue
        df.to_csv(path, index=False, encoding='utf-8')
    

def main(startdate, enddate=None):
    # startdate = '20191227'
    if enddate == None:
        enddate = startdate
        
    #主程序
    RefreshNoramlData(startdate, enddate)
    RefreshIndexData(startdate, enddate)
    i = int(startdate)
    days = []
    while True:
        days.append(i)
        if i <= int(enddate):
            i += 1
        else:
            break
    update_up_down(days)    

if __name__ == '__main__':
    #设置起始日期
    import sys
    if len(sys.argv) != 3:
        raise Exception('error.')

    startdate = sys.argv[1]
    enddate = sys.argv[2]
    main(startdate,enddate)