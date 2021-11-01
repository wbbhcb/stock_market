import numpy as np
import pandas as pd


class Account:

    def __init__(self, money_init, start_date='', end_date='', stop_loss_rate=-0.03, stop_profit_rate=0.05,
                 max_hold_period=5):
        self.cash = money_init  # 现金
        self.stock_value = 0  # 股票价值
        self.market_value = money_init  # 总市值
        self.stock_name = []  # 记录持仓股票名字
        self.stock_id = []  # 记录持仓股票id
        self.buy_date = []  # 记录持仓股票买入日期
        self.stock_num = []  # 记录持股股票剩余持股数量
        self.stock_price = []  # 记录股票的买入价格
        self.start_date = start_date
        self.end_date = end_date
        self.stock_asset = []  # 持仓数量
        self.buy_rate = 0.0003  # 买入费率
        self.buy_min = 5  # 最小买入费率
        self.sell_rate = 0.0003  # 卖出费率
        self.sell_min = 5  # 最大买入费率
        self.stamp_duty = 0.001  # 印花税
        # self.info = []  # 记录所有买入卖出记录
        self.max_hold_period = max_hold_period  # 最大持股周期
        self.hold_day = []  # 股票持股时间
        self.sell_price = []
        self.sell_kind = []
        self.buy_price = []

        self.cost = []  # 记录真实花费
        # self.profit = []  # 记录每次卖出股票收益

        self.stop_loss_rate = stop_loss_rate  # 止损比例
        self.stop_profit_rate = stop_profit_rate  # 止盈比例

        self.victory = 0  # 记录交易胜利次数
        self.defeat = 0  # 记录失败次数

        self.cash_all = [money_init]  # 记录每天收盘后所持现金
        self.stock_value_all = [0.0]  # 记录每天收盘后所持股票的市值
        self.market_value_all = [money_init]  # 记录每天收盘后的总市值
        self.max_market_value = money_init  # 记录最大的市值情况，用来计算回撤
        self.min_after_max_makret_value = money_init  # 记录最大市值后的最小市值
        self.max_retracement = 0  # 记录最大回撤率
        self.info = pd.DataFrame(
            columns=['ts_code', 'name', 'buy_price', 'buy_date', 'buy_num', 'sell_price', 'sell_date',
                     'profit'])

    # 股票买入
    def buy_stock(self, buy_date, stock_id, stock_price, buy_num):
        """
        :param buy_date: 买入日期
        :param stock_id: 买入股票的id
        :param stcok_price: 买入股票的价格
        :param buy_num: 买入股票的数量
        :return:
        """
        tmp_len = len(self.info)
        if stock_id not in self.stock_id:
            self.stock_id.append(stock_id)
            self.buy_date.append(buy_date)
            self.stock_price.append(stock_price)
            self.hold_day.append(1)

            self.info.loc[tmp_len, 'ts_code'] = stock_id
            self.info.loc[tmp_len, 'buy_price'] = stock_price
            self.info.loc[tmp_len, 'buy_date'] = buy_date

            # 更新市值、现金及股票价值
            tmp_money = stock_price * buy_num
            service_change = tmp_money * self.buy_rate
            if service_change < self.buy_min:
                service_change = self.buy_min
            tmp_cash = self.cash - tmp_money - service_change
            if tmp_cash < 0:
                buy_num = buy_num - 100
                tmp_money = stock_price * buy_num
                service_change = tmp_money * self.buy_rate
                if service_change < self.buy_min:
                    service_change = self.buy_min
                self.cash = self.cash - tmp_money - service_change
            else:
                self.cash = tmp_cash
            self.info.loc[tmp_len, 'buy_num'] = buy_num
            self.stock_num.append(buy_num)

            # self.stock_value = self.stock_value + tmp_money
            # self.market_value = self.cash + self.stock_value

            self.cost.append(tmp_money + service_change)

            info = str(buy_date) + '  买入 ' + stock_id + ' (' + stock_id + ') ' \
                   + str(int(buy_num)) + '股，股价：' + str(stock_price) + ',花费：' + str(round(tmp_money, 2)) + ',手续费：' \
                   + str(round(service_change, 2)) + '，剩余现金：' + str(round(self.cash, 2))
            print(info)

            # self.info.append(info)

    def sell_stock(self, sell_date, stock_id, sell_price, sell_num, flag):
        """
        :param sell_date: 卖出日期
        :param stock_name: 卖出股票的名字
        :param stock_id: 卖出股票的id
        :param sell_price: 卖出股票的价格
        :param sell_num: 卖出股票的数量
        :return:
        """

        if stock_id not in self.stock_id:
            raise TypeError('该股票未买入')
        idx = self.stock_id.index(stock_id)

        tmp_money = sell_num * sell_price
        service_change = tmp_money * self.sell_rate
        if service_change < self.sell_min:
            service_change = self.sell_min
        stamp_duty = self.stamp_duty * tmp_money
        self.cash = self.cash + tmp_money - service_change - stamp_duty

        service_change = stamp_duty + service_change
        # self.profit.append(tmp_money-service_change)
        profit = tmp_money - service_change - self.cost[idx]

        if flag == 1:
            info = str(sell_date) + '  止盈卖出' + ' (' + stock_id + ') ' \
                   + str(int(sell_num)) + '股，股价：' + str(sell_price) + ',收入：' + str(round(tmp_money, 2)) + ',手续费：' \
                   + str(round(service_change, 2)) + '，剩余现金：' + str(round(self.cash, 2)) \
                   + '，最终盈利：' + str(round(profit, 2))
            self.victory += 1
        elif flag == 2:
            info = str(sell_date) + '  止损卖出' + ' (' + stock_id + ') ' \
                   + str(int(sell_num)) + '股，股价：' + str(sell_price) + ',收入：' + str(round(tmp_money, 2)) + ',手续费：' \
                   + str(round(service_change, 2)) + '，剩余现金：' + str(round(self.cash, 2)) \
                   + '，最终亏损：' + str(round(profit, 2))
            self.defeat += 1

        print(info)
        idx = (self.info['ts_code'] == stock_id) & self.info['sell_date'].isna()
        self.info.loc[idx, 'sell_date'] = sell_date
        self.info.loc[idx, 'sell_price'] = sell_price
        self.info.loc[idx, 'profit'] = profit

    # 更新信息
    def update(self, day):
        # 更新市值等信息
        # print(stock_price)
        stock_price = np.array(self.buy_price)
        stock_num = np.array(self.stock_num)
        self.stock_value = np.sum(stock_num * stock_price)
        self.market_value = self.cash + self.stock_value
        self.market_value_all.append(self.market_value)
        self.stock_value_all.append(self.stock_value)
        self.cash_all.append(self.cash)

        if self.max_market_value < self.market_value:
            self.max_market_value = self.market_value
            self.min_after_max_makret_value = 99999999999
        else:
            if self.min_after_max_makret_value > self.market_value:
                self.min_after_max_makret_value = self.market_value
                #  计算回撤率
                retracement = np.abs((self.max_market_value - self.min_after_max_makret_value) / self.max_market_value)
                if retracement > self.max_retracement:
                    self.max_retracement = retracement

    def BackTest(self, buy_df, day_time, buy_price='close'):
        """
        :param buy_df: 可以买入的股票，输入为DataFrame
        :param all_df: 所有股票的DataFrame
        :param index_df: 指数对应时间的df
        :return:
        """
        for i in range(len(day_time)):
            day = day_time[i]
            tmp_idx = buy_df['day'] == day

            # tmp_df = buy_df.loc[tmp_idx].reset_index()
            tmp_df = buy_df.loc[tmp_idx].sort_values('prob', ascending=False).reset_index()

            # 先卖后买
            # ----卖股

            for j in range(len(self.stock_id)):
                stock_id = self.stock_id[j]
                # stock_name = self.stock_name[j]
                sell_num = self.stock_num[j]  # 假设全卖出去
                sell_price = self.sell_price[j]
                sell_kind = self.sell_kind[j]
                self.sell_stock(day_time[i], stock_id, sell_price, sell_num, sell_kind)

            # 重置
            self.stock_num = []
            self.stock_id = []
            self.stock_name = []
            self.buy_date = []
            self.stock_price = []
            self.hold_day = []
            self.cost = []
            self.sell_kind = []
            self.sell_price = []
            self.buy_price = []

            # ----买股
            if len(tmp_df) != 0:
                for j in range(len(tmp_df)):
                    money = self.market_value * 0.2
                    if money > self.cash:
                        money = self.cash
                    if money < 5000:  # 假设小于5000RMB，就不买股票
                        break

                    buy_num = (money / tmp_df[buy_price][j]) // 100
                    if buy_num == 0:
                        continue
                    buy_num = buy_num * 100
                    self.buy_stock(day_time[i],
                                   tmp_df['name'][j], tmp_df[buy_price][j], buy_num)

                    self.buy_price.append(tmp_df[buy_price][j])
                    # 第二天卖出的价格
                    self.sell_price.append(tmp_df['next_open'][j])
                    if tmp_df['next_open'][j] > tmp_df['close_price'][j]:
                        self.sell_kind.append(1)
                    else:
                        self.sell_kind.append(2)

            # 更新持股周期及信息
            self.update(day_time[i])

        try:
            self.info[['buy_date', 'sell_date', 'buy_num']] = self.info[['buy_date', 'sell_date', 'buy_num']].astype(int)
        except:
            pass
