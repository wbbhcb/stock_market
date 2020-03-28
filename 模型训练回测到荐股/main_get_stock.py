# -*- coding: utf-8 -*-

import sys
import RefreshData 
import CountLimit
import Normal_feature
import get_stock
import os

# reload(sys)
# sys.setdefaultencoding('utf8')

if __name__ == '__main__':
    startdate = sys.argv[1]
    enddate = int(startdate)
    
    if not os.path.exists('stock/features_update'):
        os.mkdir('stock/features_update')
        print('mkdir')
    
    print('update data')
    RefreshData.main(startdate)
    
    print('extact feature1')
    CountLimit.extract_all()
    
    print('extact feature2')
    save_path1 = 'stock/features_update/feature0.csv'
    save_path2 = 'stock/features_update/stock_info.csv'
    startdate = 20191201
    Normal_feature.main(startdate, enddate, save_path1, save_path2) 
    
    print('get stock')
    startdate = int(sys.argv[1])
    enddate = int(sys.argv[1])
    get_stock.main(startdate, enddate)