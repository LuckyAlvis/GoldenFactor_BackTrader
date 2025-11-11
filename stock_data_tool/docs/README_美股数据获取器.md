# 美股数据获取器 v2.0 - 完全重构版

## 🎯 核心改进

### 旧版本 vs 新版本

| 特性 | fetch_tesla_data.py（旧） | us_stock_data_fetcher.py（新）✅ |
|------|---------------------------|--------------------------------|
| **股票代码** | 硬编码TSLA | 支持任意股票（参数传递） |
| **时间周期** | 固定或手动输入 | 11种周期枚举 + 自定义日期 |
| **K线类型** | 固定或手动输入 | 13种类型枚举 |
| **输出格式** | 仅CSV | CSV/SQLite/JSON/DataFrame |
| **批量获取** | 不支持 | 支持批量获取多只股票 |
| **文件命名** | 固定名称 | 自动生成时间戳 |
| **代码结构** | 函数式 | 面向对象（OOP） |
| **类型安全** | 字符串 | 枚举类型 |
| **错误处理** | 基础 | 完善的异常处理 |
| **API设计** | 分散的函数 | 统一的类接口 |

---

## 📦 文件说明

### 核心文件

1. **us_stock_data_fetcher.py** ⭐⭐⭐
   - 主程序文件
   - 包含`USStockDataFetcher`和`BatchFetcher`类
   - 支持命令行和API两种使用方式

2. **us_stock_examples.py**
   - 10个完整的使用示例
   - 涵盖所有功能场景
   - 可直接运行学习

3. **美股数据获取器使用手册.md**
   - 详细的API文档
   - 参数说明
   - 最佳实践
   - 常见问题解答

### 旧文件（已废弃）

- ~~fetch_tesla_data.py~~ → 使用 `us_stock_data_fetcher.py`
- ~~fetch_tesla_simple.py~~ → 使用 `us_stock_data_fetcher.py`
- ~~特斯拉数据获取说明.md~~ → 使用 `美股数据获取器使用手册.md`

---

## 🚀 快速开始

### 方式1：命令行交互（最简单）

```bash
python3 us_stock_data_fetcher.py
```

按提示输入参数即可。

### 方式2：Python API（最灵活）

```python
from us_stock_data_fetcher import USStockDataFetcher

# 1. 创建获取器
fetcher = USStockDataFetcher('TSLA')

# 2. 获取数据
df = fetcher.fetch_historical_data(period='1y', interval='1d')

# 3. 保存数据
fetcher.save_to_csv()

# 4. 查看摘要
fetcher.print_summary()
```

### 方式3：批量获取

```python
from us_stock_data_fetcher import BatchFetcher

# 批量获取多只股票
batch = BatchFetcher(['TSLA', 'AAPL', 'MSFT', 'GOOGL'])
results = batch.fetch_all(period='1y', interval='1d')
```

---

## 💡 核心特性展示

### 1. 支持任意股票

```python
# 美股
USStockDataFetcher('TSLA')   # 特斯拉
USStockDataFetcher('AAPL')   # 苹果
USStockDataFetcher('MSFT')   # 微软

# 港股
USStockDataFetcher('0700.HK')  # 腾讯

# A股
USStockDataFetcher('600519.SS')  # 贵州茅台
```

### 2. 灵活的时间配置

```python
# 使用预定义周期
period='1d'    # 1天
period='1mo'   # 1个月
period='1y'    # 1年
period='max'   # 所有历史

# 或使用枚举（推荐）
from us_stock_data_fetcher import Period
period=Period.ONE_YEAR
period=Period.FIVE_YEARS
period=Period.MAX

# 或自定义日期范围
start_date='2024-01-01'
end_date='2024-12-31'
```

### 3. 多种K线类型

```python
# 分钟级
interval='1m'   # 1分钟
interval='5m'   # 5分钟
interval='15m'  # 15分钟

# 小时级
interval='1h'   # 1小时

# 日级以上
interval='1d'   # 1天
interval='1wk'  # 1周
interval='1mo'  # 1月
```

### 4. 多种输出格式

