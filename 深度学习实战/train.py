# -*- coding: utf-8 -*-
"""
Created on Thu May 14 15:39:44 2020

@author: hcb
"""
import pandas as pd
from tqdm import tqdm
import os
from config import config
import numpy as np
import random
from model import build_model
import keras
import tensorflow as tf
from sklearn.metrics import roc_auc_score, precision_score

def auc(y_true, y_pred):
    return tf.py_func(roc_auc_score, (y_true, y_pred), tf.double)


conf = config()

def read_data(base_path):
    # val_data

    stock_path = os.path.join(base_path, 'OldData')
    company_info = pd.read_csv(os.path.join(base_path, 'company_info.csv')) # encoding='utf-8'
    company_info.drop(['index', 'symbol', 'fullname'], axis=1, inplace=True)
    
    # 指数信息
    df = pd.read_csv(os.path.join(base_path,  'OldData', '000001.SH_NormalData.csv'))
    df = df[df['trade_date']>=conf.trn_date_start]
    df = df.sort_values('trade_date', ascending=True).reset_index(drop=True)
    
    date_df = pd.DataFrame()
    date_df['trade_date'] = df['trade_date']
    date_df['amount_index'] = df['amount']
    date_df['close_index'] = df['close']
    # date_map = dict(zip(df['trade_date'], range(len(df['trade_date']))))
    
    trn_idx = df[(df['trade_date']>=conf.trn_date_start)&(df['trade_date']<=conf.trn_date_end)].index
    val_idx = df[(df['trade_date']>=conf.val_date_start)&(df['trade_date']<=conf.val_date_end)].index
    test_idx = df[(df['trade_date']>=conf.test_date_start)].index
    
    trn_data, val_data, test_data = dict(), dict(), dict()
    v = df[['close', 'amount']].values
    trn_data['index'] = v[trn_idx]
    val_data['index'] = v[val_idx]
    test_data['index'] = v[test_idx]
    code_list = []
    trn_code_list = []
    
    # k=0
    for ts_code in tqdm(company_info['ts_code']):
        # ts_code = '000538.SZ'
        # k=k+1
        # if k>100:
        #     break
        path = os.path.join(stock_path, ts_code+'_NormalData.csv')
        df = pd.read_csv(path)
        df = date_df.merge(df[['trade_date', 'amount', 'close']], on='trade_date', how='left')
        tmp_df = df[df['close'].isna()]
        idx = tmp_df.index
        
        for i in idx:
            if i == 0:
                continue
            
            # 用上一个交易日的收盘价填充
            df.loc[i, 'close'] = df['close'][i-1] 
            df.loc[i, 'amount'] = 0
        
        # 标签制作这边不管停牌，用填充好的数据进行标签制作
        df['label'] = df['close'].shift(-1)
        df['label'] = df['label'] > df['close']
        df['label'] = df['label'].apply(lambda x: int(x))
        
        df = df.dropna(subset=['close']).reset_index(drop=True) # 删除前面还没上市的日子
        trn_idx = df[(df['trade_date']>=conf.trn_date_start)&(df['trade_date']<=conf.trn_date_end)].index
        val_idx = df[(df['trade_date']>=conf.val_date_start)&(df['trade_date']<=conf.val_date_end)].index
        test_idx = df[(df['trade_date']>=conf.test_date_start)].index
        v = df[['close', 'amount', 'close_index', 'amount_index']].values
        label = df['label'].values
        trn_data[ts_code] = {'data':v[trn_idx],'label':label[trn_idx]}
        val_data[ts_code] = {'data':v[val_idx],'label':label[val_idx]}
        test_data[ts_code] = {'data':v[test_idx],'label':label[test_idx],
                              'trade_date':df['trade_date'].values[test_idx]}
        code_list.append(ts_code)
        if len(trn_idx) >= 100:
            trn_code_list.append(ts_code)
        # break
    
    return trn_data, val_data, test_data, code_list, trn_code_list


