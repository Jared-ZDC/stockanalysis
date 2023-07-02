"""
本地数据库建立
"""
# coding=utf-8
# 导入tushare
import tushare as ts
import pandas as pd
import time

debug = True

def debug_print(msg : str) :
    """
    仅作为debug打印使用
    """
    if debug:
        print(msg)
    else:
        pass
    


def init_context() -> None:
    ts.set_token('e9a352db1e3bc57734dd5232c058b9e36e4b655f0d0661ea3ecb1b8d')

def get_hz300_company(start_date_ : str = "",end_date_ : str = "",market_cap_min : float = 10000000.0, market_cap_max : float = 1000000000.0) -> dict :
    """
    @function: 获取沪深300公司符合market_cap市值的公司,传入单位：亿；
    @market_cap_min : 最小市值
    @market_cap_max : 最大市值
    @date_ : 对应日期的沪深300成分股
    @return : dict , ts_code : DataFrame
    @DataFrame label: ts_code,total_mv,pe,pe_ttm,pb,dv_ratio,dv_ttm,turnover_rate,volume_ratio
    @link: https://tushare.pro/document/2?doc_id=32
    """
    pro = ts.pro_api()
    df = pro.index_weight(index_code='399300.SZ', start_date = start_date_, end_date = end_date_)
    index_code = df['index_code']
    con_code = df['con_code']
    
    debug_print(f"df len = {len(df)}")
    
    index = 0
    index_len = len(con_code)
    df_daily_basic_dict : dict = {}
    debug_print(f"index = {index}, index_len = {index_len}")
    while index < index_len:
        debug_print(f"{index_code[index],con_code[index]}")
        index += 1
        #获取当前code公司估值
        df_daily_basic = pro.daily_basic(ts_code=con_code[index], trade_date=start_date_, fields=
                                         'ts_code,total_mv,pe,pe_ttm,pb,dv_ratio,dv_ttm,turnover_rate,volume_ratio')
        time.sleep(0.1)
        debug_print(f"{con_code[index],df_daily_basic['total_mv']}")
        if float(df_daily_basic['total_mv']) >= market_cap_min and float(df_daily_basic['total_mv']) <= market_cap_max:
            df_daily_basic_dict[con_code[index]] = df_daily_basic
    
    return df_daily_basic_dict
    #print(index_stock_info_df)
    

if __name__ == "__main__":
    #初始化token信息
    init_context()
    
    # 获取沪深300 市值过1000亿的公司
    hz300 = get_hz300_company(start_date_= "20230601" ,end_date_="20230702")
    #查询一下市值1000亿的公司有哪些
    if debug :
        index = 0
        len = len(hz300)
        for ts_code,ts_value in hz300.items():
            print(f"{ts_code,ts_value['total_mv'],ts_value['pe_ttm'],ts_value['dv_ttm'],ts_value['volume_ratio']}")