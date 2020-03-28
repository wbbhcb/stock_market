# stock_market

利用机器学习开发选股策略文章见：
https://mp.weixin.qq.com/s/_izKXsyUcfmhl5rpnqTEgw

此代码与链接中的稍有不同之处。

不同点：

1、买入点为第二天开盘价

2、特征构造稍有不同

**说明**：

此代码在linux系统下已经过调试，可以完整运行。

此代码可能会有一些bug存在，大家自行调试（不改任何东西应该是可以运行的），windows或mac运行可能会报一些错，比如编码格式的问题，大家碰到自行百度解决。
# 代码运行说明
**1. 数据下载**

运行前需手动修改起始日期，终止日期。可能会碰到中途程序因网络问题程序终止，已经下载好的数据可以不用重新下载，注释相关代码即可。终端输入以下语句即可运行，不会终端运行的可以利用一些ide（比如pycharm）直接运行即可。

**数据下载阶段需要用到tushare的接口token，大家自己去tushare上注册账号获取token，部分数据下载需要权限积分，学生或老师可以免费申请较高权限。**
~~~~
python DataDowload.py
~~~~
**2. 特征提取及标签制作**

如果在模型训练的阶段，提取特征和标签制作运行以下三条语句。非模型训练阶段的特征提取见后面。
后面日期可以更改(表示终止日期)。
~~~~
python Normal_feature.py all 20200325
python CountLimit.csv
python MakeLabel.py
~~~~
**3. 训练模型回测及模型保存**

运行“模型训练及回测.ipynb”即可（用jupyter notebook打开）。运行完会自动保存训练得到的模型。

**4. 每天收盘后推送股票**

在模型训练完之后，终端输入以下命令会输出stock.csv，为第二天的推荐操作股票。后面的日期可以更改。需要注意一点，这个程序会自动更新数据，但是只会更新一天的数据（比如按下面输入只会更新20200326的数据）。
~~~~
python main_get_stock.py 20200326
~~~~

## 代码说明
**数据下载、更新及一些处理**

DataDowload.py:股票数据下载

RefreshData.py:股票数据更新

CountLimit.py:统计每日涨停数与跌停数，并存入limit.csv中

Normal_feature.py:提取常规特征

**账户类**

Account.py:账户类用于回测使用

**其他代码**

Draw.py: 绘图程序，绘制股票涨跌图等

MakeLabel.py：制作训练集标签

**股票推送**

main_get_stock.py: 推送第二天操作

# 结语
如果觉得代码帮助很大，希望给个星，谢谢支持！！！

此代码仍有很多改进空间，大家可以自行改进。

如果对个人在量化上的研究感兴趣可以关注个人公众号（公众号上有个人对代码的讲解）,不定期分享一些研究情况.后期策略成熟会分享一些股票.

公众号:**Gambler_Evolution**

 ![image](https://github.com/wbbhcb/stock_market/blob/master/qrcode.jpg)

个人知乎: https://www.zhihu.com/people/e-zhe-shi-wo/activities

# 未来研究
1、实时行情获取（新浪有借口可以获取）

2、自动交易（通过模拟web访问券商官网进行自动交易）

3、中高频策略实现（我坚信机器学习算法能够在中高频策略有一个好的收益）
