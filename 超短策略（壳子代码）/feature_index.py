# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 08:42:34 2020

@author: hcb
"""
import pandas as pd
import numpy as np
import os

def main():
    base_path = '../stock'
    df = pd.read_csv(os.path.join(base_path,  'OldData', '000001.SH_NormalData.csv'))
    df['rate'] = (df['close'] - df['pre_close']) / df['pre_close']
    df['rate_1'] = df['rate'].shift(1)
    df['rate_2'] = df['rate'].shift(2)
    save_path = 'feature_index.csv'
    df[['trade_date', 'rate_1', 'rate_2', 'rate']].to_csv(save_path, index=None)
    
if __name__ == '__main__':
    main()