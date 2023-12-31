# -*- coding: utf-8 -*-
# 使用交易系统代码进行回测的例子


import strategy.BaseStrategy as bs
import backtrader as bt
import jqdatapy


# 实际的策略类
class MyStrategy(bs.Strategy):
    params = (("maperiod", 15),
              ("bprint", False),)

    def __init__(self):
        super(MyStrategy, self).__init__()
        self.sma = dict()
        for i, d in enumerate(self.datas):
            self.sma[d] = bt.indicators.SimpleMovingAverage(d.close, period=self.params.maperiod)
        self.n = len(self.datas)
        self.order = None

    def downcast(self, amount, lot):
        return abs(amount // lot * lot)

    def next(self):
        if self.order:
            return

        for i, d in enumerate(self.datas):
            pos = self.getposition(d).size
            cash = self.broker.get_cash() / self.n
            amount = self.downcast(cash * 0.95 / d.close[0], 100)

            if not pos:
                if d.close[0] > self.sma[d][0]:
                    self.buy(data=d, size=amount)
                    # self.order = self.order_target_percent(d, 40, name=d._name)
            else:
                if d.close[0] < self.sma[d][0]:
                    self.order = self.order_target_percent(d, 0, name=d._name)

        """
        if not self.position:
            cash = self.broker.getcash()
            price = self.datas[0].close[0]
            if price <= 0.0:
                return
            stake = math.ceil(((0.95*cash/price)/self.n)/100)*100
            if self.datas[0].close[0] > self.sma[0][0]:
                self.order = self.buy(size = stake)
        else:
            if self.data_close[0][0] < self.sma[0][0]:
                self.order = self.close()
                """


# 买入持有的策略类，测试能否正常关闭交易
class HoldStrategy(bs.Strategy):
    params = (("maperiod", 15),
              ("bprint", False),)

    def __init__(self):
        super(HoldStrategy, self).__init__()
        self.n = len(self.datas)

    def downcast(self, amount, lot):
        return abs(amount // lot * lot)

    def next(self):
        for i, d in enumerate(self.datas):
            pos = self.getposition(d).size
            cash = self.broker.get_cash() / self.n
            amount = self.downcast(cash * 0.99 / d.close[0], 100)

            if not pos:
                self.buy(data=d, size=amount)
            else:
                if self.is_lastday(data=d):
                    self.close(data=d)

    def is_lastday(self, data):
        try:
            next_next_close = data.close[2]
        except IndexError:
            return True
        except:
            print("发生其它错误")
            return False


# 对单只股票进行回测

def back_test():
    bs.init_display()
    backtest = bs.BackTest(
        strategy=HoldStrategy,
        codes=["600027.SH"],
        bk_code="000300.SH",
        start_date="20160101",
        end_date="20230831",
        rf=0.03,
        start_cash=1000000,
        stamp_duty=0.005,
        commission=0.0001,
        adjust="hfq",
        period="daily",
        refresh=True,
        bprint=False,
        bdraw=True)
    results = backtest.run()
    print("回测结果", results)


# 对整个市场进行回测
def do_research():
    bs.init_display()
    research = bs.Research(MyStrategy,code = ["600036.SH","000858.SZ"],bk_code="600027.SH" ,start_date="20150101", end_date="20210101", min_len=100, retest=True,
                           refresh=False, maperiod=19)
    results = research.run()
    print(results.head(), results.describe())
    print(results.isnull().any())


# 进行调参
def do_opt():
    bs.init_display()
    map = range(2, 20)
    opt = bs.OptStrategy(
        codes=["600036.SH"],
        bk_code="000300.SZ",
        strategy=MyStrategy,
        start_date="20160101",
        end_date="20211231",
        start_cash=10000000,
        retest=False,
        refresh=False,
        bprint=False,
        bdraw=False,
        maperiod=range(10, 20))
    results = opt.run()
    results = opt.sort_results(results, key="年化收益率")
    print(results.loc[:, ["参数", "年化收益率"]])


if __name__ == "__main__":
    back_test()
    #do_research()
    #do_opt()
    pass
