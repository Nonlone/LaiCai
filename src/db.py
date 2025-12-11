import pymysql
import os
import re
from datetime import date, datetime
from typing import Optional


# 自定义日期适配器
def adapt_date(val):
    return val.isoformat()


# 自定义时间戳适配器
def adapt_datetime(val):
    return val.isoformat(" ")


# 自定义日期转换器
def convert_date(val):
    return date.fromisoformat(val.decode())


# 自定义时间戳转换器
def convert_timestamp(val):
    return datetime.fromisoformat(val.decode())


def check_table_exists(conn: pymysql.connections.Connection, table_name: str) -> bool:
    """
    检查表是否存在
    
    Args:
        conn (pymysql.connections.Connection): 数据库连接对象
        table_name (str): 表名
        
    Returns:
        bool: 表存在返回 True，否则返回 False
    """
    cursor = conn.cursor()
    # MariaDB 查询表是否存在的方式
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = DATABASE() AND table_name = %s
    """, (table_name,))
    
    exists = cursor.fetchone()[0] > 0
    cursor.close()
    return exists


def create_tables(conn: pymysql.connections.Connection, sql_file_path: str, table_name: str) -> bool:
    """
    从SQL文件创建表
    
    Args:
        conn (pymysql.connections.Connection): 数据库连接对象
        sql_file_path (str): SQL文件路径
        table_name (str): 实际要创建的表名
        
    Returns:
        bool: 创建成功返回 True，否则返回 False
    """
    try:
        if os.path.exists(sql_file_path):
            print(f"正在执行SQL文件: {sql_file_path}")
            
            # 读取SQL文件内容
            with open(sql_file_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            # 检查表名是否以 -数字 结尾
            match = re.match(r'^(.+)-(\d+)$', table_name)
            if match:
                # 提取 -数字 前部分作为基础表名
                base_table_name = match.group(1)
                print(f"已将表名 '{table_name}' 中的基础表名识别为 '{base_table_name}'")
                
                # 替换SQL中的表名为实际要创建的表名
                # 匹配 CREATE TABLE 语句中的表名
                pattern = rf'(CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+){re.escape(base_table_name)}'
                replacement = f'\\1"{table_name}"'
                sql_content_modified = re.sub(pattern, replacement, sql_content, flags=re.IGNORECASE)
                
                # 匹配 CREATE INDEX 语句中的表名
                pattern_idx = rf'(CREATE\s+(?:UNIQUE\s+)?INDEX(?:\s+IF\s+NOT\s+EXISTS)?\s+\w+\s+ON\s+){re.escape(base_table_name)}'
                replacement_idx = f'\\1"{table_name}"'
                sql_content_modified = re.sub(pattern_idx, replacement_idx, sql_content_modified, flags=re.IGNORECASE)
            else:
                # 如果表名不以 -数字 结尾，直接使用原始SQL，但加上引号
                pattern = r'(CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+)(\w+)'
                replacement = r'\1"\2"'
                sql_content_modified = re.sub(pattern, replacement, sql_content, flags=re.IGNORECASE)
                
                pattern_idx = r'(CREATE\s+(?:UNIQUE\s+)?INDEX(?:\s+IF\s+NOT\s+EXISTS)?\s+\w+\s+ON\s+)(\w+)'
                replacement_idx = r'\1"\2"'
                sql_content_modified = re.sub(pattern_idx, replacement_idx, sql_content_modified, flags=re.IGNORECASE)
            
            # 执行修改后的SQL脚本
            cursor = conn.cursor()
            # PostgreSQL 不支持 executescript，需要逐条执行
            # 分割 SQL 语句，注意处理可能在引号内的分号
            statements = sql_content_modified.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            
            conn.commit()
            cursor.close()
            print("SQL脚本执行完成")
            return True
        else:
            print(f"SQL文件不存在: {sql_file_path}")
            return False
    except Exception as e:
        print(f"执行SQL脚本出错: {e}")
        return False


maria_db_config = {
    'host': 'localhost',
    'port': 3306,
    'database': 'LaiCai',
    'user': 'root',
    'password': '123456',
    'charset': 'utf8mb4'
}

def get_db_connection(table_name: str) -> Optional[pymysql.connections.Connection]:
    """
    获取MariaDB数据库连接，如果表不存在则创建对应表
    
    Args:
        table_name (str): 表名
        
    Returns:
        pymysql.connections.Connection: 数据库连接对象，如果失败返回 None
    """
    try:
        # 连接数据库
        conn = pymysql.connect(**maria_db_config)
        
        # 检查表是否存在，如果不存在则创建
        if not check_table_exists(conn, table_name):
            print(f"检测到表 {table_name} 不存在，正在创建表...")
            # 检查表名是否以 -数字 结尾
            match = re.match(r'^(.+)-(\d+)$', table_name)
            if match:
                # 提取 -数字 前部分作为基础表名
                base_table_name = match.group(1)
                # 拼接 initsql 路径
                sql_file_path = f"./initsql/{base_table_name}.sql"
            else:
                sql_file_path = f"./initsql/{table_name}.sql"
                
            # 尝试从SQL文件创建表
            if not create_tables(conn, sql_file_path, table_name):
                # 如果SQL文件不存在或执行失败，使用默认建表语句
                conn.commit()
                print("数据库表创失败")
            
        return conn
    except Exception as e:
        print(f"连接数据库失败: {e}")
        return None


def drop_tables_with_numeric_suffix(conn: pymysql.connections.Connection) -> None:
    """
    删除数据库中带有数字后缀的表
    
    Args:
        conn (pymysql.connections.Connection): 数据库连接对象
    """
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = DATABASE()
    """)
    tables = cursor.fetchall()
    
    # 筛选出带有数字后缀的表（格式为：表名-数字）
    tables_to_drop = []
    for table in tables:
        table_name = table[0]
        # 使用正则表达式匹配带有数字后缀的表名（例如：tablename-123）
        if re.match(r'^.+-\d+$', table_name):
            tables_to_drop.append(table_name)
    
    # 删除这些表
    for table_name in tables_to_drop:
        print(f"正在删除表: {table_name}")
        cursor.execute('DROP TABLE IF EXISTS `%s`' % table_name)
    
    conn.commit()
    cursor.close()
    if tables_to_drop:
        print(f"已删除 {len(tables_to_drop)} 个带有数字后缀的表: {tables_to_drop}")
    else:
        print("没有找到带有数字后缀的表")


# 使用示例
if __name__ == "__main__":
    # 获取数据库连接
    conn = get_db_connection("raw_basic_info")
    
    if conn:
        # 测试数据库连接
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = DATABASE()
        """)
        tables = cursor.fetchall()
        print("当前数据库中的表:", [table[0] for table in tables])
        cursor.close()
        
        conn.close()