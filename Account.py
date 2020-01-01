import numpy as np


class Account:

    def __init__(self, money_init, start_date='', end_date=''):
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
        self.info = []  # 记录所有买入卖出记录
        self.max_hold_period = 5  # 最大持股周期
        self.hold_day = []  # 股票持股时间

        self.cost = []  # 记录真实花费
        # self.profit = []  # 记录每次卖出股票收益

        self.stop_loss_rate = -0.03  # 止损比例
        self.stop_profit_rate = 0.05  # 止盈比例

        self.victory = 0  # 记录交易胜利次数
        self.defeat = 0  # 记录失败次数

        self.cash_all = [money_init]  # 记录每天收盘后所持现金
        self.stock_value_all = [0.0]  # 记录每天收盘后所持股票的市值
        self.market_value_all = [money_init]  # 记录每天收盘后的总市值
        self.max_market_value = money_init  # 记录最大的市值情况，用来计算回撤
        self.min_after_max_makret_value = money_init  # 记录最大市值后的最小市值
        self.max_retracement = 0  #记录最大回撤概率

    # 股票买入
    def buy_stock(self, buy_date, stock_name, stock_id, stock_price, buy_num):
        """
        :param buy_date: 买入日期
        :param stock_name: 买入股票的名字
        :param stock_id: 买入股票的id
        :param stcok_price: 买入股票的价格
        :param buy_num: 买入股票的数量
        :return:
        """
        if stock_id not in self.stock_id:
            self.stock_id.append(stock_id)
            self.stock_name.append(stock_name)
            self.buy_date.append(buy_date)
            self.stock_price.append(stock_price)
            self.hold_day.append(1)

            # 更新市值、现金及股票价值
            tmp_money = stock_price * buy_num
            service_change = tmp_money * self.buy_rate
            if service_change < self.buy_min:
                service_change = self.buy_min
            self.cash = self.cash - tmp_money - service_change
            if self.cash < 0:
                buy_num = buy_num - 100
                tmp_money = stock_price * buy_num
                service_change = tmp_money * self.buy_rate
                if service_change < self.buy_min:
                    service_change = self.buy_min
                self.cash = self.cash - tmp_money - service_change
            self.stock_num.append(buy_num)

            # self.stock_value = self.stock_value + tmp_money
            # self.market_value = self.cash + self.stock_value

            self.cost.append(tmp_money + service_change)

            info = str(buy_date) + '  买入 ' + stock_name + ' (' + stock_id + ') ' \
                   + str(int(buy_num)) + '股，股价：'+str(stock_price)+',花费：' + str(round(tmp_money, 2)) + ',手续费：' \
                   + str(round(service_change, 2)) + '，剩余现金：' + str(round(self.cash, 2))
            print(info)
            self.info.append(info)

    def sell_stock(self, sell_date, stock_name, stock_id, sell_price, sell_num, flag):
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
        service_change = tmp_money * self.buy_rate
        if service_change < self.sell_min:
            service_change = self.sell_min
        stamp_duty = self.stamp_duty * tmp_money
        self.cash = self.cash + tmp_money - service_change - stamp_duty

        # self.stock_value = self.stock_value - tmp_money
        # self.market_value = self.cash + self.stock_value

        service_change = stamp_duty + service_change
        # self.profit.append(tmp_money-service_change)
        profit = tmp_money-service_change - self.cost[idx]
        if self.stock_num[idx] == sell_num:
            # 全部卖出
            del self.stock_num[idx]
            del self.stock_id[idx]
            del self.stock_name[idx]
            del self.buy_date[idx]
            del self.stock_price[idx]
            del self.hold_day[idx]
            del self.cost[idx]
        else:
            self.stock_num[idx] = self.stock_num[idx] - sell_num
            # 还需要补充profit的计算先放着
            pass

        if flag == 0:
            info = str(sell_date) + '  到期卖出' + stock_name + ' (' + stock_id + ') ' \
                   + str(int(sell_num)) + '股，股价：'+str(sell_price) + ',收入：' + str(round(tmp_money,2)) + ',手续费：' \
                   + str(round(service_change, 2)) + '，剩余现金：' + str(round(self.cash, 2))
            if profit > 0:
                info = info + '，最终盈利：' + str(round(profit, 2))
                self.victory += 1
            else:
                info = info + '，最终亏损：' + str(round(profit, 2))
                self.defeat += 1
        elif flag == 1:
            info = str(sell_date) + '  止盈卖出' + stock_name + ' (' + stock_id + ') ' \
                   + str(int(sell_num)) + '股，股价：' + str(sell_price) + ',收入：' + str(round(tmp_money, 2)) + ',手续费：' \
                   + str(round(service_change, 2)) + '，剩余现金：' + str(round(self.cash, 2)) \
                   + '，最终盈利：' + str(round(profit, 2))
            self.victory += 1
        elif flag == 2:
            info = str(sell_date) + '  止损卖出' + stock_name + ' (' + stock_id + ') ' \
                   + str(int(sell_num)) + '股，股价：' + str(sell_price) + ',收入：' + str(round(tmp_money, 2)) + ',手续费：' \
                   + str(round(service_change, 2)) + '，剩余现金：' + str(round(self.cash, 2)) \
                   + '，最终亏损：' + str(round(profit, 2))
            self.defeat += 1

        print(info)
        self.info.append(info)

    # 买入触发时间，后期可以补
    def buy_trigger(self):
        pass

    # 判断是否达到卖出条件
    def sell_trigger(self, stock_id, day, all_df, index_df):
        """
        :param stock_id: 股票id
        :param day: 回测时间
        :param all_df: 所有数据的DataFrame
        :param index_df: 指数的DataFram
        :return: 第一个返回是否卖出，第二个返回卖出类型，第三个返回
                  卖出价格；若不卖出，后面两个值无意义
        """
        # print(day, stock_id)
        # 可能会有一些停牌企业，后期再改
        idx = (all_df['trade_date'] == day) & (all_df['ts_code'] == stock_id)
        # print(all_df[idx]['low'])
        low = all_df[idx]['low'].values[0]
        high = all_df[idx]['high'].values[0]
        open = all_df[idx]['open'].values[0]
        close = all_df[idx]['close'].values[0]

        idx = self.stock_id.index(stock_id)
        tmp_rate = (open - self.stock_price[idx]) / self.stock_price[idx]
        if tmp_rate <= self.stop_loss_rate:  # 止损卖出，开盘价卖出
            return True, 2, open
        elif tmp_rate >= self.stop_profit_rate:  # 止盈卖出，开盘价卖出
            return True, 1, open

        # 这里有点bug，先判断最低吧，优先出现最差的可能
        tmp_rate = (low - self.stock_price[idx]) / self.stock_price[idx]
        if tmp_rate <= self.stop_loss_rate:  # 止损卖出，止损价卖出
            # 假设都止损价不能马上卖出，多损失 0.01%
            sell_price = self.stock_price[idx] * (1 + self.stop_loss_rate - 0.01)
            return True, 2, sell_price

        tmp_rate = (high - self.stock_price[idx]) / self.stock_price[idx]
        if tmp_rate >= self.stop_profit_rate:  # 止盈卖出，止盈价卖出
            sell_price = self.stock_price[idx] * (1 + self.stop_profit_rate)
            return True, 1, sell_price

        # 判断持股周期是否达到上限
        hold_day = self.hold_day[idx]
        if hold_day >= self.max_hold_period:  # 收盘价卖出
            return True, 0, close

        return False, 3, 0

    # 更新信息
    def update(self, day, all_df):
        stock_price = []
        for j in range(len(self.stock_id)):
            self.hold_day[j] = self.hold_day[j] + 1  # 更新持股时间
            idx = (all_df['trade_date'] == day) & (all_df['ts_code'] == self.stock_id[j])
            close = all_df.loc[idx]['close'].values[0]
            stock_price.append(close)
        # 更新市值等信息
        # print(stock_price)
        stock_price = np.array(stock_price)
        stock_num = np.array(self.stock_num)
        self.stock_value = np.sum(stock_num * stock_price)
        self.market_value = self.cash + self.stock_value
        self.market_value_all.append(self.market_value)
        self.stock_value_all.append(self.stock_value)
        self.cash_all.append(self.cash)

        if self.max_market_value < self.market_value:
            self.max_market_value = self.market_value
        else:
            if self.min_after_max_makret_value > self.market_value:
                self.min_after_max_makret_value = self.market_value
                #  计算回撤率
                retracement = np.abs((self.max_market_value - self.min_after_max_makret_value) / self.max_market_value)
                if retracement > self.max_retracement:
                    self.max_retracement = retracement

    def BackTest(self, buy_df, all_df, index_df):
        """
        :param buy_df: 可以买入的股票，输入为DataFrame
        :param all_df: 所有股票的DataFrame
        :param index_df: 指数对应时间的df
        :return:
        """
        day_info = np.sort(index_df['trade_date'])
        for i in range(len(day_info)):
            day = day_info[i]
            tmp_idx = buy_df['trade_date'] == day
            tmp_df = buy_df.loc[tmp_idx].reset_index()

            # 先买后卖吧
            # ----买股
            if len(tmp_df) != 0:
                for j in range(len(tmp_df)):
                    money = self.market_value * 0.2
                    if money > self.cash:
                        money = self.cash
                    if money < 5000:  # 假设小于5000RMB，就不买股票
                        break
                    # print(1)
                    # print(tmp_df)
                    # print(tmp_df['close'])
                    buy_num = (money / tmp_df['close'][j]) // 100
                    if buy_num == 0:
                        continue
                    buy_num = buy_num * 100
                    self.buy_stock(day, tmp_df['name'][j],
                                   tmp_df['ts_code'][j], tmp_df['close'][j], buy_num)

            # ----卖股
            for j in range(len(self.stock_id) - 1, -1, -1):
                if self.buy_date[j] == day:
                    continue
                stock_id = self.stock_id[j]
                stock_name = self.stock_name[j]
                sell_num = self.stock_num[j]  # 假设全卖出去

                is_sell, sell_kind, sell_price = self.sell_trigger(stock_id, day, all_df, index_df)
                if is_sell:
                    self.sell_stock(day, stock_name, stock_id, sell_price, sell_num, sell_kind)

            # 更新持股周期及信息
            self.update(day, all_df)
