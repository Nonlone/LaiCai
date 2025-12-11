import akshare as ak
import pymysql
from db import get_db_connection
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
import random
import time
import pandas as pd


@dataclass
class StockBasicInfo:
    """股票基本信息数据类，映射 stock_basic_info 表结构"""
    code: str
    name: str
    market: str
    created_at: Optional[datetime] = None


def sync_stock_basic_info() -> List[StockBasicInfo]:
    """
    同步 akshare 的 stock_info_a_code_name 方法返回数据到 stock_basic_info 表中
    
    Returns:
        List[StockBasicInfo]: 同步的股票基本信息对象数组
    """
    stock_objects: List[StockBasicInfo] = []
    # 定义表名常量
    TABLE_NAME = "raw_basic_info"
    # 生成临时表名，格式为原表名-随机数（符合 db.py 中的处理逻辑）
    # TEMP_TABLE_NAME = f"{TABLE_NAME}-{random.randint(100, 999)}"
    
    try:
        # 获取数据库连接，使用临时表名
        conn = get_db_connection(TABLE_NAME)
        if not conn:
            raise Exception("无法建立数据库连接")
            
        cursor = conn.cursor()
        
        # 使用 akshare 获取所有股票代码和名称
        stock_info_df = ak.stock_info_a_code_name()
        
        # 准备插入数据
        stock_data = []
        for _, row in stock_info_df.iterrows():
            code = row['code']
            name = row['name']
            
            # 根据股票代码判断市场类型
            if code.startswith('6'):
                market = 'SH'  # 上海
            elif code.startswith(('0', '3')):
                market = 'SZ'  # 深圳
            else:
                market = 'Unknown'
                
            stock_data.append((code, name, market))
            stock_objects.append(StockBasicInfo(code=code, name=name, market=market))
        
        # 批量插入或更新数据到临时表
        # MariaDB 使用 ON DUPLICATE KEY UPDATE 子句替代 INSERT OR REPLACE
        cursor.executemany(f'''
            INSERT INTO `{TABLE_NAME}` (code, name, market)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                name = VALUES(name),
                market = VALUES(market)
        ''', stock_data)
        
        conn.commit()

        
    except Exception as e:
        print(f"同步股票基本信息时发生错误: {e}")
        stock_objects = []
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            
    return stock_objects


if __name__ == "__main__":
    sync_stock_basic_info()