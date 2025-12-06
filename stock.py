import akshare as ak
import psycopg2
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
    TEMP_TABLE_NAME = f"{TABLE_NAME}-{random.randint(100, 999)}"
    
    try:
        # 获取数据库连接，使用临时表名
        conn = get_db_connection(TEMP_TABLE_NAME)
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
        # PostgreSQL 使用 ON CONFLICT 子句替代 INSERT OR REPLACE
        cursor.executemany(f'''
            INSERT INTO "{TEMP_TABLE_NAME}" (code, name, market)
            VALUES (%s, %s, %s)
            ON CONFLICT (code) 
            DO UPDATE SET 
                name = EXCLUDED.name,
                market = EXCLUDED.market
        ''', stock_data)
        
        conn.commit()
        print(f"成功同步 {len(stock_data)} 只股票的基本信息到临时表 {TEMP_TABLE_NAME}")
        
        # 将临时表重命名为正式表名
        try:
            # 先删除已存在的正式表（如果存在）
            cursor.execute(f'DROP TABLE IF EXISTS "{TABLE_NAME}" CASCADE')
            # 将临时表重命名为正式表名
            cursor.execute(f'ALTER TABLE "{TEMP_TABLE_NAME}" RENAME TO "{TABLE_NAME}"')
            conn.commit()
            print(f"成功将临时表 {TEMP_TABLE_NAME} 重命名为 {TABLE_NAME}")
        except psycopg2.Error as e:
            print(f"重命名表时发生错误: {e}")
        
    except Exception as e:
        print(f"同步股票基本信息时发生错误: {e}")
        stock_objects = []
    finally:
        # 先删除临时表
        cursor.execute(f'DROP TABLE IF EXISTS "{TEMP_TABLE_NAME}" CASCADE')
        if 'conn' in locals() and conn:
            conn.close()
            
    return stock_objects


def sync_stock_share_change(stocks: List[StockBasicInfo] = None) -> None:
    """
    同步股票股本变动数据到 raw_share_change 表中
    
    Args:
        stocks (List[StockBasicInfo]): 股票列表
    """
    if not stocks:
        print("未提供股票列表，终止同步")
        return
    
    # 定义表名常量
    TABLE_NAME = "raw_share_change"
    # 生成临时表名，格式为原表名-随机数（符合 db.py 中的处理逻辑）
    TEMP_TABLE_NAME = f"{TABLE_NAME}-{random.randint(100, 999)}"
    
    # 最多重试次数
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 获取数据库连接，使用临时表名
            conn = get_db_connection(TEMP_TABLE_NAME)
            if not conn:
                raise Exception("无法建立数据库连接")
                
            cursor = conn.cursor()
            
            total_count = 0
            error_count = 0
            
            # 处理每只股票的股本变动数据
            for stock in stocks:
                try:
                    # 使用 akshare 获取单只股票的股本变动数据
                    share_change_df = ak.stock_share_change_cninfo(symbol=stock.code)
                    
                    if share_change_df.empty:
                        continue
                    
                    # 准备插入数据
                    share_change_data = []
                    for _, row in share_change_df.iterrows():
                        # 安全地获取各字段值，如果字段不存在则使用默认值
                        row_data = (
                            stock.code,  # code 字段
                            row.get('证券简称', ''),  # name 字段，如果找不到则置空
                            row.get('变动日期', ''),  # change_date 字段，如果找不到则置空
                            row.get('公告日期', ''),  # announce_date 字段，如果找不到则置空
                            row.get('总股本')   # total 字段
                        )
                        share_change_data.append(row_data)
                    
                    # 批量插入数据到临时表
                    # PostgreSQL 使用 ON CONFLICT DO NOTHING 替代 INSERT OR REPLACE
                    cursor.executemany(f'''
                        INSERT INTO "{TEMP_TABLE_NAME}" (
                            code, name, change_date, announce_date, total
                        ) VALUES (
                            %s, %s, %s, %s, %s
                        )
                        ON CONFLICT DO NOTHING
                    ''', share_change_data)
                    
                    total_count += len(share_change_data)
                    
                except Exception as e:
                    error_count += 1
                    print(f"获取股票 {stock.code} 的股本变动数据时发生错误: {e}")
                    # 继续处理下一个股票而不是中断整个过程
                    continue
                finally:
                    # 每次请求后等待1秒，减轻服务器压力
                    time.sleep(1)
            
            conn.commit()
            print(f"成功同步 {total_count} 条股本变动记录到临时表 {TEMP_TABLE_NAME}")
            if error_count > 0:
                print(f"处理过程中有 {error_count} 只股票发生错误")
            
            # 将临时表重命名为正式表名
            try:
                # 先删除已存在的正式表（如果存在）
                cursor.execute(f'DROP TABLE IF EXISTS "{TABLE_NAME}" CASCADE')
                # 将临时表重命名为正式表名
                cursor.execute(f'ALTER TABLE "{TEMP_TABLE_NAME}" RENAME TO "{TABLE_NAME}"')
                conn.commit()
                print(f"成功将临时表 {TEMP_TABLE_NAME} 重命名为 {TABLE_NAME}")
            except psycopg2.Error as e:
                print(f"重命名表时发生错误: {e}")
            
            break  # 成功执行后跳出重试循环
            
        except psycopg2.OperationalError as e:
            if "database is locked" in str(e) and retry_count < max_retries - 1:
                retry_count += 1
                print(f"数据库被锁定，进行第 {retry_count} 次重试...")
                time.sleep(random.uniform(1, 3))  # 随机等待一段时间再重试
            else:
                print(f"同步股票股本变动数据时发生错误: {e}")
                break
        except Exception as e:
            print(f"同步股票股本变动数据时发生错误: {e}")
            break
        finally:
            if 'conn' in locals() and conn:
                conn.close()


