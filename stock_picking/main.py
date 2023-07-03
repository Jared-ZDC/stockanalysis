"""
本地数据库建立
"""
# coding=utf-8
# 导入tushare
import tushare as ts
import time

debug = True

class cmp_opt:
    """
    定义标的的一些常用属性,比如pe_ttm/total_mv/pb/dv_ratio/turnover_rate/ema5/ema10/ema30/ema300 主要是每日指标
    """
    #标的代码
    ts_code : str = ""
    #总市值(单位亿)
    total_mv : float = 0.0
    #动态市盈率
    pe_ttm : float = 0.0
    #静态市盈率
    pe : float = 0.0
    #市净率
    pb : float = 0.0
    #换手率
    turnover_rate : float = 0.0
    #量比
    volume_ratio : float = 0.0
    #动态股息率
    dv_ttm : float = 0.0
    #静态股息率
    dv_ratio : float = 0.0
    #date
    date : str = ""
    #评分
    score : float = 0.0

    def __str__( self ):
        return f"ts_code = {self.ts_code}, total_mv={self.total_mv}, pe_ttm={self.pe_ttm}, pe={self.pe}, pb={self.pb}, turnover_rate={self.turnover_rate}, volume_ratio={self.volume_ratio}, dv_ttm={self.dv_ttm}, date={self.date}, score={self.score}"

def dprint(msg : str) :
    """
        仅作为debug打印到消息队列中使用
    """
    if debug:
        print(msg)
    else:
        pass


def none2zero(var : object) -> float:
    """
    None对象转换成0
    """
    try:
        if var == None:
            return 0.0
        else:
            return float(var)
    except:
        return 0.0

def init_context() -> None:
    ts.set_token('e9a352db1e3bc57734dd5232c058b9e36e4b655f0d0661ea3ecb1b8d')

def get_hz300_company(start_date_ : str = "",end_date_ : str = "",market_cap_min : float = 20000000.0, market_cap_max : float = 1000000000.0) -> dict :
    """
    @function: 月度接口,获取沪深300公司符合market_cap市值的公司,传入单位：亿；
    @market_cap_min : 最小市值
    @market_cap_max : 最大市值
    @date_ : 对应日期的沪深300成分股
    @return : dict , ts_code : DataFrame
    @DataFrame label: ts_code,total_mv,pe,pe_ttm,pb,dv_ratio,dv_ttm,turnover_rate,volume_ratio
    @link: https://tushare.pro/document/2?doc_id=32
    """
    pro = ts.pro_api()
    #月度接口, 获取日期内的成分股
    df = pro.index_weight(index_code='399300.SZ', start_date = start_date_, end_date = end_date_)
    con_code = df['con_code']
    
    index = 0
    index_len = len(con_code)
    df_daily_basic_dict : dict = {}
    print("checking daily_basic for hz300")
    t0 = time.time_ns()
    while index < index_len:
        #获取当前code公司估值
        df_daily_basic = pro.daily_basic(ts_code=con_code[index], trade_date=start_date_, fields=
                                         'ts_code,total_mv,pe,pe_ttm,pb,dv_ratio,dv_ttm,turnover_rate,volume_ratio')
        total_mv = 0.0
        if len(df_daily_basic['total_mv']) == 0:
            print(f"{con_code[index]} has no total_mv, total_mv = zero")
        else:
            total_mv = float(df_daily_basic['total_mv'].iloc[0])
        #判断当前估值是否在规定范围以内    
        if total_mv >= market_cap_min and total_mv <= market_cap_max:
            df_daily_basic_dict[con_code[index]] = df_daily_basic
        index += 1
    t1 = time.time_ns()
    print(f"checking daily_basic for hz300 finish, time cose {t1 - t0}ns")
    return df_daily_basic_dict
    #print(index_stock_info_df)
    
if __name__ == "__main__":
    #初始化token信息
    init_context()

    #cmp_opt对象
    ts_target : dict = {}

    # 获取沪深300 市值过2000亿的公司
    hz300 = get_hz300_company(start_date_= "20230601" ,end_date_="20230631")
    #查询一下市值1000亿的公司有哪些
    #if debug :
    print(f"more than 2000yi : {len(hz300)}")

    for ts_code,ts_value in hz300.items():
        #解析数据到对象中，对象存放在dict中，以ts_code作为索引
        ts = cmp_opt()
        ts.ts_code = ts_value['ts_code'].iloc[0]
        ts.total_mv = none2zero(ts_value['total_mv'].iloc[0]) / 10000.0
        ts.dv_ratio = none2zero(ts_value['dv_ratio'].iloc[0])
        ts.dv_ttm = none2zero(ts_value['dv_ttm'].iloc[0])
        ts.pb = none2zero(ts_value['pb'].iloc[0])
        ts.pe = none2zero(ts_value['pe'].iloc[0])
        ts.pe_ttm = none2zero(ts_value['pe_ttm'].iloc[0])
        ts.turnover_rate = none2zero(ts_value['turnover_rate'].iloc[0])
        ts.volume_ratio = none2zero(ts_value['volume_ratio'].iloc[0])
        ts_target[ts.ts_code] = ts
        print(ts)






