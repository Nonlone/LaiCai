import sqlite3
import os
import re

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
    conn = sqlite3.connect(db_path)
    
    # 检查表是否存在，如果不存在则创建
    if not check_table_exists(conn, table_name):
        print("检测到表不存在，正在创建表...")
        # 检查表名是否以 -数字 结尾
        match = re.match(r'^(.+)-(\d+)$', table_name)
        if match:
            # 提取 -数字 前部分
            base_table_name = match.group(1)
            # 拼接 initsql 路径
            sql_file_path = f"./initsql/{base_table_name}.sql"
            # 调用 create_tables 方法创建表
            create_tables(conn, sql_file_path,base_table_name,table_name)
        else:
            # 使用原始表名构建 SQL 文件路径
            sql_file_path = f"./initsql/{table_name}.sql"
            create_tables(conn, sql_file_path)
    
    return conn

def check_table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """
    检查指定表是否存在于数据库中
    
    Args:
        conn (sqlite3.Connection): 数据库连接对象
        table_name (str): 表名
        
    Returns:
        bool: 表存在返回True，否则返回False
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None

def create_default_tables(conn: sqlite3.Connection) -> None:
    """
    创建默认数据库表（当SQL文件不存在或执行出错时使用）
    
    Args:
        conn (sqlite3.Connection): 数据库连接对象
    """
    cursor = conn.cursor()
    
    # 创建股票基本信息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_basic_info (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            market TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建股票价格表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            turnover REAL,
            FOREIGN KEY (code) REFERENCES stock_basic_info(code),
            UNIQUE(code, date)
        )
    ''')
    
    # 创建索引提高查询效率
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_code ON stock_basic_info(code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_code_date ON stock_prices(code, date)')
    
    conn.commit()
    print("默认数据库表创建完成")

def create_tables(conn: sqlite3.Connection, sql_file_path: str = "schema.sql", 
                  placeholder: str = None, replacement: str = None) -> None:
    """
    通过执行外部SQL文件创建数据库表
    
    Args:
        conn (sqlite3.Connection): 数据库连接对象
        sql_file_path (str): SQL文件路径，默认为"schema.sql"
        placeholder (str): SQL文件中的占位符，可选
        replacement (str): 替换占位符的字符串，可选
    """
    cursor = conn.cursor()
    
    # 检查SQL文件是否存在
    if not os.path.exists(sql_file_path):
        print(f"警告: SQL文件 {sql_file_path} 不存在")
        # 使用原来的默认建表语句
    else:
        print(f"正在执行SQL文件: {sql_file_path}")
        # 读取并执行SQL文件
        with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
            sql_script = sql_file.read()
        
        # 如果提供了占位符和替换文本，则进行替换
        if placeholder is not None and replacement is not None:
            sql_script = sql_script.replace(placeholder, replacement)
            print(f"已将 '{placeholder}' 替换为 '{replacement}'")
        
        # 执行整个脚本
        try:
            cursor.executescript(sql_script)
            print("SQL脚本执行成功")
        except sqlite3.Error as e:
            print(f"执行SQL脚本出错: {e}")
            print("使用默认建表语句...")
        finally:
            conn.commit()
    
    print("数据库表创建完成")

# 使用示例
if __name__ == "__main__":
    # 获取数据库连接
    conn = get_db_connection("stocks.db", "stock_basic_info")
    
    # 测试数据库连接
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("当前数据库中的表:", [table[0] for table in tables])
    
    conn.close()