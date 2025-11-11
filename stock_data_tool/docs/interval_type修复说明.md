# interval_type 硬编码问题修复说明

## 问题描述

用户修改了获取数据的K线类型为 `1h`：
```python
df = fetcher.fetch_historical_data(period='1y', interval='1h')
```

但保存到MySQL数据库时，`interval_type` 字段仍然是 `'1d'`。

## 问题原因

在 `auto_save_tesla_to_mysql.py` 第115行，`interval_type` 被硬编码为 `'1d'`：

```python
data_list.append((
    'TSLA',
    trade_date,
    float(row['Open']),
    float(row['High']),
    float(row['Low']),
    float(row['Close']),
    int(row['Volume']),
    float(row.get('Dividends', 0)),
    float(row.get('Stock Splits', 0)),
    '1d'  # ❌ 硬编码
))
```

## 解决方案

### 1. 添加配置参数

在文件开头添加可配置的参数：

```python
# 配置参数
symbol = 'TSLA'
period = '1y'
interval = '1h'  # 可修改：1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
```

### 2. 使用变量替代硬编码

```python
data_list.append((
    symbol,           # 使用变量
    trade_date,
    float(row['Open']),
    float(row['High']),
    float(row['Low']),
    float(row['Close']),
    int(row['Volume']),
    float(row.get('Dividends', 0)),
    float(row.get('Stock Splits', 0)),
    interval  # ✅ 使用变量
))
```

### 3. 更新查询SQL

修改前：
```python
WHERE symbol = 'TSLA' AND interval_type = '1d'  # ❌ 硬编码
```

修改后：
```python
WHERE symbol = %s AND interval_type = %s  # ✅ 参数化
cursor.execute(query_sql, (symbol, interval))
```

## 修改内容

### 文件：auto_save_tesla_to_mysql.py

#### 1. 添加配置参数（第71-74行）

```python
# 配置参数
symbol = 'TSLA'
period = '1y'
interval = '1h'  # 可修改：1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
```

#### 2. 修改数据插入（第115-124行）

```python
data_list.append((
    symbol,           # 改为变量
    trade_date,
    float(row['Open']),
    float(row['High']),
    float(row['Low']),
    float(row['Close']),
    int(row['Volume']),
    float(row.get('Dividends', 0)),
    float(row.get('Stock Splits', 0)),
    interval  # 改为变量
))
```

#### 3. 修改查询SQL（第153行）

```python
WHERE symbol = %s AND interval_type = %s
cursor.execute(query_sql, (symbol, interval))
```

#### 4. 修改统计SQL（第178行）

```python
WHERE symbol = %s AND interval_type = %s
cursor.execute(stats_sql, (symbol, interval))
```

## 测试结果

### 运行脚本

```bash
python3 auto_save_tesla_to_mysql.py
```

### 输出

```
步骤3：获取特斯拉数据...
[OK] 成功获取 1738 条数据
    股票代码: TSLA
    时间周期: 1y
    K线类型: 1h

步骤4：保存数据到MySQL...
[OK] 成功保存 1738 条记录到MySQL

步骤5：查询验证...

最近5条记录 (K线类型: 1h):
日期                   开盘         最高         最低         收盘         成交量      
2025-11-10 15:30:00  $444.58    $446.05    $443.55    $445.26    4,032,161
2025-11-10 14:30:00  $446.51    $447.15    $443.77    $444.61    4,826,090
2025-11-10 13:30:00  $444.58    $447.70    $442.08    $446.47    6,468,919
2025-11-10 12:30:00  $446.23    $448.70    $444.45    $444.60    4,827,067
2025-11-10 11:30:00  $446.85    $449.43    $444.32    $446.21    7,231,818

数据库统计信息 (TSLA - 1h):
  总记录数: 1738
  最低价: $214.25
  最高价: $488.54
  平均价: $348.42
  总成交量: 22,946,781,923
  日期范围: 2024-11-11 09:30:00 至 2025-11-10 15:30:00
```

### 数据库验证

```sql
SELECT interval_type, COUNT(*) as count
FROM us_stock_data
WHERE symbol = 'TSLA'
GROUP BY interval_type;
```

**结果**：
```
K线类型    记录数
1d        1738
1h        1738
```

✅ 数据已正确保存为 `1h` 类型！

## 使用方法

### 修改K线类型

只需修改第74行的 `interval` 变量：

```python
# 1分钟K线
interval = '1m'

# 5分钟K线
interval = '5m'

# 15分钟K线
interval = '15m'

# 30分钟K线
interval = '30m'

# 1小时K线
interval = '1h'

# 日K线
interval = '1d'

# 周K线
interval = '1wk'

# 月K线
interval = '1mo'
```

### 修改股票代码

```python
symbol = 'AAPL'  # 苹果
symbol = 'MSFT'  # 微软
symbol = 'GOOGL' # 谷歌
```

### 修改时间周期

```python
period = '1d'   # 1天
period = '5d'   # 5天
period = '1mo'  # 1个月
period = '3mo'  # 3个月
period = '6mo'  # 6个月
period = '1y'   # 1年
period = '2y'   # 2年
period = '5y'   # 5年
period = 'max'  # 所有历史数据
```

## 注意事项

### 1. 分钟数据限制

yfinance对分钟级别数据有限制：
- `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`: 最多7天数据
- 如果设置 `period='1y'` 和 `interval='1m'`，实际只能获取最近7天

### 2. 数据去重

数据库中设置了唯一索引：
```sql
UNIQUE KEY `uk_symbol_date_interval` (`symbol`, `trade_date`, `interval_type`)
```

相同的 `(symbol, trade_date, interval_type)` 组合会自动更新而不是重复插入。

### 3. 查询不同K线类型

```sql
-- 查询日K线
SELECT * FROM us_stock_data 
WHERE symbol = 'TSLA' AND interval_type = '1d'
ORDER BY trade_date DESC;

-- 查询小时K线
SELECT * FROM us_stock_data 
WHERE symbol = 'TSLA' AND interval_type = '1h'
ORDER BY trade_date DESC;

-- 查询所有K线类型的统计
SELECT 
    interval_type,
    COUNT(*) as count,
    MIN(trade_date) as start_date,
    MAX(trade_date) as end_date
FROM us_stock_data
WHERE symbol = 'TSLA'
GROUP BY interval_type;
```

## 改进建议

### 1. 添加命令行参数

可以进一步改进，支持命令行参数：

```python
import sys

if len(sys.argv) >= 4:
    symbol = sys.argv[1]
    period = sys.argv[2]
    interval = sys.argv[3]
else:
    symbol = 'TSLA'
    period = '1y'
    interval = '1h'
```

使用：
```bash
python3 auto_save_tesla_to_mysql.py AAPL 6mo 1d
```

### 2. 添加配置文件

创建 `config.ini`：
```ini
[stock]
symbol = TSLA
period = 1y
interval = 1h

[database]
host = 101.37.164.75
port = 3307
user = root
password = Cd40k1SKIXBQ
database = ry-vue
```

### 3. 批量保存多只股票

```python
symbols = ['TSLA', 'AAPL', 'MSFT', 'GOOGL', 'NVDA']
for symbol in symbols:
    # 保存每只股票的数据
```

## 总结

✅ **问题已解决**：
- interval_type 不再硬编码
- 使用变量动态设置
- 查询SQL也已参数化

✅ **改进点**：
- 添加了配置参数区域
- 代码更灵活易维护
- 输出信息更详细

✅ **测试通过**：
- 1小时K线数据正确保存
- 查询验证正确
- 数据库统计正确

---

**修复时间**：2025年11月11日  
**状态**：✅ 已修复并测试通过
