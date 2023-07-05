#!/bin/python
"""
本地数据库建立
"""
# coding=utf-8
# 导入tushare
import tushare as ts
import os
import shutil
from tushare.pro import client as cl
import pandas as pd

class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}
    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]
    
@Singleton
class localtushare(object):
    """
    单例模式，生成localtushare对象
    """
    #cache path
    g_cache_path : str = ""
    #token
    token : str = ""

    #tushare DataApi
    tushareApi : cl.DataApi 

    def __init__(self):
        pass

    def set_token(self, token : str) -> None: 
        self.token  = token
        ts.set_token(token)
        self.tushareApi = ts.pro_api()

    def initcache(self,cache_path: str = "") -> bool:
        """
        @function :  初始化数据cache数据池
        """
        if cache_path == "":
            cache_path = ".cache"
        try:
            # 去除首位空格
            cache_path=cache_path.strip()
            # 去除尾部 \ 符号
            cache_path=cache_path.rstrip("\\")
            # 判断路径是否存在
            isExists=os.path.exists(cache_path)
            # 判断结果
            if not isExists:
                # 如果不存在则创建目录,创建目录操作函数
                #os.mkdir(path)与os.makedirs(path)的区别是,当父目录不存在的时候os.mkdir(path)不会创建，os.makedirs(path)则会创建父目录
                #此处路径最好使用utf-8解码，否则在磁盘中可能会出现乱码的情况
                os.makedirs(cache_path.decode('utf-8')) 
                print(cache_path+' 创建成功')
        
            self.g_cache_path = cache_path
            return True
        except:
            return False
        

    def cleancache(self) -> bool:
        """
        
        """
        # 去除首位空格
        self.g_cache_path=self.g_cache_path.strip()
        # 去除尾部 \ 符号
        self.g_cache_path=self.g_cache_path.rstrip("\\")
        # 判断路径是否存在
        isExists=os.path.exists(self.g_cache_path)
        # 判断结果
        if not isExists:
            return True
        
        try:
            shutil.rmtree(self.g_cache_path) 
            return True
        except:
            return False


    def daily_basic(self, ts_code_ : str, trade_date_: str = "", fields_ : str = "", rewrite : bool = False) -> pd.DataFrame :
        """
        @function : cache daily_basic
        @rewrite : 判断是否需要重写cache文件
        """
        filepath = self.g_cache_path + f"/{ts_code_}_{trade_date_}_{fields_}.csv"
        if (not os.access(filepath, os.F_OK)) or (rewrite):
            df = self.tushareApi.daily_basic(ts_code=ts_code_, trade_date=trade_date_, fields=fields_)
            df.to_csv()

    