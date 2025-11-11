# MySQL数据库使用说明

## 📋 概述

本文档说明如何将美股数据保存到MySQL数据库，以及如何查询和使用这些数据。

---

## 🗄️ 数据库信息

### 连接信息

```
主机: 101.37.164.75
端口: 3307
数据库: ry-vue
用户名: root
密码: Cd40k1SKIXBQ
字符集: utf8mb4
```

### JDBC连接字符串

```
jdbc:mysql://101.37.164.75:3307/ry-vue?useUnicode=true&characterEncoding=utf8&zeroDateTimeBehavior=convertToNull&useSSL=true&serverTimezone=GMT%2B8
```

---

## 📊 数据表结构

### 1. us_stock_data（美股历史数据表）

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | BIGINT(20) | 主键ID | 自增 |
| symbol | VARCHAR(20) | 股票代码 | 如：TSLA, AAPL |
| trade_date | DATETIME | 交易日期时间 | 精确到秒 |
| open_price | DECIMAL(12,4) | 开盘价 | 4位小数 |
| high_price | DECIMAL(12,4) | 最高价 | 4位小数 |
| low_price | DECIMAL(12,4) | 最低价 | 4位小数 |
| close_price | DECIMAL(12,4) | 收盘价 | 4位小数 |
| volume | BIGINT(20) | 成交量 | 股数 |
| dividends | DECIMAL(12,4) | 股息 | 默认0 |
| stock_splits | DECIMAL(12,4) | 股票拆分比例 | 默认0 |
| interval_type | VARCHAR(10) | K线类型 | 1m,5m,1h,1d,1wk,1mo |
| create_time | DATETIME | 创建时间 | 自动生成 |
| update_time | DATETIME | 更新时间 | 自动更新 |

**索引**：
- 主键：`id`
- 唯一索引：`uk_symbol_date_interval` (symbol, trade_date, interval_type)
- 普通索引：`idx_symbol` (symbol)
- 普通索引：`idx_trade_date` (trade_date)

### 2. us_stock_realtime（美股实时信息表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT(20) | 主键ID |
| symbol | VARCHAR(20) | 股票代码 |
| company_name | VARCHAR(200) | 公司名称 |
| current_price | DECIMAL(12,4) | 当前价格 |
| open_price | DECIMAL(12,4) | 开盘价 |
| high_price | DECIMAL(12,4) | 最高价 |
| low_price | DECIMAL(12,4) | 最低价 |
| previous_close | DECIMAL(12,4) | 前收盘价 |
| volume | BIGINT(20) | 成交量 |
| market_cap | BIGINT(20) | 市值 |
| pe_ratio | DECIMAL(12,4) | 市盈率 |
| week_52_high | DECIMAL(12,4) | 52周最高价 |
| week_52_low | DECIMAL(12,4) | 52周最低价 |
| change_percent | DECIMAL(12,4) | 涨跌幅(%) |
| update_time | DATETIME | 更新时间 |

**索引**：
- 主键：`id`
- 唯一索引：`uk_symbol` (symbol)

### 3. us_stock_list（美股列表表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT(20) | 主键ID |
| symbol | VARCHAR(20) | 股票代码 |
| company_name | VARCHAR(200) | 公司名称 |
| industry | VARCHAR(100) | 所属行业 |
| sector | VARCHAR(100) | 所属板块 |
| market | VARCHAR(50) | 市场 |
| status | TINYINT(1) | 状态 |
| remark | VARCHAR(500) | 备注 |
| create_time | DATETIME | 创建时间 |
| update_time | DATETIME | 更新时间 |

---

## 🚀 快速开始

### 方式1：自动化脚本（推荐）

```bash
# 自动保存特斯拉数据到MySQL
python3 auto_save_tesla_to_mysql.py
```

**功能**：
- ✅ 自动连接数据库
- ✅ 自动创建表（如果不存在）
- ✅ 获取特斯拉1年日线数据
- ✅ 批量保存到MySQL
- ✅ 查询验证
- ✅ 显示统计信息

### 方式2：交互式脚本

```bash
# 交互式保存（可选择是否创建表）
python3 save_to_mysql.py
```

### 方式3：批量导入

```bash
# 批量导入多只股票
python3 save_to_mysql.py batch
```

