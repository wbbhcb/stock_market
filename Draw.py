import matplotlib.pyplot as plt
import numpy as np
from mpl_finance import candlestick_ochl


def Draw_Market_Value_Change(day, market_value, index_value=None):
    """
    绘制账号市值变化
    :param day: list, 日期,(只需要起始日和终止日即可)
    :param market_value:  list, 总市值收盘信息
    :param index_value: list, 指数收盘信息
    :return:
    """

    x = list(range(len(market_value)))
    plt.figure(figsize=(12, 8))
    market_value = np.array(market_value) / market_value[0]
    plt.plot(x, market_value, label='My account')

    if index_value is not None:
        index_value = np.array(index_value) / index_value[0]
        plt.plot(x, index_value, label='The index')
    plt.xlabel("Date")
    plt.legend()
    plt.show()


def Draw_Stock(stock_id, stock_info, buy_day, sell_date=None, left_offset=5, right_offset=5):
    """
    绘制股票交易前后其股价变化
    :param stock_id: 股票id
    :param stock_info: 所有股票的信息
    :param buy_day: 买入股票的日子
    :param left_offset: 绘图左偏天数，用于调整可见天数
    :param right_offset: 绘图右偏天数，用于调整可见天数
    :return:
    """
    fig, ax = plt.subplots(1, 1, figsize=(8,3))
    idx = (stock_info['trade_date'] == buy_day) & (stock_info['ts_code'] == stock_id)
    ts_date_id = stock_info[idx]['ts_date_id'].values[0]
    idx = (stock_info['ts_date_id'] <= ts_date_id + right_offset) & (
                stock_info['ts_date_id'] >= ts_date_id - left_offset)
    tmp_df = stock_info[idx].sort_values('trade_date').reset_index()
    x = list(range(len(tmp_df)))
    tmp_df['index'] = x
    idx = (tmp_df['trade_date'] == buy_day)
    x_loc = tmp_df[idx]['index'].values[0]
    y_loc = tmp_df[idx]['close'].values[0]
    # print(x_loc, y_loc)
    data = tmp_df[['index', 'open', 'close', 'high', 'low']].values
    candlestick_ochl(ax, data, width=0.1, colorup='r', colordown='g')
    # plt.arrow(x_loc, y_loc*1.5, x_loc, y_loc, length_includes_head=True, head_width=0.25, head_length=0.5, fc='r', ec='b')
    plt.annotate("buy",
                xy=(x_loc, y_loc*1.001),
                xytext=(x_loc, y_loc * 1.06),
                # xycoords="figure points",
                arrowprops=dict(arrowstyle="->", color="b"))
    # plt.plot(x_loc, y_loc * 1.03, '*')
    title = tmp_df['name'][0]
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.title(title)
    plt.tick_params(labelsize=15)

    if sell_date:
        idx = (tmp_df['trade_date'] == sell_date)
        x_loc = tmp_df[idx]['index'].values[0]
        y_loc = tmp_df[idx]['high'].values[0]
        plt.annotate("sell",
                     xy=(x_loc, y_loc * 1.001),
                     xytext=(x_loc, y_loc * 1.06),
                     # xycoords="figure points",
                     arrowprops=dict(arrowstyle="->", color="r"))
