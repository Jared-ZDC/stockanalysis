"""
选股策略的interface
"""
# coding=utf-8
# 导入tushare


class ts_select:
    date : str = ""

    def strategy_main(self) -> object:
        """
        返回目标标的对象
        """
        pass