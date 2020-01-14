# stock_market

注意：在运行选股策略时(ipyn文件)，可能会出现内存不够的情况，本人电脑是有40个G，所以没有考虑这些问题。如果电脑内存不够，可以考虑去掉一些行业，或者在数据读取的时候就提出一些不需要的时间（如提出2017年之前的数据），或者选择任意300支股等（总共有2800多支股票）。


Account.py:账户类用于回测使用

DataDowload.py:股票数据下载

CountLimit.py:统计每日涨停数与跌停数，并存入limit.csv中

RefreshData.py:股票数据更新

Draw.py: 绘图程序，绘制股票涨跌图等

短期选股策略1.ipyn: 训练模型及回测程序，具体可以看 （公众号第三篇文章）

https://mp.weixin.qq.com/s?__biz=MzIyNjg5MTAzOA==&tempkey=MTA0M18xZ0xXUDNXNEFvbGUvdW9pX0RNN1ZLV0tiZE1Zc2xOT3ZjaHA2RzdtWDBJak9RLW0xampvZGJtWUdQbTROUlp5VzE1aUdDOTdvMGJvSUNBRkNFTmh6enFIaHMyYXo5M2JVVUFKbUt2eVdQa0l1N2Itc3phZmNid3JWWWxKWkdWMEFQZHBxNTFPaFhoSW42U1lYZ2xhLXhpMFF6bkV2OTZxUGM5VmpBfn4%3D&chksm=6868c56d5f1f4c7b9ae3cc18ad9cc0efcd8dec5526c063f6c97d30200685155ab6d0ed9684b4#rd 


短期选股策略2.ipyn: 训练模型及回测程序，具体可以看 （公众号第五篇文章）

https://mp.weixin.qq.com/s?__biz=MzIyNjg5MTAzOA==&mid=2247483706&idx=1&sn=1b10768665edb191b55da8992267d8b2&chksm=e868c54bdf1f4c5d6121a398069db0bf2c0de77d1e1aee4d9c20aea208f51ce8d66714ef5a40&token=952490994&lang=zh_CN#rd


如果对个人在量化上的研究感兴趣可以关注个人公众号（公众号上有个人对代码的讲解）,不定期分享一些研究情况.后期策略成熟会分享一些股票.
公众号:Gambler_Evolution

个人知乎:https://www.zhihu.com/people/e-zhe-shi-wo/activities
