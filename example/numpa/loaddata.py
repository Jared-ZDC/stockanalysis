"""
从trueshare以及akshare获取数据，存放到csv文件中
"""

import pandas as pd
import akshare as ak
import tushare as ts
import time
import _thread

    
ts.set_token("e9a352db1e3bc57734dd5232c058b9e36e4b655f0d0661ea3ecb1b8d")    
pro = ts.pro_api()

#获取当前的股票信息
data : pd.DataFrame = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
#data.to_csv("/mnt/e/tushare/stock_basic.csv",index=False,encoding='utf_8_sig')
data.to_csv("/workspaces/stockanalysis/stock_basic.csv",index=False,encoding='utf_8_sig')
def download(ts_code) :
    #print(f"{type(ts_code)}")
    index : int = 0
    for code in ts_code:
        index += 1
        #不复权
        diary: pd.DataFrame = ts.pro_bar(ts_code=code, adj=None, start_date='20150101', end_date='20230820')
        if diary.empty == True :
            continue
        diary = diary.set_index(['trade_date'])
        diary.index = pd.to_datetime(diary.index,format="%Y%m%d",utc=False)
        diary.loc[:, 'openinterest'] = 0
        diary = diary.sort_index()
        diary.to_csv(f"/workspaces/stockanalysis/{code}diaryNone.csv",index=True,encoding='utf_8_sig')
        print(f"{index} save {code} to /mnt/e/tushare/{code}diaryNone.csv")   
        
        #前复权
        diary: pd.DataFrame = ts.pro_bar(ts_code=code, adj="qfq", start_date='20150101', end_date='20230820')
        diary = diary.set_index(['trade_date'])
        diary.index = pd.to_datetime(diary.index,format="%Y%m%d",utc=False)
        diary.loc[:, 'openinterest'] = 0
        diary = diary.sort_index()
        diary.to_csv(f"/workspaces/stockanalysis/{code}diaryqfq.csv",index=True,encoding='utf_8_sig')
        print(f"{index} save {code} to /mnt/e/tushare/{code}diaryqfq.csv")   

        #后复权
        diary: pd.DataFrame = ts.pro_bar(ts_code=code, adj="hfq", start_date='20150101', end_date='20230820')
        diary = diary.set_index(['trade_date'])
        diary.index = pd.to_datetime(diary.index,format="%Y%m%d",utc=False)
        diary.loc[:, 'openinterest'] = 0
        diary = diary.sort_index()
        diary.to_csv(f"/workspaces/stockanalysis/{code}diaryhfq.csv",index=True,encoding='utf_8_sig')
        print(f"{index} save {code} to /mnt/e/tushare/{code}diaryhfq.csv")   

#循环当前的股票信息
ts_code = data['ts_code']
#try:
#_thread.start_new_thread( download, (ts_code[:1000],))
#_thread.start_new_thread( download, (ts_code[1000:2000],))
#_thread.start_new_thread( download, (ts_code[2000:3000],))
#_thread.start_new_thread( download, (ts_code[3000:4000],))
#_thread.start_new_thread( download, (ts_code[4000:5000],))
#_thread.start_new_thread( download, (ts_code[5000:5262],))
target_code = ("600036.SH","000858.SZ","600027.SH")
download(target_code)
#except Exception:
#   print ("Error: 无法启动线程")

while 1:
    pass
