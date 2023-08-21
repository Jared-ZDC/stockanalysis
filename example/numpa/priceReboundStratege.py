"""
股价反弹策略
价格连续下跌，反弹则买入，连续上涨，下跌则卖

选择三只股票，招商银行，五粮液，华电国际作为标的

总资金分成3份,并且卖出 买入的时候,动态平衡,基本保持各1/3

"""
import backtrader as bt
import pandas as pd
import numpy as np
import datetime
from copy import deepcopy
import time

#目标： 招商银行，五粮液，华电国际
#target_code = ("600036.SH","000858.SZ","600027.SH")
target_code = ("600225.SH",)
daily_price_hfq : list[pd.DataFrame] = []
daily_price_none : list[pd.DataFrame] = []

#构建交易策略 价格反转策略
class priceRebound(bt.Strategy):
    '''选股策略'''
    def __init__(self):
        self.buy_stock = target_code # 保留调仓列表
        self.order_list = [] # 记录以往订单，方便调仓日对未完成订单做处理
        self.buy_stocks_pre = [] # 记录上一期持仓
        pass
    def next(self):
        dt = self.datas[0].datetime.date(0) # 获取当前的回测时间点
        print(f"date = {dt}")
        
        #判断当前的股价是否处于反弹状态
        time.sleep(1)
        pass
    def notify_order(self, order):
        # 未被处理的订单
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 已经处理的订单
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log(
                        'BUY EXECUTED, ref:%.0f,Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2f, Stock: %s' %
                        (order.ref, # 订单编号
                        order.executed.price, # 成交价
                        order.executed.value, # 成交额
                        order.executed.comm, # 佣金
                        order.executed.size, # 成交量
                        order.data._name)) # 股票名称
            else: # Sell
                self.log('SELL EXECUTED, ref:%.0f, Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2f, Stock: %s' %
                            (order.ref,
                            order.executed.price,
                            order.executed.value,
                            order.executed.comm,
                            order.executed.size,
                            order.data._name))
    pass

if __name__ == "__main__":
    # 实例化 cerebro
    cerebro = bt.Cerebro()
    # 打印初始资金
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    #准备数据
    for ts_code in target_code:
        #后复权数据技术指标
        pd_temp : pd.DataFrame = pd.read_csv(f"/mnt/e/tushare/{ts_code}diaryhfq.csv", parse_dates=['trade_date'],
                                           encoding='utf_8_sig', infer_datetime_format=True)
        #重命名: 表内字段就是 Backtrader 默认情况下要求输入的 7 个字段： 
        # 'datetime' 、'open'、'high'、'low'、'close'、'volume'、'openinterest'，外加一个 'sec_code' 股票代码字段。
        pd_temp = pd_temp.rename(columns={'trade_date':'datetime','ts_code':'sec_code','vol':'volume'})
        
        pd_temp.loc[:, 'openinterest'] = 0
        pd_temp["datetime"] = pd.to_datetime(pd_temp["datetime"])
        pd_temp = pd_temp.set_index(['datetime'])
        
        pd_temp.index = pd.to_datetime(pd_temp.index,format="%Y-%m-%d",utc=False)
        #datafeed = bt.feeds.PandasData(dataname=pd_temp)
        
        # 缺失值处理：有些交易日的数据为空，所以需要对缺失数据进行填充
        pd_temp.loc[:,['volume','openinterest']] = pd_temp.loc[:,['volume','openinterest']].fillna(0)
        pd_temp.loc[:,['open','high','low','close']] = pd_temp.loc[:,['open','high','low','close']].fillna(method='pad')
        pd_temp.loc[:,['open','high','low','close']] = pd_temp.loc[:,['open','high','low','close']].fillna(0)
        daily_price_hfq.append(pd_temp)
        
         # 导入未复权的数据
        data = bt.feeds.GenericCSVData(
            dataname=f"/mnt/e/tushare/{ts_code}diaryNone.csv",
            fromdate=datetime.datetime(2015, 1, 1),
            todate=datetime.datetime(2023, 8, 20),
            nullvalue=0.0,
            dtformat=('%Y-%m-%d'),
            datetime=0,
            high=3,
            low=4,
            open=2,
            close=5,
            volume=9,
            openinterest=-1
        )
        cerebro.adddata(data, name=ts_code) # 通过 name 实现数据集与股票的一一对应
        """
        #未复权的数据作为回测基线
        pd_temp : pd.DataFrame  = pd.read_csv(f"/mnt/e/tushare/{ts_code}diaryNone.csv", parse_dates=['trade_date'],
                                           encoding='utf_8_sig', infer_datetime_format=True)
        pd_temp = pd_temp.rename(columns={'trade_date':'datetime','ts_code':'sec_code','vol':'volume'})
        pd_temp.loc[:, 'openinterest'] = 0
        pd_temp["datetime"] = pd.to_datetime(pd_temp["datetime"])
        pd_temp = pd_temp.set_index(['datetime'])
        
        pd_temp.index = pd.to_datetime(pd_temp.index,format="%Y-%m-%d",utc=True)
        #datafeed = bt.feeds.PandasData(dataname=pd_temp)
        
        # 缺失值处理：有些交易日的数据为空，所以需要对缺失数据进行填充
        pd_temp.loc[:,['volume','openinterest']] = pd_temp.loc[:,['volume','openinterest']].fillna(0)
        pd_temp.loc[:,['open','high','low','close']] = pd_temp.loc[:,['open','high','low','close']].fillna(method='pad')
        pd_temp.loc[:,['open','high','low','close']] = pd_temp.loc[:,['open','high','low','close']].fillna(0)
        daily_price_none.append(pd_temp)
        """
       
    
    # 初始资金 100,000
    cerebro.broker.setcash(100000.0)
    # 佣金，双边各 0.0002
    cerebro.broker.setcommission(commission=0.0002)
    # 滑点：双边各 0.0001
    cerebro.broker.set_slippage_perc(perc=0.0001)
    
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='pnl') # 返回收益率时序数据
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='_AnnualReturn') # 年化收益率
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='_SharpeRatio') # 夏普比率
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='_DrawDown') # 回撤
    
    # 将编写的策略添加给大脑
    cerebro.addstrategy(priceRebound)
    
    # 启动回测
    cerebro.run()
    # 打印回测完成后的资金
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    #初始化数据
    pass
