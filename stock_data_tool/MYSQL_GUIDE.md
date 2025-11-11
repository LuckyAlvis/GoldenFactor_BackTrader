# MySQL数据库使用指南

## 快速配置

### 1. 修改config.py

```python
# 启用MySQL导出
EXPORT_MYSQL = True

# MySQL配置
MYSQL_HOST = '101.37.164.75'    # 你的MySQL主机
MYSQL_PORT = 3307                # 你的MySQL端口
MYSQL_USER = 'root'              # 你的MySQL用户名
MYSQL_PASSWORD = 'your_password' # 你的MySQL密码
MYSQL_DATABASE = 'ry-vue'        # 你的数据库名
MYSQL_TABLE = 'stock_data'       # 表名
```

### 2. 运行程序

```bash
python3 main.py
```

程序会自动：
1. 连接MySQL数据库
2. 创建表（如果不存在）
3. 插入数据（重复数据会自动更新）

---

## 表结构

程序会自动创建以下表结构：

```sql
CREATE TABLE IF NOT EXISTS stock_data (
  `id` BIGINT AUTO_INCREMENT,
  `symbol` VARCHAR(20) NOT NULL COMMENT '股票代码',
  `trade_date` DATETIME NOT NULL COMMENT '交易日期',
  `open_price` DECIMAL(20,4) COMMENT '开盘价',
  `high_price` DECIMAL(20,4) COMMENT '最高价',
  `low_price` DECIMAL(20,4) COMMENT '最低价',
  `close_price` DECIMAL(20,4) COMMENT '收盘价',
  `volume` BIGINT COMMENT '成交量',
  `dividends` DECIMAL(20,4) DEFAULT 0 COMMENT '分红',
  `stock_splits` DECIMAL(20,4) DEFAULT 0 COMMENT '拆股',
  `interval_type` VARCHAR(10) DEFAULT '1d' COMMENT 'K线类型',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_symbol_date_interval` (`symbol`, `trade_date`, `interval_type`),
  KEY `idx_symbol` (`symbol`),
  KEY `idx_trade_date` (`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票历史数据表'
```

**特点**：
- ✅ 自动创建表
- ✅ 唯一索引防止重复数据
- ✅ 重复数据自动更新
- ✅ 支持多只股票
- ✅ 支持多种K线类型

---

## 查询示例

### 查询某只股票的所有数据

```sql
SELECT * FROM stock_data 
WHERE symbol = '000001.SZ' 
ORDER BY trade_date DESC;
```

### 查询最新N条记录

```sql
SELECT 
    trade_date,
    open_price,
    high_price,
    low_price,
    close_price,
    volume
FROM stock_data 
WHERE symbol = '000001.SZ' 
ORDER BY trade_date DESC 
LIMIT 10;
```

### 统计数据量

```sql
SELECT 
    symbol,
    COUNT(*) as count,
    MIN(trade_date) as start_date,
    MAX(trade_date) as end_date
FROM stock_data 
GROUP BY symbol;
```

### 查询价格范围

```sql
SELECT 
    symbol,
    MIN(low_price) as min_price,
    MAX(high_price) as max_price,
    AVG(close_price) as avg_price
FROM stock_data 
WHERE symbol = '000001.SZ';
```

### 查询指定日期范围

```sql
SELECT * FROM stock_data 
WHERE symbol = '000001.SZ' 
  AND trade_date BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY trade_date;
```

### 查询不同K线类型

```sql
-- 查询日线数据
SELECT * FROM stock_data 
WHERE symbol = '000001.SZ' AND interval_type = '1d';

-- 查询小时线数据
SELECT * FROM stock_data 
WHERE symbol = '000001.SZ' AND interval_type = '1h';
```

---

## 使用场景

### 场景1：每日更新股票数据

```python
# config.py
SYMBOL = '000001.SZ'
PERIOD = '1d'  # 只获取最新1天
INTERVAL = '1d'
EXPORT_MYSQL = True
```

运行后会自动更新最新数据。

### 场景2：批量导入多只股票

修改config.py中的SYMBOL，多次运行：

```bash
# 第一次
SYMBOL = '000001.SZ'
python3 main.py

# 第二次
SYMBOL = '600000.SS'
python3 main.py

# 第三次
SYMBOL = 'AAPL'
python3 main.py
```

### 场景3：获取不同K线类型

```python
# 获取日线
INTERVAL = '1d'
python3 main.py

# 获取小时线
INTERVAL = '1h'
python3 main.py
```

所有数据会保存在同一张表中，通过`interval_type`字段区分。

---

## Python查询示例

```python
import pymysql

# 连接数据库
conn = pymysql.connect(
    host='101.37.164.75',
    port=3307,
    user='root',
    password='your_password',
    database='ry-vue'
)

cursor = conn.cursor()

# 查询数据
sql = "SELECT * FROM stock_data WHERE symbol = %s ORDER BY trade_date DESC LIMIT 10"
cursor.execute(sql, ('000001.SZ',))
results = cursor.fetchall()

for row in results:
    print(row)

conn.close()
```

---

## 常见问题

### Q: 如何避免重复数据？

A: 表中有唯一索引 `(symbol, trade_date, interval_type)`，相同的数据会自动更新而不是重复插入。

### Q: 可以保存多只股票吗？

A: 可以，所有股票数据保存在同一张表中，通过`symbol`字段区分。

### Q: 如何删除某只股票的数据？

A: 
```sql
DELETE FROM stock_data WHERE symbol = '000001.SZ';
```

### Q: 如何清空整张表？

A: 
```sql
TRUNCATE TABLE stock_data;
```

### Q: 数据库连接失败怎么办？

A: 检查：
1. MySQL服务是否启动
2. 主机地址和端口是否正确
3. 用户名和密码是否正确
4. 数据库是否存在
5. 防火墙是否允许连接

---

## 性能优化

### 批量插入

程序已经使用批量插入（`executemany`），性能较好。

### 索引优化

表中已经创建了必要的索引：
- 主键索引：`id`
- 唯一索引：`(symbol, trade_date, interval_type)`
- 普通索引：`symbol`, `trade_date`

### 分区表（可选）

如果数据量非常大，可以考虑按日期分区：

```sql
ALTER TABLE stock_data 
PARTITION BY RANGE (YEAR(trade_date)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026)
);
```

---

## 安全建议

1. **不要在代码中硬编码密码**
   - 使用环境变量
   - 使用配置文件（不要提交到git）

2. **使用只读用户查询数据**
   ```sql
   CREATE USER 'readonly'@'%' IDENTIFIED BY 'password';
   GRANT SELECT ON ry-vue.stock_data TO 'readonly'@'%';
   ```

3. **定期备份数据**
   ```bash
   mysqldump -h 101.37.164.75 -P 3307 -u root -p ry-vue stock_data > backup.sql
   ```

---

## 总结

✅ **配置简单**：只需修改config.py  
✅ **自动建表**：无需手动创建表  
✅ **防止重复**：自动去重和更新  
✅ **支持多股票**：一张表存储所有数据  
✅ **查询方便**：标准SQL查询
