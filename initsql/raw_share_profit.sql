-- 股票分红数据表
CREATE TABLE IF NOT EXISTS raw_share_profit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    name TEXT,
    reporting_period TEXT,
    announcement_date TEXT,
    dividend_amount REAL,
    payout_ratio REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引提高查询效率
CREATE INDEX IF NOT EXISTS idx_raw_share_profit_code ON raw_share_profit(code);
CREATE INDEX IF NOT EXISTS idx_raw_share_profit_announcement_date ON raw_share_profit(announcement_date);