---

## 💻 代码示例

### 示例1：保存单只股票

```python
from us_stock_data_fetcher import USStockDataFetcher
from save_to_mysql import MySQLStockSaver

# 1. 创建MySQL保存器
saver = MySQLStockSaver(
    host='101.37.164.75',
    port=3307,
    user='root',
    password='Cd40k1SKIXBQ',
    database='ry-vue'
)

# 2. 连接数据库
saver.connect()

# 3. 获取数据
fetcher = USStockDataFetcher('TSLA')
df = fetcher.fetch_historical_data(period='1y', interval='1d')

# 4. 保存到MySQL
saver.save_historical_data(df, 'TSLA', interval_type='1d')

# 5. 关闭连接
saver.close()
```

### 示例2：保存实时信息

```python
# 获取实时信息
info = fetcher.fetch_realtime_info()

# 保存到MySQL
saver.save_realtime_info(info, 'TSLA')
```

### 示例3：查询数据

```python
# 查询最近30天的数据
df = saver.query_stock_data(
    symbol='TSLA',
    start_date='2024-10-01',
    end_date='2024-11-01',
    interval_type='1d',
    limit=30
)

print(df)
```

### 示例4：获取统计信息

```python
# 获取统计信息
stats = saver.get_statistics('TSLA', interval_type='1d')

print(f"总记录数: {stats['record_count']}")
print(f"最低价: ${stats['min_price']:.2f}")
print(f"最高价: ${stats['max_price']:.2f}")
```

---

## 📝 SQL查询示例

### 查询最近30天数据

```sql
SELECT 
    symbol,
    trade_date,
    open_price,
    high_price,
    low_price,
    close_price,
    volume
FROM us_stock_data
WHERE symbol = 'TSLA' 
  AND interval_type = '1d'
  AND trade_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY trade_date DESC;
```

### 查询价格统计

```sql
SELECT 
    symbol,
    COUNT(*) as record_count,
    MIN(low_price) as min_price,
    MAX(high_price) as max_price,
    AVG(close_price) as avg_price,
    SUM(volume) as total_volume
FROM us_stock_data
WHERE symbol = 'TSLA' 
  AND interval_type = '1d'
GROUP BY symbol;
```

### 查询多只股票最新价格

```sql
SELECT 
    d.symbol,
    l.company_name,
    d.close_price,
    d.volume,
    d.trade_date
FROM us_stock_data d
LEFT JOIN us_stock_list l ON d.symbol = l.symbol
WHERE d.interval_type = '1d'
  AND d.trade_date = (
    SELECT MAX(trade_date) 
    FROM us_stock_data 
    WHERE symbol = d.symbol AND interval_type = '1d'
  )
ORDER BY d.symbol;
```

### 查询涨跌幅排行

```sql
SELECT 
    symbol,
    close_price,
    (close_price - open_price) / open_price * 100 as change_percent,
    volume,
    trade_date
FROM us_stock_data
WHERE interval_type = '1d'
  AND trade_date = (SELECT MAX(trade_date) FROM us_stock_data WHERE interval_type = '1d')
ORDER BY change_percent DESC
LIMIT 10;
```

### 查询移动平均线

```sql
SELECT 
    trade_date,
    close_price,
    AVG(close_price) OVER (
        ORDER BY trade_date 
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) as ma20,
    AVG(close_price) OVER (
        ORDER BY trade_date 
        ROWS BETWEEN 59 PRECEDING AND CURRENT ROW
    ) as ma60
FROM us_stock_data
WHERE symbol = 'TSLA' 
  AND interval_type = '1d'
ORDER BY trade_date DESC
LIMIT 100;
```

### 查询成交量异常

```sql
SELECT 
    trade_date,
    close_price,
    volume,
    AVG(volume) OVER (
        ORDER BY trade_date 
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) as avg_volume,
    volume / AVG(volume) OVER (
        ORDER BY trade_date 
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) as volume_ratio
FROM us_stock_data
WHERE symbol = 'TSLA' 
  AND interval_type = '1d'
HAVING volume_ratio > 1.5
ORDER BY trade_date DESC;
```

---

## 🔧 维护操作

### 删除旧数据

