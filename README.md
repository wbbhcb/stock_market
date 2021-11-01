# stock_market

**注意1**：在运行选股策略时(ipyn文件)，可能会出现内存不够的情况，本人电脑是有40个G，所以没有考虑这些问题。如果电脑内存不够，可以考虑去掉一些行业，或者在数据读取的时候就剔除一些不需要的时间（如提出2017年之前的数据），或者选择任意300支股等（总共有2800多支股票）。

**注意2**：如若因权限原因无法获取tushare数据，可以关注公众号（公众号在末尾），在公众号后台回复“数据获取”，即可获取数据。

## 代码说明
**数据下载、更新及一些处理**

DataDowload.py:股票数据下载

RefreshData.py:股票数据更新

CountLimit.py:统计每日涨停数与跌停数，并存入limit.csv中

**账户类**

Account.py:账户类用于回测使用

**策略代码**

短期选股策略1.ipyb: 训练模型及回测程序，具体可以看 （公众号第三篇文章）

https://mp.weixin.qq.com/s/LLE3Oe8x13BdAqjCs4Geqw

短期选股策略2.ipyb: 训练模型及回测程序，具体可以看 （公众号第五篇文章）

https://mp.weixin.qq.com/s/drVANZjUhtltD9rsFNb0ZA

中线股选股策略1.ipyb:训练模型及回测程序，具体可以看 （公众号第六篇文章）

https://mp.weixin.qq.com/s/L0p2Z71vorV39qSucQIlFg

超级简单的仓位设置策略.ipynb：超级简单的仓位设置策略，具体可以看

https://mp.weixin.qq.com/s/WOpFs5Tkd7RP0sIZq1JEmg

仓位设置策略2.ipynb:

https://mp.weixin.qq.com/s/WoZG3iO52o-6VWv0RfDlMw

**其他代码**

Draw.py: 绘图程序，绘制股票涨跌图等
MakeLabel.py：制作训练集标签

# 运行顺序
短期选股策略1：
DataDowload.py->短期选股策略1.ipynb

短期选股策略2：
DataDowload.py->CountLimit.py->短期选股策略2.ipynb

中线股选股策略1：
DataDowload.py->CountLimit.py->MakeLabel.py->中线股选股策略1.ipynb

# 结语
如果觉得代码帮助很大，希望给个星，谢谢支持！！！

如果对个人在量化上的研究感兴趣可以关注个人公众号（公众号上有个人对代码的讲解）,不定期分享一些研究情况.

公众号:**Gambler_Evolution**

 ![image](https://github.com/wbbhcb/stock_market/blob/master/qrcode.jpg)

个人知乎:https://www.zhihu.com/people/e-zhe-shi-wo/activities