```python
# CSV文件
fetcher.save_to_csv('output.csv')

# SQLite数据库
fetcher.save_to_sqlite('stocks.db', table_name='tsla')

# JSON文件
fetcher.save_to_json('output.json')

# DataFrame对象（用于分析）
df = fetcher.data
```

### 5. 类型安全（枚举）

```python
from us_stock_data_fetcher import Period, Interval, OutputFormat

# 使用枚举避免拼写错误，有IDE提示
fetcher.fetch_historical_data(
    period=Period.ONE_YEAR,
    interval=Interval.ONE_DAY
)

fetcher.save(OutputFormat.CSV)
```

---

## 📊 使用示例

### 示例1：获取特斯拉数据

```python
from us_stock_data_fetcher import USStockDataFetcher

fetcher = USStockDataFetcher('TSLA')
df = fetcher.fetch_historical_data(period='1y', interval='1d')
fetcher.save_to_csv('tsla_1y.csv')
fetcher.print_summary()
```

**输出**：
```
初始化美股数据获取器: TSLA
✅ 成功获取 250 条数据
📅 日期范围: 2024-11-11 至 2025-11-10
✅ 数据已保存到CSV: tsla_1y.csv

数据摘要 - TSLA
总记录数: 250
最高价: $488.54
最低价: $214.25
平均收盘价: $348.67
```

### 示例2：批量获取科技股

```python
from us_stock_data_fetcher import BatchFetcher

tech_stocks = ['TSLA', 'AAPL', 'MSFT', 'GOOGL', 'NVDA']
batch = BatchFetcher(tech_stocks)

results = batch.fetch_all(
    period='3mo',
    interval='1d',
    output_format='csv',
    output_dir='tech_stocks'
)

print(f"成功获取 {len(results)} 只股票")
```

### 示例3：保存到数据库

```python
fetcher = USStockDataFetcher('AAPL')
df = fetcher.fetch_historical_data(period='1y', interval='1d')

# 保存到SQLite数据库
fetcher.save_to_sqlite(
    db_path='my_stocks.db',
    table_name='aapl_daily',
    if_exists='replace'
)
```

### 示例4：数据分析

```python
fetcher = USStockDataFetcher('TSLA', verbose=False)
df = fetcher.fetch_historical_data(period='1y', interval='1d')

# 计算技术指标
df['Returns'] = df['Close'].pct_change()
df['MA20'] = df['Close'].rolling(20).mean()
df['MA60'] = df['Close'].rolling(60).mean()

# 统计分析
print(f"平均价格: ${df['Close'].mean():.2f}")
print(f"波动率: {df['Returns'].std() * 100:.2f}%")

# 保存分析结果
df.to_csv('tsla_analysis.csv', index=False)
```

---

## 🎓 代码对比

### 旧版本代码

```python
# fetch_tesla_data.py（旧版）

import yfinance as yf
import pandas as pd

def fetch_tesla_historical_data(period='1y', interval='1d', save_path='tsla_historical.csv'):
    print(f'正在获取特斯拉历史数据...')
    tsla = yf.Ticker("TSLA")
    df = tsla.history(period=period, interval=interval)
    df.reset_index(inplace=True)
    df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f'✅ 成功获取 {len(df)} 条数据')
    return df

# 使用
df = fetch_tesla_historical_data(period='1y', interval='1d')
```

**问题**：
- ❌ 只能获取特斯拉
- ❌ 参数硬编码
- ❌ 只能保存CSV
- ❌ 没有数据验证
- ❌ 没有错误处理
- ❌ 文件名固定

### 新版本代码

```python
# us_stock_data_fetcher.py（新版）

from us_stock_data_fetcher import USStockDataFetcher, Period, Interval

# 创建获取器（支持任意股票）
fetcher = USStockDataFetcher('TSLA')

# 获取数据（类型安全）
df = fetcher.fetch_historical_data(
    period=Period.ONE_YEAR,
    interval=Interval.ONE_DAY
)

# 保存数据（多种格式）
fetcher.save_to_csv()  # 自动生成文件名
fetcher.save_to_sqlite('stocks.db')
fetcher.save_to_json()

# 数据摘要
fetcher.print_summary()
```

