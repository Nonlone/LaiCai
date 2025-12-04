import sqlite3
import os
import re
from datetime import date, datetime


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


# 注册自定义适配器和转换器
sqlite3.register_adapter(date, adapt_date)
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("date", convert_date)
sqlite3.register_converter("timestamp", convert_timestamp)


def check_table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """
    检查表是否存在
    
    Args:
        conn (sqlite3.Connection): 数据库连接对象
        table_name (str): 表名
        
    Returns:
        bool: 表存在返回 True，否则返回 False
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
        (table_name,)
    )
    return cursor.fetchone() is not None


def create_tables(conn: sqlite3.Connection, sql_file_path: str, table_name: str) -> bool:
    """
    从SQL文件创建表
    
    Args:
        conn (sqlite3.Connection): 数据库连接对象
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
                pattern_idx = rf'(CREATE\s+INDEX(?:\s+IF\s+NOT\s+EXISTS)?\s+\w+\s+ON\s+){re.escape(base_table_name)}'
                replacement_idx = f'\\1"{table_name}"'
                sql_content_modified = re.sub(pattern_idx, replacement_idx, sql_content_modified, flags=re.IGNORECASE)
            else:
                # 如果表名不以 -数字 结尾，直接使用原始SQL，但加上引号
                pattern = r'(CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+)(\w+)'
                replacement = r'\1"\2"'
                sql_content_modified = re.sub(pattern, replacement, sql_content, flags=re.IGNORECASE)
                
                pattern_idx = r'(CREATE\s+INDEX(?:\s+IF\s+NOT\s+EXISTS)?\s+\w+\s+ON\s+)(\w+)'
                replacement_idx = r'\1"\2"'
                sql_content_modified = re.sub(pattern_idx, replacement_idx, sql_content_modified, flags=re.IGNORECASE)
            
            # 执行修改后的SQL脚本
            cursor = conn.cursor()
            cursor.executescript(sql_content_modified)
            conn.commit()
            print("SQL脚本执行完成")
            return True
        else:
            print(f"SQL文件不存在: {sql_file_path}")
            return False
    except Exception as e:
        print(f"执行SQL脚本出错: {e}")
        return False


def get_db_connection(db_path: str, table_name: str) -> sqlite3.Connection:
    """
    获取SQLite数据库连接，如果数据库文件不存在则创建新文件，
    如果表不存在则创建对应表
    
    Args:
        db_path (str): 数据库文件的相对路径
        table_name (str): 表名
        
    Returns:
        sqlite3.Connection: 数据库连接对象
    """
    # 检查数据库文件是否存在
    db_exists = os.path.exists(db_path)
    
    # 连接数据库（如果文件不存在会自动创建）
    # 使用自定义类型检测标志来启用转换器
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    
    # 检查表是否存在，如果不存在则创建
    if not check_table_exists(conn, table_name):
        print("检测到表不存在，正在创建表...")
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
            print("使用默认建表语句...")
            cursor = conn.cursor()
            
            conn.commit()
            print("数据库表创建完成")
        
    return conn



def drop_tables_with_numeric_suffix(conn: sqlite3.Connection) -> None:
    """
    删除数据库中带有数字后缀的表
    
    Args:
        conn (sqlite3.Connection): 数据库连接对象
    """
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
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
        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    
    conn.commit()
    if tables_to_drop:
        print(f"已删除 {len(tables_to_drop)} 个带有数字后缀的表: {tables_to_drop}")
    else:
        print("没有找到带有数字后缀的表")

# 使用示例
if __name__ == "__main__":
    # 获取数据库连接
    conn = get_db_connection("stocks.db", "raw_basic_info")
    
    # 测试数据库连接
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("当前数据库中的表:", [table[0] for table in tables])

    # 测试删除临时表
    drop_tables_with_numeric_suffix(conn)
    
    conn.close()