```sql
-- 删除1年前的数据
DELETE FROM us_stock_data
WHERE trade_date < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

### 更新数据

```sql
-- 更新特定记录
UPDATE us_stock_data
SET close_price = 450.00
WHERE symbol = 'TSLA' 
  AND trade_date = '2024-11-10'
  AND interval_type = '1d';
```

### 清空表数据

```sql
-- 清空表（保留结构）
TRUNCATE TABLE us_stock_data;
```

### 删除表

```sql
-- 删除表
DROP TABLE IF EXISTS us_stock_data;
```

---

## 📊 当前数据状态

### 特斯拉数据

- ✅ 已保存250条日线数据
- 📅 日期范围：2024-11-11 至 2025-11-10
- 💰 价格范围：$214.25 - $488.54
- 📈 平均价格：$348.67
- 📊 总成交量：25,018,997,800股

### 数据表

| 表名 | 记录数 | 状态 |
|------|--------|------|
| us_stock_data | 250+ | ✅ 已创建 |
| us_stock_realtime | 0+ | ✅ 已创建 |
| us_stock_list | 8 | ✅ 已创建 |

---

## 🎯 最佳实践

### 1. 数据更新策略

```python
# 每日定时更新
import schedule
import time

def update_daily():
    """每日更新数据"""
    saver = MySQLStockSaver(...)
    saver.connect()
    
    fetcher = USStockDataFetcher('TSLA')
    df = fetcher.fetch_historical_data(period='5d', interval='1d')
    saver.save_historical_data(df, 'TSLA')
    
    saver.close()

# 每天美股收盘后执行（北京时间早上5点）
schedule.every().day.at("05:00").do(update_daily)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 2. 批量更新多只股票

```python
symbols = ['TSLA', 'AAPL', 'MSFT', 'GOOGL', 'NVDA']

saver = MySQLStockSaver(...)
saver.connect()

for symbol in symbols:
    try:
        fetcher = USStockDataFetcher(symbol, verbose=False)
        df = fetcher.fetch_historical_data(period='5d', interval='1d')
        saver.save_historical_data(df, symbol)
        print(f'✅ {symbol} 更新成功')
    except Exception as e:
        print(f'❌ {symbol} 更新失败: {e}')

saver.close()
```

### 3. 数据备份

```bash
# 导出数据
mysqldump -h 101.37.164.75 -P 3307 -u root -p ry-vue us_stock_data > backup.sql

# 导入数据
mysql -h 101.37.164.75 -P 3307 -u root -p ry-vue < backup.sql
```

---

## ⚠️ 注意事项

### 1. 数据去重

表中已设置唯一索引 `uk_symbol_date_interval`，自动防止重复数据。

### 2. 时区处理

- 数据库存储时已移除时区信息
- 查询时注意时区转换

### 3. 数据精度

- 价格字段使用 DECIMAL(12,4)，支持4位小数
- 成交量使用 BIGINT(20)，支持大数值

### 4. 性能优化

- 批量插入使用 `executemany()`
- 查询时使用索引字段
- 定期清理历史数据

---

## 📚 相关文件

- `create_stock_table.sql` - 数据表创建脚本
- `save_to_mysql.py` - MySQL保存器类
- `auto_save_tesla_to_mysql.py` - 自动化保存脚本
- `us_stock_data_fetcher.py` - 数据获取器

---

## 🆘 常见问题

### Q1: 连接数据库失败？

**A**: 检查：
- 网络连接
- 主机地址和端口
- 用户名和密码
- 数据库是否存在

### Q2: 插入数据失败？

**A**: 检查：
- 表是否已创建
- 数据格式是否正确
- 是否有重复数据（检查唯一索引）

### Q3: 如何更新已存在的数据？

**A**: 使用 `ON DUPLICATE KEY UPDATE`：
```sql
INSERT INTO us_stock_data (...) VALUES (...)
ON DUPLICATE KEY UPDATE
    close_price = VALUES(close_price),
    volume = VALUES(volume);
```

### Q4: 如何查询指定日期范围的数据？

**A**: 
```python
df = saver.query_stock_data(
    symbol='TSLA',
    start_date='2024-10-01',
    end_date='2024-11-01'
)
```

---

**最后更新**：2025年11月  
**版本**：v1.0  
**作者**：Ivan
