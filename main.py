import akshare as ak
import pandas as pd



def stock_day_detail(symbol: str,date=str) -> float:
    """
    获取某个股票某天行情
    """
    # 获取数据
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",  # 日频数据
        start_date=date,
        end_date=date,
        adjust="qfq"  # 前复权
    )
    for _, row in df.iterrows():
       finish_price = row.get('收盘价')
       if finish_price:
           return finish_price
    return 





# 使用示例
if __name__ == "__main__":
    # 使用示例
    symbol = "601006"
    finish_price  = stock_day_detail(symbol,"20070618")
    if not finish_price:
        print("没有获取到数据")

    result = ak.stock_fhps_detail_em(symbol)
    print(result)

    columns = ['除权除息日','股权登记日', '现金分红-股息率', '每股未分配利润',
               '每股收益', '每股公积金', '现金分红-现金分红比例','预案公告日'] 
    process_data = []
    for _, row in result.iterrows():
        if pd.isna(row.get('除权除息日')):
            #  如果除权除息日不是时间则跳过
            continue
        divide_date = row.get('除权除息日').strftime("%Y%m%d")
        stock_detail = stock_day_detail(symbol, divide_date)
       

        row_data = ()
        for i in columns:
            row_data += (row.get(i),)

        row_data += stock_detail
        
        process_data.append(row_data)

    process_data = pd.DataFrame(process_data, columns=columns.append(['股票收盘价']))
    process_data = process_data.sort_values(by='除权除息日', ascending=False)
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
    # print(process_data)

    


