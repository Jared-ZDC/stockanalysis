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
target_code = ("600036.SH","000858.SZ","600027.SH")
#target_code = ("600225.SH",)
#考虑的天数, 如果前precont_days的时间都是下降的， 第五天是反弹
precont_days = 5

#考虑precont_days中，允许多少次反弹
rebound_times = 1

#最高价回弹多少，清仓， 默认5%
biggest_rebound = 0.05



#构建交易策略 价格反转策略
class priceRebound(bt.Strategy):
    '''选股策略'''
    def __init__(self):
        self.buy_stock = target_code # 保留调仓列表
        self.order_list = [] # 记录以往订单，方便调仓日对未完成订单做处理
        self.buy_stocks_pre = [] # 记录上一期持仓
        self.count = 0 # 记录next循环次数
        self.precont_days : list[int] = []
        self.rebound_times : list[int] = []
        self.biggest_value : list[float] = []  #当前趋势中的最高价
        self.lowest_value : list[float] = []  #当前趋势中的最低价
        self.buy_point : list[float] = []  #买点
        
        print("-------------self.datas-------------")
        print(f"len = {len(self.datas)}")
        print("-------------self.datas[0]-------------")
        print(self.datas[0]._name, self.datas[0]) # 返回第一个导入的数据表格，常规形式
        print("-------------self.datas[1]-------------")
        print(self.datas[1]._name, self.datas[1]) # 返回第二个导入的数据表格，常规形式
        print("-------------self.datas[2]-------------")
        print(self.datas[2]._name, self.datas[2]) # 返回第三个导入的数据表格，常规形式

        print("--------- 打印 self 策略本身的 lines ----------")
        print(self.lines.getlinealiases())
        print("--------- 打印 self.datas 第一个数据表格的 lines ----------")
        print(self.datas[0].lines.getlinealiases())
        pass
    def next(self):
        dt = self.datas[0].datetime.date(0) # 获取当前的回测时间点
        print(f"date = {dt}")

        print(f"------------- next 的第{self.count+1}次循环 --------------")
        print("当前时点（今日）：",'datetime',self.data1.lines.datetime.date(0),'close', self.data1.lines.close[0])
        print("往前推1天（昨日）：",'datetime',self.data1.lines.datetime.date(-1),'close', self.data1.lines.close[-1])
        print("往前推2天（前日）", 'datetime',self.data1.lines.datetime.date(-2),'close', self.data1.lines.close[-2])
        print("前日、昨日、今日的收盘价：", self.data1.lines.close.get(ago=0, size=3))
        print("往后推1天（明日）：",'datetime',self.data1.lines.datetime.date(1),'close', self.data1.lines.close[1])
        print("往后推2天（明后日）", 'datetime',self.data1.lines.datetime.date(2),'close', self.data1.lines.close[2])
        # 在 next() 中调用 len(self.data0)，返回的是当前已处理（已回测）的数据长度，会随着回测的推进动态增长
        print("已处理的数据点：", len(self.data1))
        # buflen() 返回整条线的总长度，固定不变；
        print("line的总长度：", self.data0.buflen())
        

        #判断当前的股价是否处于反弹状态
        #循环取出目标股票，判断目标股票的价格,间隔2是由于存放数据的方式是交替进行的， index=0 未复权数据， index=1 后复权数据
        for index in range(0,len(self.datas),2):
            none_index = index
            hfq_index = index + 1
            today_close:float = self.datas[hfq_index].lines.close[0]
            if self.count == 0 :
                #第一次进入循环， 只要记录lowest_value，biggest_value
                self.lowest_value[hfq_index] = today_close
                self.biggest_value[hfq_index] = today_close
                self.precont_days[hfq_index] = 0
                self.rebound_times[hfq_index] = 0
                self.buy_point[hfq_index] = 0
                continue
            
            #第二次进入循环， 开始进行算法迭代, 需要取后复权数据，所以要index + 1
            yesterday_close:float = self.datas[hfq_index].lines.close[-1]
            
            #最低点、最高点用来做卖出条件
            if today_close < self.lowest_value[hfq_index] :
                #如果今天收盘价比当前最低点要低，则更新最低点
                self.lowest_value[hfq_index] = today_close
                
            if today_close > self.biggest_value[hfq_index] :
                #如果今天收盘价比当前最高点要高，则更新最高点
                self.biggest_value[hfq_index] = today_close
            
            if today_close <= yesterday_close :
                #如果今天收盘价比昨天收盘价要低，则precont_days计数+1
                self.precont_days[hfq_index] += 1
            else:
                if self.precont_days[hfq_index] >= precont_days:
                    #如果之前precont_days天都是下降得，今天开始反弹，则买入
                    
                    continue
                if self.rebound_times[hfq_index] <= rebound_times:
                    #如果今天收盘价比昨天收盘价要高，且次数小于等于rebound_times
                    self.rebound_times[hfq_index] += 1
                    self.precont_days[hfq_index] += 1
                else:
                    #如果次数大于了rebound_times
                    self.precont_days[hfq_index] = 0
                    self.rebound_times[hfq_index] = 0
            
            
            
        time.sleep(1)
        self.count += 1
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
        # 导入未复权的数据
        data = bt.feeds.GenericCSVData(
            dataname=f"/workspaces/stockanalysis/{ts_code}diaryNone.csv",
            fromdate=datetime.datetime(2014, 1, 1),
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
        cerebro.adddata(data, name=f"{ts_code}_none") # 通过 name 实现数据集与股票的一一对应
        
        # 导入后复权的数据
        data = bt.feeds.GenericCSVData(
            dataname=f"/workspaces/stockanalysis/{ts_code}diaryhfq.csv",
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
        cerebro.adddata(data, name=f"{ts_code}_hfq")
        
       
    
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