# 标准化
def transform(x):
    ave = np.mean(x, axis=0)
    std = np.std(x, axis=0)
    x = (x-ave) / (std + 0.00001)
    return x 
    

def trndata_gen(trn_data, trn_code_list):
    random.shuffle(trn_code_list)
    # x = np.array()
    while True:
        # 随机选取batch只股票
        tmp_code_list = random.sample(trn_code_list, conf.batch_size)
        x_batch = []
        y_batch = []
        for i in range(conf.batch_size):
            # 对每只股票随机取一段时间
            y = trn_data[tmp_code_list[i]]['label']
            x = trn_data[tmp_code_list[i]]['data']
            tmp_idx = int(np.random.rand() * (len(x)-conf.day))
            x = x[tmp_idx:tmp_idx+conf.day]
            y = y[tmp_idx+conf.day-1]
            x_batch.append(transform(x))
            y_batch.append(y)
        yield np.array(x_batch), np.array(y_batch)


def valdata_gen(x_all, y_all):
    while True:
        for i in range(0, len(x_all), conf.batch_size):
            x = x_all[i:i+conf.batch_size]
            y = y_all[i:i+conf.batch_size]
            yield np.array(x), np.array(y)    


def get_valdata():
    x_all = []
    y_all = []
    for tmp_code in code_list:
        y = val_data[tmp_code]['label']
        x = val_data[tmp_code]['data']        
        if len(x) < conf.day:
            continue
        for i in range(len(x)-conf.day+1):
            x_all.append(transform(x[i:i+conf.day]))
            y_all.append(y[i+conf.day-1])
    return np.array(x_all), np.array(y_all)


def predict(model, test_data, code_list):
    df_list = []
    for tmp_code in tqdm(code_list):
        y_batch = []
        x_batch = []
        
        y = test_data[tmp_code]['label']
        x = test_data[tmp_code]['data']
        if len(x) < conf.day:
            continue
        for i in range(len(x)-conf.day+1):
            x_batch.append(transform(x[i:i+conf.day]))
            y_batch.append(y[i+conf.day-1])
        
        y_pred = model.predict(np.array(x_batch))
        tmp_df = pd.DataFrame()
        tmp_df['label'] = y_batch
        tmp_df['pred'] = y_pred
        tmp_df['ts_code'] = tmp_code
        tmp_df['trade_date'] = test_data[tmp_code]['trade_date'][conf.day-1:] 
        df_list.append(tmp_df)
    
    df_list = pd.concat(df_list)
    df_list.to_csv('pred.csv', index=None)       
    for threshold in [0.5, 0.6, 0.7, 0.8, 0.9]:
        print('threshold: %.1f, precision:%.3f'%(threshold, 
            precision_score(df_list['label'], df_list['pred']>threshold)))
    
    
if __name__ == '__main__':
    base_path = conf.base_path
    if not os.path.exists('model'):
        os.mkdir('model')
    # 这部分读取数据耗时长，可以先保存下来
    trn_data, val_data, test_data, code_list, trn_code_list = read_data(base_path)
    model = build_model()
    x_all_val, y_all_val = get_valdata()
    ckpt = keras.callbacks.ModelCheckpoint(
        filepath='model/model.h5',mode='max',
        monitor='val_auc', save_best_only=True,verbose=1)
    model.compile(loss='binary_crossentropy',
                optimizer='adam', metrics=[auc])
    
    model.fit_generator(
        generator=trndata_gen(trn_data, trn_code_list),
        steps_per_epoch=200,
        epochs=50,
        initial_epoch=0,
        validation_data=valdata_gen(x_all_val, y_all_val),
        validation_steps=np.ceil(len(x_all_val)/conf.batch_size),
        max_q_size=10,
        # use_multiprocessing=True,
        callbacks=[ckpt],
        # workers=4
        )
    model.save_weights('model/model_final.h5')
    model.load_weights('model/model.h5')
    predict(model, test_data, code_list)
    # pass
    