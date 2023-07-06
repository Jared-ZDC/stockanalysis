#!/bin/python
"""
测试主流程
"""
# coding=utf-8
# 导入tushare

from strategy.value_selection_strategy import * 
from strategy.ts_select import *


if __name__ == "__main__":
    
    #选股策略
    ts = value_selection_strategy()
    ts.strategy_main()

