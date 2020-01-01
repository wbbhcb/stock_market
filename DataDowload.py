import tushare as ts
import pandas as pd
import os
import time

"""
获取历史数据
"""

mytoken = '10a361cde441a9e7aea6e98441a8bea0fbb2c82ac8298899ee22fbfd'
ts.set_token(mytoken)
ts.set_token(mytoken)
save_path = 'F:\stock'
pro = ts.pro_api()


def getNoramlData():
    #获取基础信息数据，包括股票代码、名称、上市日期、退市日期等
    pool = pro.stock_basic(exchange='',
                           list_status='L',
                           adj='qfq',
                           fields='ts_code,symbol,name,area,industry,fullname,list_date, market,exchange,is_hs')
    #print(pool.head())

    # 因为穷没开通创业板和科创板权限，这里只考虑主板和中心板
    pool = pool[pool['market'].isin(['主板', '中小板'])].reset_index()
    pool.to_csv(os.path.join(save_path, 'company_info.csv'), index=False, encoding='ANSI')

    print('获得上市股票总数：', len(pool)-1)
    j = 1
    for i in pool.ts_code:
        print('正在获取第%d家，股票代码%s.' % (j, i))
        #接口限制访问200次/分钟，加一点微小的延时防止被ban
        path = os.path.join(save_path, 'OldData', i + '_NormalData.csv')
        j += 1
        # if os.path.exists(path):
        #     continue
        time.sleep(0.301)
        df = pro.daily(ts_code=i,
                       start_date=startdate,
                       end_date=enddate,
                       fields='ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount')
        df = df.sort_values('trade_date', ascending=True)
        df.to_csv(path, index=False)


def getIndexData():
    # 上交所指数信息
    df = pro.index_basic(market='SSE')
    df.to_csv(os.path.join(save_path, 'SSE.csv'), index=False, encoding='ANSI')

    # 深交所指数信息
    df = pro.index_basic(market='SZSE')
    df.to_csv(os.path.join(save_path, 'SZSE.csv'), index=False, encoding='ANSI')

    # 获取指数历史信息
    # 这里获取几个重要的指数 【上证综指，上证50，上证A指，深证成指，深证300，中小300，创业300，中小板综，创业板综】
    index = ['000001.SH', '000016.SH', '000002.SH', '399001.SZ', '399007.SZ', '399008.SZ', '399012.SZ', '399101.SZ',
             '399102.SZ']
    for i in index:
        path = os.path.join(save_path, 'OldData', i + '_NormalData.csv')
        df = pro.index_daily(ts_code=i,
                             start_date=startdate,
                             end_date=enddate,
                             fields='ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, '
                                    'vol, amount')
        df = df.sort_values('trade_date', ascending=True)
        df.to_csv(path, index=False)


if __name__ == '__main__':
    #设置起始日期
    startdate = '20120101'
    enddate = '20191226'
    #主程序
    getNoramlData()
    getIndexData()
