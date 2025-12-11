-- 股票基本信息表
CREATE TABLE IF NOT EXISTS `raw_basic_info` (
    `code` VARCHAR(10) PRIMARY KEY,
    `name` TEXT NOT NULL,
    `market` VARCHAR(10),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引提高查询效率
CREATE INDEX IF NOT EXISTS `idx_stock_code` ON `raw_basic_info`(`code`);