def sync_stock_share_profit(stocks: List[StockBasicInfo] = None) -> None:
    """
    同步股票分红数据到 raw_share_profit 表中
    
    Args:
        stocks (List[StockBasicInfo]): 股票列表
    """
    if not stocks:
        print("未提供股票列表，终止同步")
        return
    
    # 定义表名常量
    TABLE_NAME = "raw_share_profit"
    # 生成临时表名，格式为原表名-随机数（符合 db.py 中的处理逻辑）
    TEMP_TABLE_NAME = f"{TABLE_NAME}-{random.randint(100, 999)}"
    
    # 最多重试次数
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 获取数据库连接，使用临时表名
            conn = get_db_connection(TEMP_TABLE_NAME)
            if not conn:
                raise Exception("无法建立数据库连接")
                
            cursor = conn.cursor()
            
            total_count = 0
            error_count = 0
            
            # 处理每只股票的分红数据
            for stock in stocks:
                try:
                    # 使用 akshare 获取单只股票的分红数据
                    share_profit_df = ak.stock_fhps_detail_ths(symbol=stock.code)
                    
                    if share_profit_df.empty:
                        continue
                    
                    # 准备插入数据
                    share_profit_data = []
                    for _, row in share_profit_df.iterrows():
                        # 如果实施公告日期为空值则跳过该行
                        if pd.isna(row.get('实施公告日')):
                            continue
                        
                        # 安全地获取各字段值，如果字段不存在则使用默认值
                        row_data = (
                            stock.code,  # code 字段
                            row.get('股票简称', stock.name),  # name 字段
                            row.get('报告期', ''),  # reporting_period 字段
                            row.get('实施公告日', ''),  # announcement_date 字段
                            row.get('分红总额', 0),  # dividend_amount 字段
                            row.get('股利支付率', 0)   # payout_ratio 字段
                        )
                        share_profit_data.append(row_data)
                    
                    # 批量插入数据到临时表
                    # PostgreSQL 使用 ON CONFLICT DO NOTHING 替代 INSERT OR REPLACE
                    cursor.executemany(f'''
                        INSERT INTO "{TEMP_TABLE_NAME}" (
                            code, name, reporting_period, announcement_date, dividend_amount, payout_ratio
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT DO NOTHING
                    ''', share_profit_data)
                    
                    total_count += len(share_profit_data)
                    
                except Exception as e:
                    error_count += 1
                    print(f"获取股票 {stock.code} 的分红数据时发生错误: {e}")
                    # 继续处理下一个股票而不是中断整个过程
                    continue
                finally:
                    # 每次请求后等待1秒，减轻服务器压力
                    time.sleep(1)
            
            conn.commit()
            print(f"成功同步 {total_count} 条分红记录到临时表 {TEMP_TABLE_NAME}")
            if error_count > 0:
                print(f"处理过程中有 {error_count} 只股票发生错误")
            
            # 将临时表重命名为正式表名
            try:
                # 先删除已存在的正式表（如果存在）
                cursor.execute(f'DROP TABLE IF EXISTS "{TABLE_NAME}" CASCADE')
                # 将临时表重命名为正式表名
                cursor.execute(f'ALTER TABLE "{TEMP_TABLE_NAME}" RENAME TO "{TABLE_NAME}"')
                conn.commit()
                print(f"成功将临时表 {TEMP_TABLE_NAME} 重命名为 {TABLE_NAME}")
            except psycopg2.Error as e:
                print(f"重命名表时发生错误: {e}")
            
            break  # 成功执行后跳出重试循环
            
        except psycopg2.OperationalError as e:
            if "database is locked" in str(e) and retry_count < max_retries - 1:
                retry_count += 1
                print(f"数据库被锁定，进行第 {retry_count} 次重试...")
                time.sleep(random.uniform(1, 3))  # 随机等待一段时间再重试
            else:
                print(f"同步股票分红数据时发生错误: {e}")
                break
        except Exception as e:
            print(f"同步股票分红数据时发生错误: {e}")
            break
        finally:
            if 'conn' in locals() and conn:
                conn.close()


def sync_stock(batch_size: int = 50) -> None:
    """
    协调股票数据同步过程
    
    Args:
        batch_size (int): 批量处理大小（此参数在此版本中未使用，为了保持接口兼容性保留）
    """
    # 先同步股票基本信息
    print("开始同步股票基本信息...")
    stocks = sync_stock_basic_info()
    
    if not stocks:
        print("未能获取股票基本信息，终止同步")
        return
    
    print(f"获取到 {len(stocks)} 只股票，开始同步股本变动数据...")
    
    # 获取到股票列表后，判断是否需要限制数量
    max_sync_count = 2000
    if len(stocks) > max_sync_count:
        import random
        print(f"获取到 {len(stocks)} 只股票，超过{max_sync_count}只，随机抽取{max_sync_count}只进行股本变动数据同步...")
        stocks_to_sync = random.sample(stocks, max_sync_count)
    else:
        stocks_to_sync = stocks
    
    # 同步股票股本变动数据
    sync_stock_share_change(stocks_to_sync)
    
    # 同步股票分红数据
    print(f"开始同步{len(stocks_to_sync)}只股票的分红数据...")
    sync_stock_share_profit(stocks_to_sync)
    
    print("股票数据同步完成")


# 使用示例
if __name__ == "__main__":
    # print(ak.stock_info_a_code_name())
   sync_stock_basic_info()
