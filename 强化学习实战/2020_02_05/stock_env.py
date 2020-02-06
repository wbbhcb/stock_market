# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 15:16:28 2020

@author: hcb
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class stock:
    
    def __init__(self, trend, init_money=10000, window_size=16):
        
        self.n_actions = 3 # 动作数量
        self.n_features = 16 # 特征数量   
        self.trend = trend # 收盘数据
        self.init_money = init_money # 初始化资金
        
        self.window_size = window_size #滑动窗口大小
        self.half_window = window_size // 2
        
    def reset(self):
        self.hold_money = self.init_money # 持有资金
        self.buy_num = 0 # 买入数量
        self.hold_num = 0 # 持有股票数量
        self.stock_value = 0 # 持有股票总市值
        self.maket_value = 0 # 总市值（加上现金）
        self.last_value = self.init_money # 上一天市值
        self.total_profit = 0 # 总盈利
        self.t = 0 # 时间
        self.reward = 0 # 收益
        # self.inventory = []
        
        self.states_sell = [] #卖股票时间
        self.states_buy = [] #买股票时间
        
        self.profit_rate_account = [] # 账号盈利
        self.profit_rate_stock = [] # 股票波动情况
        return self.get_state(0)
    
    def get_state(self, t): #某t时刻的状态
        window_size = self.window_size + 1
        d = t - window_size + 1
		#早期天数不够窗口打小，用0时刻来凑，即填补相应个数
        block = self.trend[d : t + 1] if d >= 0 else -d * [self.trend[0]] + self.trend[0 : t + 1]
        res = []
        for i in range(window_size - 1):
            res.append((block[i + 1] - block[i])/(block[i]+0.0001)) #每步收益
        return np.array(res) #作为状态编码
    
    def step(self, action, show_log=False):
        
        if action == 1 and self.hold_money >= self.trend[self.t]*100 and self.t < (len(self.trend) - self.half_window):
            # 买入股票
            self.buy_num = self.hold_money // self.trend[self.t] // 100 # 买入手数
            self.hold_num += self.buy_num
            self.stock_value += self.trend[self.t] * 100 * self.buy_num
            self.hold_money -= self.trend[self.t] * 100 * self.buy_num     
            self.states_buy.append(self.t)
            if show_log:
                print('day %d: buy 1 unit at price %f'% (self.t, self.trend[self.t]))
        
        elif action == 2 and self.hold_num > 0:
            # 卖出股票              
            self.hold_money += self.trend[self.t] * self.hold_num * 100
            self.hold_num = 0
            self.stock_value = 0
            self.states_sell.append(self.t)
            if show_log:
                print(
                    'day %d, sell 1 unit at price %f, total balance %f,'
                    % (self.t, self.trend[self.t], self.hold_money)
                )
            
        self.stock_value = self.trend[self.t] * self.hold_num * 100
        # print(stock_value, hold_money)
        self.maket_value = self.stock_value + self.hold_money 
        self.total_profit = self.maket_value - self.init_money
        self.reward = ((self.maket_value - self.last_value) / self.last_value)
        self.last_value = self.maket_value
        
        self.profit_rate_account.append((self.maket_value - self.init_money) / self.init_money)
        self.profit_rate_stock.append((self.trend[self.t] - self.trend[0]) / self.trend[0])
        done = False
        self.t = self.t + 1
        if self.t == len(self.trend) - 1:
            done = True
        s_ = self.get_state(self.t)
        reward = self.reward
        
        return s_, reward, done
    
    def get_info(self):
        return self.states_sell, self.states_buy, self.profit_rate_account, self.profit_rate_stock  
    
    def draw(self):
        # 绘制结果
        states_sell, states_buy, profit_rate_account, profit_rate_stock = self.get_info()
        invest = profit_rate_account[-1]
        total_gains = self.total_profit
        close = self.trend
        fig = plt.figure(figsize = (15,5))
        plt.plot(close, color='r', lw=2.)
        plt.plot(close, 'v', markersize=8, color='k', label = 'selling signal', markevery = states_sell)
        plt.plot(close, '^', markersize=8, color='m', label = 'buying signal', markevery = states_buy)        
        plt.title('total gains %f, total investment %f%%'%(total_gains, invest))
        plt.legend()
        plt.savefig('trade.png')
        plt.close()
        
        fig = plt.figure(figsize = (15,5))
        plt.plot(profit_rate_account, label='my account')
        plt.plot(profit_rate_stock, label='stock')
        plt.legend()
        plt.savefig('profit.png')
        plt.close()
        
        
        
        