"""
获得每日涨跌停统计, tushare limit_list接口获得是每日个股涨跌停情况，
以下代码为，统计每日涨停数和跌停数
"""
import pandas as pd
import numpy as np
import os
base_path = 'stock'
base_path = os.path.join(base_path, 'OhterData')

filename = []
U = []
D = []

for file in os.listdir(base_path):

    if 'limit_list' in file:
        filename.append(file)
        df = pd.read_csv(os.path.join(base_path, file))
        tmp = len(df[df['limit'] == 'U'])
        U.append(tmp)
        tmp = len(df[df['limit'] == 'D'])
        D.append(tmp)


def mysplit(x):
    x = x.split('.')[0]
    x = x.split('_')[-1]
    return x


df = pd.DataFrame()
df['file'] = filename
df['U'] = U
df['D'] = D
df['date'] = df['file'].apply(mysplit)

df = df.sort_values('date').reset_index(drop=True)

df.to_csv('limit.csv', index=None)