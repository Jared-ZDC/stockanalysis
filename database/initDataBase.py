'''
创建数据库
'''



def createDatabase(baseName : str) -> bool:
    '''
    @function: 创建数据库
    @baseName : 数据库名字
    '''
    return True

def createTable(baseName : str, tableName : str,  table_consistant : dict) -> bool :
    '''
    @func: 创建表单
    @baseName : 数据库
    @tableName : 表名
    @table_consistant : 表的结构 {"ts_code",str}
    '''
    return True


if __name__ == '__main__' :
    print(f"create database")
