import numpy as nm
from pandas import DataFrame 
import tushare as ts


xx = DataFrame(index=['high','low','open'], columns=['a','b','c'])

#print(xx.info)



pro = ts.pro_api('e9a352db1e3bc57734dd5232c058b9e36e4b655f0d0661ea3ecb1b8d')

df = pro.index_daily(ts_code='399300.SZ')

#或者按日期取

df = pro.index_daily(ts_code='399300.SZ', start_date='20180101', end_date='20181010')
# ss = demo.createTable('test_demo','users',df)
# print(ss)

size= len(df.index)
# print(f"空值：{df.notnull()}")
# print(f"info:{df.info()}")
# print(df.count)
# print(f'df的类型是:',type(df))
# print(f"dtypes的值是:",df.)
# for i in range(0,size):
#     print(df.loc[i])
#xx = DataFrame(index=['high','low','open'], columns=['a','b','c'])
# df.info();
# print(df.info())
# print(f"type是：{type(ss)}")
# data = df.info();
# print(f"size = {size}")
for i in range(0,size):
    file = 'vol,amount'
    print(f"{df.loc[0][file]}")
    exit()
# for item in data:
#     print(type(item))

#print(df['ts_code'].dtypes)

