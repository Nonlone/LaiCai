import akshare as ak
import pandas as pd


def calculate_dividend_yield(symbol):
    """计算股息率：每股分红 / 当前股价"""
    try:
        # 1. 获取最新股价
        stock_spot = ak.stock_zh_a_spot()
        stock_info = stock_spot[stock_spot['代码'] == symbol]

        if stock_info.empty:
            print(f"未找到股票 {symbol} 的实时行情")
            return None

        current_price = stock_info['最新价'].iloc[0]
        stock_name = stock_info['名称'].iloc[0]

        # 2. 获取分红数据
        dividend_data = ak.stock_fhps_detail_em(symbol=symbol)
        if dividend_data.empty:
            print(f"股票 {symbol} 无分红历史")
            return None

        # 3. 获取最新分红信息
        latest_dividend = dividend_data.iloc[0]
        dividend_per_share = latest_dividend['现金分红-现金分红比例']

        # 4. 计算股息率
        dividend_yield = latest_dividend['现金分红-股息率']

        result = {
            '股票代码': symbol,
            '股票名称': stock_name,
            '当前股价': current_price,
            '最新每股现金分红': dividend_per_share,
            '现金分红股息率': f"{dividend_yield:.2f}%",
            '分红年度': latest_dividend['分红年度'],
            '分红方案': latest_dividend['分红方案']
        }

        return result

    except Exception as e:
        print(f"计算股息率失败: {e}")
        return None


# 使用示例
if __name__ == "__main__":
    # 使用示例
    symbol = "601006"

    result = ak.stock_fhps_detail_em(symbol)
    print(result)

    columns = ['股权登记日', '除权除息日', '现金分红-股息率', '每股未分配利润',
               '每股收益', '每股公积金', '现金分红-现金分红比例描述', '现金分红-现金分红比例','预案公告日'] 
    process_data = []
    for _, row in result.iterrows():
        row_data = ()
        for i in columns:
            row_data += (row.get(i),)
        process_data.append(row_data)

    process_data = pd.DataFrame(process_data, columns=columns)
    process_data = process_data.sort_values(by='股权登记日', ascending=False)
    process_data = process_data.reset_index(drop=True)
    # 输出对其列的数据
    print(process_data)

    result = ak.stock_fhps_detail_ths(symbol)
    # print(result)
    columns = ['报告期', '实施公告日', '分红总额', '股利支付率']
    process_data = []
    for _, row in result.iterrows():
        # 如果实施公告期不是时间则跳过
        if pd.isna(row.get('实施公告日')):
            continue
        row_data = ()
        for i in columns:
            row_data += (row.get(i),)
        process_data.append(row_data)

    process_data = pd.DataFrame(process_data, columns=columns)
    process_data = process_data.sort_values(by='实施公告日', ascending=False)
    process_data = process_data.reset_index(drop=True)
    # 输出对其列的数据
    print(process_data)
