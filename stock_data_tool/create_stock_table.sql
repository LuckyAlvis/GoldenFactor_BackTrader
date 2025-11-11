-- ============================================
-- 美股数据表结构设计
-- 数据库：ry-vue
-- 用途：存储美股历史数据（OHLCV）
-- ============================================

-- 1. 创建美股历史数据表
DROP TABLE IF EXISTS `us_stock_data`;

CREATE TABLE `us_stock_data` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `symbol` VARCHAR(20) NOT NULL COMMENT '股票代码（如：TSLA, AAPL）',
  `trade_date` DATETIME NOT NULL COMMENT '交易日期时间',
  `open_price` DECIMAL(12,4) NOT NULL COMMENT '开盘价',
  `high_price` DECIMAL(12,4) NOT NULL COMMENT '最高价',
  `low_price` DECIMAL(12,4) NOT NULL COMMENT '最低价',
  `close_price` DECIMAL(12,4) NOT NULL COMMENT '收盘价',
  `volume` BIGINT(20) NOT NULL COMMENT '成交量',
  `dividends` DECIMAL(12,4) DEFAULT 0.0000 COMMENT '股息',
  `stock_splits` DECIMAL(12,4) DEFAULT 0.0000 COMMENT '股票拆分比例',
  `interval_type` VARCHAR(10) DEFAULT '1d' COMMENT 'K线类型（1m,5m,1h,1d,1wk,1mo）',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_symbol_date_interval` (`symbol`, `trade_date`, `interval_type`),
  KEY `idx_symbol` (`symbol`),
  KEY `idx_trade_date` (`trade_date`),
  KEY `idx_symbol_date` (`symbol`, `trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='美股历史数据表';

-- 2. 创建美股实时信息表
DROP TABLE IF EXISTS `us_stock_realtime`;

CREATE TABLE `us_stock_realtime` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `symbol` VARCHAR(20) NOT NULL COMMENT '股票代码',
  `company_name` VARCHAR(200) DEFAULT NULL COMMENT '公司名称',
  `current_price` DECIMAL(12,4) DEFAULT NULL COMMENT '当前价格',
  `open_price` DECIMAL(12,4) DEFAULT NULL COMMENT '开盘价',
  `high_price` DECIMAL(12,4) DEFAULT NULL COMMENT '最高价',
  `low_price` DECIMAL(12,4) DEFAULT NULL COMMENT '最低价',
  `previous_close` DECIMAL(12,4) DEFAULT NULL COMMENT '前收盘价',
  `volume` BIGINT(20) DEFAULT NULL COMMENT '成交量',
  `market_cap` BIGINT(20) DEFAULT NULL COMMENT '市值',
  `pe_ratio` DECIMAL(12,4) DEFAULT NULL COMMENT '市盈率',
  `week_52_high` DECIMAL(12,4) DEFAULT NULL COMMENT '52周最高价',
  `week_52_low` DECIMAL(12,4) DEFAULT NULL COMMENT '52周最低价',
  `change_percent` DECIMAL(12,4) DEFAULT NULL COMMENT '涨跌幅（%）',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_symbol` (`symbol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='美股实时信息表';

-- 3. 创建股票列表表（可选，用于管理关注的股票）
DROP TABLE IF EXISTS `us_stock_list`;

CREATE TABLE `us_stock_list` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `symbol` VARCHAR(20) NOT NULL COMMENT '股票代码',
  `company_name` VARCHAR(200) DEFAULT NULL COMMENT '公司名称',
  `industry` VARCHAR(100) DEFAULT NULL COMMENT '所属行业',
  `sector` VARCHAR(100) DEFAULT NULL COMMENT '所属板块',
  `market` VARCHAR(50) DEFAULT 'US' COMMENT '市场（US/HK/CN）',
  `status` TINYINT(1) DEFAULT 1 COMMENT '状态（0-停用，1-启用）',
  `remark` VARCHAR(500) DEFAULT NULL COMMENT '备注',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_symbol` (`symbol`),
  KEY `idx_industry` (`industry`),
  KEY `idx_sector` (`sector`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='美股列表表';

-- 4. 插入一些常用的科技股到股票列表
INSERT INTO `us_stock_list` (`symbol`, `company_name`, `industry`, `sector`, `status`) VALUES
('TSLA', 'Tesla, Inc.', 'Automotive', 'Technology', 1),
('AAPL', 'Apple Inc.', 'Consumer Electronics', 'Technology', 1),
('MSFT', 'Microsoft Corporation', 'Software', 'Technology', 1),
('GOOGL', 'Alphabet Inc.', 'Internet', 'Technology', 1),
('AMZN', 'Amazon.com, Inc.', 'E-commerce', 'Technology', 1),
('META', 'Meta Platforms, Inc.', 'Social Media', 'Technology', 1),
('NVDA', 'NVIDIA Corporation', 'Semiconductors', 'Technology', 1),
('NFLX', 'Netflix, Inc.', 'Streaming', 'Technology', 1);

-- 5. 创建索引优化查询
-- 已在表创建时添加

-- 6. 查询示例
-- 查询特斯拉最近30天的数据
-- SELECT * FROM us_stock_data WHERE symbol = 'TSLA' AND interval_type = '1d' ORDER BY trade_date DESC LIMIT 30;

-- 查询特斯拉的价格统计
-- SELECT 
--   symbol,
--   COUNT(*) as record_count,
--   MIN(low_price) as min_price,
--   MAX(high_price) as max_price,
--   AVG(close_price) as avg_price,
--   SUM(volume) as total_volume
-- FROM us_stock_data 
-- WHERE symbol = 'TSLA' AND interval_type = '1d'
-- GROUP BY symbol;

-- 查询多只股票的最新价格
-- SELECT 
--   d.symbol,
--   l.company_name,
--   d.close_price,
--   d.volume,
--   d.trade_date
-- FROM us_stock_data d
-- LEFT JOIN us_stock_list l ON d.symbol = l.symbol
-- WHERE d.interval_type = '1d'
-- AND d.trade_date = (
--   SELECT MAX(trade_date) 
--   FROM us_stock_data 
--   WHERE symbol = d.symbol AND interval_type = '1d'
-- )
-- ORDER BY d.symbol;
