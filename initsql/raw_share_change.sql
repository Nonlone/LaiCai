-- 股票股本变动表
CREATE TABLE IF NOT EXISTS raw_share_change (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    name TEXT,
    change_date TEXT,
    announce_date TEXT,
    total REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引提高查询效率
CREATE INDEX IF NOT EXISTS idx_raw_share_change_code ON raw_share_change(code);
CREATE INDEX IF NOT EXISTS idx_raw_share_change_change_date ON raw_share_change(change_date);