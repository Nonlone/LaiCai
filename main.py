import akshare as ak


# 使用示例
if __name__ == "__main__":
    temp = ak.stock_share_change_cninfo(symbol="600519")
    
    # 获取列名和对应的索引
    column_names = temp.columns.tolist()
    column_indices = {name: index for index, name in enumerate(column_names)}
    
    code_index = column_indices.get('证券代码', 25)
    simple_name_index = column_indices.get('证券简称', 0)
    announcement_date_index = column_indices.get('公告日期', 23)
    change_date_index = column_indices.get('变动日期', 26)
    total_equity_index = column_indices.get('总股本', 34)
    
    for t in temp.values.tolist():
        # 通过列名获取索引，然后获取对应的数据
        print(f'{t[code_index]} {t[simple_name_index]} {t[announcement_date_index]} {t[change_date_index]} {t[total_equity_index]}')