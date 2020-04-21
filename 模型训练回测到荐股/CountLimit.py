# -*- coding: utf-8 -*-
"""
获得每日涨跌停统计, tushare limit_list接口获得是每日个股涨跌停情况，
以下代码为，统计每日涨停数和跌停数
"""
import pandas as pd
import numpy as np
import os
base_path = 'stock'
base_path = os.path.join(base_path, 'OhterData')

def mysplit(x):
    x = x.split('.')[0]
    x = x.split('_')[-1]
    return x

def feature(filename, U, D):
    df = pd.DataFrame()
    df['file'] = filename
    df['U'] = U
    df['D'] = D
    df['date'] = df['file'].apply(mysplit) 
    df = df.sort_values('date').reset_index(drop=True) 
    for day in [5,10,13,21]:
        df['U_max_'+str(day)] = df['U'].rolling(day).max()
        df['D_max_'+str(day)] = df['D'].rolling(day).max()
        df['U_mean_'+str(day)] = df['U'].rolling(day).mean()
        df['D_mean_'+str(day)] = df['D'].rolling(day).mean()
        df['Umean-Dmeam'+str(day)] = df['U_mean_'+str(day)] - df['D_mean_'+str(day)]
    df.drop('file', axis=1, inplace=True)
    return df
        
def extract_all():
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

    df = feature(filename, U, D)    
    save_path = 'stock/features/limit.csv'
    df.to_csv(save_path, index=None)    
    
if __name__ == '__main__':
    extract_all()
    
