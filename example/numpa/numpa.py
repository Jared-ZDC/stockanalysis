import numpy as nm
from pandas import DataFrame 
import tushare as ts



xx = DataFrame(index=['high','low','open'], columns=['a','b','c'])

#print(xx.info)



pro = ts.pro_api('e9a352db1e3bc57734dd5232c058b9e36e4b655f0d0661ea3ecb1b8d')

df = pro.index_daily(ts_code='399300.SZ')

#或者按日期取

df = pro.index_daily(ts_code='399300.SZ', start_date='20180101', end_date='20181010')


print(df.info())

size= len(df.index)

print(f"size = {size}")

for i in range(0,size)
    print(f"{df.loc[i]}")
