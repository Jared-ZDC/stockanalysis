'''
创建数据库
'''
import pymysql
import configparser
from pandas import DataFrame
import tushare as ts
class initDataBase:
    def __init__(self):
        '''
        @func 初始化方法
        '''
        try:
            config = configparser.ConfigParser()
            config.read('../config/config.properties',encoding="utf-8")
            host = config.get('mysql','ip')
            user = config.get('mysql','user')
            password = config.get('mysql','password')
            self.mydb = pymysql.connect(
                host=host,
                user=user,
                password=password,
                charset='utf8',
                unix_socket="/tmp/mysql.sock"
                # autocommit= True
            )
            self.my_cursor = self.mydb.cursor()
        except(Exception) as msg:
            print('数据库链接失败,详细原因：',msg)

    def __del__(self):
        try:
            self.my_cursor.close()  # 先关闭游标
            self.mydb.close()  # 再关闭数据库连接
        except:
            pass
    '''创建数据库方法'''
    def createDatabase(self,baseName: str) -> bool:
        ''' 初始化数据库参数'''
        '''
        @function: 创建数据库
        @baseName : 数据库名字
        '''
        if not baseName:
            print("数据库名称不能为空")
            return False
        try:
            sql = f"CREATE DATABASE  `{baseName}` DEFAULT CHARSET utf8 COLLATE utf8_general_ci;"
            self.my_cursor.execute(sql)
            return True
        except:
            return False

    '''创建数据表方法'''
    def createTable(self,baseName: str, tableName: str, table_consistant:DataFrame) -> bool:
        '''
        @func: 创建表单
        @baseName : 数据库名称
        @tableName : 表名
        @table_consistant : 数据及结构
        '''

        if not baseName or not tableName or  table_consistant.empty:
            print("参数不能为空错误，请检查上传参数")
            return False
        try:
            #打开指定数据库
            self.my_cursor.execute(f"USE {baseName}")
            #解析表格数据，生成数据表格
            table_sql = self.analyzeData(table_consistant,tableName)
            self.my_cursor.execute(table_sql)
            #插入表格数据
            self.install(table_consistant,tableName)
            return True
        except(Exception) as msg:
            print(msg)
            return False

    def delDataBase(self,baseName:str)->bool:
        '''
        @func:删除数据库方法
        :param baseName: 数据库名称
        :return: bool
        '''

        if not baseName:
            print('数据库名称不能为空')
        try:
            sql = f"drop database {baseName};"
            self.my_cursor.execute(sql)
            return True
        except(Exception) as msg:
            return False

    def delTable(self,baseName:str,table_name:str)->bool:
        '''
        @func 删除数据表方法
        :param table_name: 表名称
        :return: bool
        '''

        try:
            if not baseName or not table_name:
                print('参数不能为空')
                return False

            sql = f'drop table {baseName}.{table_name};';
            self.my_cursor.execute(sql)
            return True
        except(Exception) as msg:
            print(msg)
            return False


    def analyzeData(self, table_consistant:DataFrame, table_name:str)->str:
        '''
        @func:数据处理方法
        :param table_consistant: 数据及结构
        :param table_name:  表名
        :return: str
        '''

        typeList = table_consistant.dtypes #获取字段类型
        fileList = table_consistant.columns.values.tolist() #获取所有字段
        str = ''
        str += f'Create Table  `{table_name}`(\n'
        str += '\t `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,\n'
        for k,v in enumerate(fileList):
            #indx = fileList[1] if k == 0 else indx
            #代码优化，看了表不是所有表都有交易日期字段
            if v == 'trade_date':
                index = v
            else:
                index = 'id'
            type = self.mapDataType(typeList[k])
            str += f'\t`{v}` {type} ,\n'

        if index:
            str += f'\tPRIMARY KEY ( `{index}` ) \n'

        str += ')ENGINE=InnoDB CHARACTER SET utf8;'
        return  str

    def mapDataType(self,type:str)->str:
        '''
        @func 数据类型映射方法
        :param type: 字段类型
        :return: str
        '''
        if type == 'object':
            type = 'varchar(150)'
        elif type=='float64':
            type = 'numeric(14,5)'
        elif type == 'int64':
            type = 'int(30)'
        elif type == 'datetime64':
            type = 'char(8)'

        return  type

    def install(self, table_consistant, table_name):
        '''
        @func 批量插入表格数据
        :param table_consistant: 数据结构
        :param table_name: 表名称
        :return: bool
        '''
        # 先获取数据大小
        size = len(table_consistant.index)
        # 默认取第一行列的总长度
        lengt = len(table_consistant.loc[0])
        # 获取所有表格数据并转成字典类型
        dataInfo = table_consistant.to_dict('list')
        #拼接插入字段名
        filed = '`'+'`,`'.join(list(dataInfo.keys()))+'`'
        #声明占位符
        Placeholder = ''
        #标识，用来判断是否满足了大于字段长度的判断
        sign = False
        #申明存储数据值
        data = []
        #定义读取字段对应内容索引
        lindex = 0
        for i in range(0, size):
            #定义一个数组列表存入循环获取到的行数据
            newInfo = []
            while (lindex < lengt):
                #因为读取一行数据是纵向的，所以需要一行行循环获取
                newInfo.append(table_consistant.loc[i][lindex])
                #判断标识是否为True 如果是代表已经申明好了占位符了
                if not sign:
                    Placeholder += '%s,'

                lindex += 1
            #while循环结束初始化变量
            lindex = 0
            #标识已经申明好了占位符
            sign = True
            #将获取到的行数据存转成元组类型并存入列表当中
            data.append(tuple(newInfo))

        # 去除最后一个逗号
        Placeholder = Placeholder[:-1]
        sql = f"insert into {table_name}({filed}) VALUES({Placeholder})"
        self.my_cursor.executemany(sql,data)
        self.mydb.commit()
        return True


'''可以打开测试使用'''
# pro = ts.pro_api('e9a352db1e3bc57734dd5232c058b9e36e4b655f0d0661ea3ecb1b8d')
# df = pro.index_daily(ts_code='399300.SZ', start_date='20180101', end_date='20181010')
s = initDataBase()
# print(s.delDataBase('test_demo'))
# print(s.delTable('test_demo','users'))
# vool = s.createDatabase('test_demo')
# data1 = s.createTable(baseName='test_demo',tableName='users',table_consistant=df)
# print(data1)
if __name__ == '__main__' :
    initDataBase()