**优势**：
- ✅ 支持任意股票
- ✅ 参数化设计
- ✅ 多种输出格式
- ✅ 完整的数据验证
- ✅ 完善的错误处理
- ✅ 自动生成文件名
- ✅ 面向对象设计
- ✅ 类型安全（枚举）

---

## 📚 完整功能列表

### USStockDataFetcher 类

| 方法 | 功能 |
|------|------|
| `__init__(symbol, verbose)` | 初始化获取器 |
| `fetch_historical_data()` | 获取历史数据 |
| `fetch_realtime_info()` | 获取实时信息 |
| `save_to_csv()` | 保存为CSV |
| `save_to_sqlite()` | 保存到数据库 |
| `save_to_json()` | 保存为JSON |
| `save()` | 统一保存接口 |
| `get_data_summary()` | 获取数据摘要 |
| `print_summary()` | 打印数据摘要 |

### BatchFetcher 类

| 方法 | 功能 |
|------|------|
| `__init__(symbols, verbose)` | 初始化批量获取器 |
| `fetch_all()` | 批量获取所有股票 |

### 枚举类型

| 枚举 | 用途 |
|------|------|
| `Period` | 时间周期（11种） |
| `Interval` | K线类型（13种） |
| `OutputFormat` | 输出格式（4种） |

---

## 🔧 高级用法

### 1. 自定义日期范围

```python
fetcher = USStockDataFetcher('AAPL')

# 获取2024年全年数据
df = fetcher.fetch_historical_data(
    start_date='2024-01-01',
    end_date='2024-12-31',
    interval='1d'
)
```

### 2. 连续获取多个时间段

```python
from datetime import datetime, timedelta
import pandas as pd

all_data = []
end_date = datetime.now()

for i in range(12):  # 获取12个月
    start_date = end_date - timedelta(days=30)
    
    fetcher = USStockDataFetcher('TSLA', verbose=False)
    df = fetcher.fetch_historical_data(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        interval='1d'
    )
    
    if df is not None:
        all_data.append(df)
    
    end_date = start_date

# 合并数据
combined = pd.concat(all_data, ignore_index=True)
```

### 3. 数据库管理

```python
import sqlite3

# 创建数据库并保存多只股票
symbols = ['TSLA', 'AAPL', 'MSFT', 'GOOGL']

for symbol in symbols:
    fetcher = USStockDataFetcher(symbol, verbose=False)
    df = fetcher.fetch_historical_data(period='1y', interval='1d')
    
    fetcher.save_to_sqlite(
        db_path='portfolio.db',
        table_name=f'stock_{symbol.lower()}',
        if_exists='replace'
    )

# 查询数据库
conn = sqlite3.connect('portfolio.db')

# 查看所有表
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())

# 查询数据
df = pd.read_sql_query("SELECT * FROM stock_tsla WHERE Close > 400", conn)
conn.close()
```

---

## ⚠️ 注意事项

### 1. 数据限制

| K线类型 | 最大时间范围 |
|---------|-------------|
| 1分钟 | 7天 |
| 2-90分钟 | 60天 |
| 1小时 | 730天 |
| 1天及以上 | 无限制 |

### 2. 数据延迟

免费API数据有15-20分钟延迟。

### 3. 请求频率

建议不要过于频繁请求，避免被限制。

---

## 📖 更多资源

- **详细文档**：`美股数据获取器使用手册.md`
- **使用示例**：`us_stock_examples.py`
- **API文档**：见使用手册

---

## 🎉 总结

新版本 `us_stock_data_fetcher.py` 是对旧版本的完全重构，提供了：

1. ✅ **更强大的功能**：支持任意股票、多种格式、批量获取
2. ✅ **更好的设计**：面向对象、类型安全、统一接口
3. ✅ **更易使用**：命令行+API、详细文档、丰富示例
4. ✅ **更高质量**：完善的错误处理、数据验证、日志输出

**建议**：
- 新项目使用 `us_stock_data_fetcher.py`
- 旧项目逐步迁移到新版本
- 旧文件可以保留作为参考

---

**版本**：v2.0  
**更新时间**：2025年11月  
**作者**：Ivan

**免责声明**：本工具仅供学习研究使用，不构成投资建议。
