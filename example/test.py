import tushare as ts

ts.set_token("e9a352db1e3bc57734dd5232c058b9e36e4b655f0d0661ea3ecb1b8d")

df = ts.pro_bar(ts_code='018257.OF', freq='D', adj='hfq', start_date='20180101', end_date='20191011')
print(df)
pro = ts.pro_api()
df = pro.fund_adj(ts_code='018257.OF', start_date='20160101', end_date='20230826')
print(df)