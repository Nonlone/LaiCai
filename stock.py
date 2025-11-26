import akshare as ak
import sqlite3
from db import get_db_connection
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class StockBasicInfo:
    """股票基本信息数据类，映射 stock_basic_info 表结构"""
    code: str
    name: str
    market: str
    created_at: Optional[datetime] = None


def sync_stock_basic_info(db_path: str = "stocks.db") -> List[StockBasicInfo]:
    """
    同步 akshare 的 stock_info_a_code_name 方法返回数据到 stock_basic_info 表中
    
    Args:
        db_path (str): 数据库文件路径，默认为 "stocks.db"
        
    Returns:
        List[StockBasicInfo]: 同步的股票基本信息对象数组
    """
    stock_objects: List[StockBasicInfo] = []
    # 定义表名常量
    TABLE_NAME = "raw_basic_info"
    
    try:
        # 获取数据库连接
        conn = get_db_connection(db_path, TABLE_NAME)
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
        
        # 批量插入或更新数据
        cursor.executemany(f'''
            INSERT OR REPLACE INTO {TABLE_NAME} (code, name, market)
            VALUES (?, ?, ?)
        ''', stock_data)
        
        conn.commit()
        print(f"成功同步 {len(stock_data)} 只股票的基本信息到数据库")
        
    except Exception as e:
        print(f"同步股票基本信息时发生错误: {e}")
        stock_objects = []
    finally:
        if 'conn' in locals():
            conn.close()
            
    return stock_objects


def sync_stock_share_change(db_path: str, stocks: List[StockBasicInfo]) -> None:
    """
    同步股票股本变动数据到 raw_share_change 表中
    
    Args:
        db_path (str): 数据库文件路径
        stocks (List[StockBasicInfo]): 股票基本信息对象数组
    """
    TABLE_NAME = "raw_share_change"
    
    try:
        # 获取数据库连接
        conn = get_db_connection(db_path, TABLE_NAME)
        cursor = conn.cursor()
        
        total_count = 0
        error_count = 0
        
        # 遍历所有股票，获取股本变动数据
        for i, stock in enumerate(stocks):
            try:
                # 显示进度
                if i % 100 == 0:
                    print(f"处理进度: {i}/{len(stocks)}")
                
                # 使用 akshare 获取单只股票的股本变动数据
                share_change_df = ak.stock_share_change_cninfo(symbol=stock.code)
                
                if share_change_df.empty:
                    continue
                
                # 准备插入数据
                share_change_data = []
                for _, row in share_change_df.iterrows():
                    # 使用 get 方法安全访问字段，避免 KeyError 异常
                    row_data = (
                        stock.code,  # code 字段
                        row.get('证券简称'),  # name 字段
                        row.get('变动日期'),  # change_date 字段
                        row.get('公告日期'),  # announce_date 字段
                        row.get('总股本')   # total 字段
                    )
                    share_change_data.append(row_data)
                
                # 批量插入数据
                cursor.executemany(f'''
                    INSERT OR REPLACE INTO {TABLE_NAME} (
                        code, name, change_date, announce_date, total
                    ) VALUES (
                        ?, ?, ?, ?, ?
                    )
                ''', share_change_data)
                
                total_count += len(share_change_data)
                
            except Exception as e:
                # 记录错误但不中断整个过程
                print(f"获取或处理股票 {stock.code} 的股本变动数据时发生错误: {e}")
                error_count += 1
                continue
        
        conn.commit()
        print(f"成功同步 {total_count} 条股本变动记录到数据库，{error_count} 只股票处理失败")
        
    except Exception as e:
        print(f"同步股票股本变动数据时发生错误: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


def sync_stock(db_path: str = "stocks.db", batch_size: int = 50) -> None:
    """
    协调股票数据同步过程
    
    Args:
        db_path (str): 数据库文件路径
        batch_size (int): 批量处理大小（此参数在此版本中未使用，为了保持接口兼容性保留）
    """
    # 先同步股票基本信息
    print("开始同步股票基本信息...")
    stocks = sync_stock_basic_info(db_path)
    
    if not stocks:
        print("未能获取股票基本信息，终止同步")
        return
    
    print(f"获取到 {len(stocks)} 只股票，开始同步股本变动数据...")
    
    # 串行处理所有股票，避免数据库锁定问题
    sync_stock_share_change(db_path, stocks)
    
    print("股票数据同步完成")


# 使用示例
if __name__ == "__main__":
    stocks = sync_stock_basic_info()
    print(f"\n返回了 {len(stocks)} 个股票对象")
    if stocks:
        print("前5个股票对象:")
        for stock in stocks[:5]:
            print(f"  代码: {stock.code}, 名称: {stock.name}, 市场: {stock.market}")