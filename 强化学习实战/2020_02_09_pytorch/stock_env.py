# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 15:16:28 2020

@author: hcb
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class stock:
    
    def __init__(self, df, init_money=10000, window_size=6):
        
        self.n_actions = 3 # 动作数量
        self.n_features = window_size # 特征数量   
        self.trend = df['close'].values # 收盘数据
        self.df = df #数据的DataFrame
        self.init_money = init_money # 初始化资金
        
        self.window_size = window_size #滑动窗口大小
        self.half_window = window_size // 2
        
        self.buy_rate = 0.0003  # 买入费率
        self.buy_min = 5  # 最小买入费率
        self.sell_rate = 0.0003  # 卖出费率
        self.sell_min = 5  # 最大买入费率
        self.stamp_duty = 0.001  # 印花税
        
    def reset(self):
        self.hold_money = self.init_money # 持有资金
        self.buy_num = 0 # 买入数量
        self.hold_num = 0 # 持有股票数量
        self.stock_value = 0 # 持有股票总市值
        self.maket_value = 0 # 总市值（加上现金）
        self.last_value = self.init_money # 上一天市值
        self.total_profit = 0 # 总盈利
        self.t = self.window_size // 2 # 时间
        self.reward = 0 # 收益
        # self.inventory = []
        
        self.states_sell = [] #卖股票时间
        self.states_buy = [] #买股票时间
        
        self.profit_rate_account = [] # 账号盈利
        self.profit_rate_stock = [] # 股票波动情况
        return self.get_state(self.t)
    
    def get_state(self, t): #某t时刻的状态
        
        window_size = self.window_size + 1
        d = t - window_size + 1
		#早期天数不够窗口打小，用0时刻来凑，即填补相应个数
        # block = self.trend[d : t + 1] if d >= 0 else (-d * [self.trend[0]] + self.trend[0 : t + 1])
        block = []
        if d<0:
            for i in range(-d):
                block.append(self.trend[0])
            for i in range(t+1):
                block.append(self.trend[i])
        else:
            block = self.trend[d : t + 1]
                
            
        res = []
        for i in range(window_size - 1):
            res.append((block[i + 1] - block[i])/(block[i]+0.0001)) #每步收益
        # res = []
            
        # if self.hold_num > 0:
        #     res.append(1)
        # else:
        #     res.append(0)
            
        # res.append((self.df['close'][t] - self.df['ma21'][t]) / self.df['ma21'][t])
        # res.append((self.df['close'][t] - self.df['ma13'][t]) / self.df['ma13'][t])
        # res.append((self.df['close'][t] - self.df['ma5'][t]) / self.df['ma5'][t])
        # res.append((self.df['vol'][t] - self.df['ma_v_21'][t]) / self.df['ma_v_21'][t])
        return np.array(res) #作为状态编码
    
    def buy_stock(self):       
        # 买入股票
        self.buy_num = self.hold_money // self.trend[self.t] // 100 # 买入手数
        self.buy_num = self.buy_num * 100
        
        # 计算手续费等
        tmp_money = self.trend[self.t] * self.buy_num
        service_change = tmp_money * self.buy_rate
        if service_change < self.buy_min:
            service_change = self.buy_min
        # 如果手续费不够，就少买100股
        if service_change + tmp_money > self.hold_money:
            self.buy_num = self.buy_num - 100
        tmp_money = self.trend[self.t] * self.buy_num
        service_change = tmp_money * self.buy_rate
        if service_change < self.buy_min:
            service_change = self.buy_min
            
        self.hold_num += self.buy_num
        self.stock_value += self.trend[self.t] * self.buy_num
        self.hold_money = self.hold_money - self.trend[self.t] * \
            self.buy_num - service_change
        self.states_buy.append(self.t)
    
    def sell_stock(self, sell_num):
        tmp_money = sell_num * self.trend[self.t]
        service_change = tmp_money * self.sell_rate
        if service_change < self.sell_min:
            service_change = self.sell_min
        stamp_duty = self.stamp_duty * tmp_money
        self.hold_money = self.hold_money + tmp_money - service_change - stamp_duty
        self.hold_num = 0
        self.stock_value = 0
        self.states_sell.append(self.t)
        
    def trick(self):
        if self.df['close'][self.t] >= self.df['ma21'][self.t]:
            return True
        else:
            return False
    
    def step(self, action, show_log=False, my_trick=False):
        
        if action == 1 and self.hold_money >= (self.trend[self.t]*100 + \
            max(self.buy_min, self.trend[self.t]*100*self.buy_rate)) and self.t < (len(self.trend) - self.half_window):
            buy_ = True
            if my_trick and not self.trick(): 
                # 如果使用自己的触发器并不能出发买入条件，就不买
                buy_ = False
            if buy_ : 
                self.buy_stock()
                if show_log:
                    print('day:%d, buy price:%f, buy num:%d, hold num:%d, hold money:%.3f'% \
                          (self.t, self.trend[self.t], self.buy_num, self.hold_num, self.hold_money))
        
        elif action == 2 and self.hold_num > 0:
            # 卖出股票         
            self.sell_stock(self.hold_num)
            if show_log:
                print(
                    'day:%d, sell price:%f, total balance %f,'
                    % (self.t, self.trend[self.t], self.hold_money)
                )
        else:
            if my_trick and self.hold_num>0 and not self.trick():
                self.sell_stock(self.hold_num)
                if show_log:
                    print(
                        'day:%d, sell price:%f, total balance %f,'
                        % (self.t, self.trend[self.t], self.hold_money)
                    )
                    
        self.stock_value = self.trend[self.t] * self.hold_num

        self.maket_value = self.stock_value + self.hold_money 
        self.total_profit = self.maket_value - self.init_money
        
        # self.reward = (self.maket_value - self.last_value) / self.last_value
        reward = (self.trend[self.t + 1] - self.trend[self.t]) / self.trend[self.t]
        if np.abs(reward)<=0.015:
            self.reward = reward * 0.2
        elif np.abs(reward)<=0.03:
            self.reward = reward * 0.7
        elif np.abs(reward)>=0.05:
            if reward < 0 :
                self.reward = (reward+0.05) * 0.1 - 0.05
            else:
                self.reward = (reward-0.05) * 0.1 + 0.05
        
        # reward = (self.trend[self.t + 1] - self.trend[self.t]) / self.trend[self.t]
        if self.hold_num > 0 or action == 2:                                
            self.reward = reward    
            if action == 2:
                self.reward = -self.reward
        else:
            self.reward = -self.reward * 0.1
            # self.reward = 0
        
        self.last_value = self.maket_value
        
        self.profit_rate_account.append((self.maket_value - self.init_money) / self.init_money)
        self.profit_rate_stock.append((self.trend[self.t] - self.trend[0]) / self.trend[0])
        done = False
        self.t = self.t + 1
        if self.t == len(self.trend) - 2:
            done = True
        s_ = self.get_state(self.t)
        reward = self.reward
        
        return s_, reward, done
    
    def get_info(self):
        return self.states_sell, self.states_buy, self.profit_rate_account, self.profit_rate_stock  
    
    def draw(self, save_name1, save_name2):
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
        plt.savefig(save_name1)
        plt.close()
        
        fig = plt.figure(figsize = (15,5))
        plt.plot(profit_rate_account, label='my account')
        plt.plot(profit_rate_stock, label='stock')
        plt.legend()
        plt.savefig(save_name2)
        plt.close()
        
        
        
        