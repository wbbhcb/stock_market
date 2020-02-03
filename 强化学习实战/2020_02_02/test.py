import tushare as ts
import pandas as pd
import time
import os

mytoken = '10a361cde441a9e7aea6e98441a8bea0fbb2c82ac8298899ee22fbfd'
ts.set_token(mytoken)
save_path = 'F:\stock'


def maintask():
    pro = ts.pro_api()
    #获取基础信息数据，包括股票代码、名称、上市日期、退市日期等
    pool = pro.stock_basic(exchange='',
                           list_status='L',
                           adj='qfq',
                           fields='ts_code,symbol,name,area,industry,fullname,list_date, market,exchange,is_hs')
    #print(pool.head())
    pool.to_csv(os.path.join(save_path, 'company_info.csv'), index=False, encoding='ANSI')
    print('获得上市股票总数：', len(pool)-1)
    j = 1
    for i in pool.ts_code:
        print('正在获取第%d家，股票代码%s.' % (j, i))
        #接口限制访问200次/分钟，加一点微小的延时防止被ban
        time.sleep(0.301)
        j += 1
        df = pro.daily(ts_code='002195.SZ',
                       start_date=startdate,
                       end_date=enddate,
                       fields='ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount')
        df.to_csv(i + '.csv', index=False)
        break


# if __name__ == '__main__':
#     #设置起始日期
#     startdate = '20120101'
#     enddate = '20191225'
#     #主程序
#     maintask()