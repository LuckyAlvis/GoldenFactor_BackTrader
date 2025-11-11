# 股票数据获取工具

简洁通用的股票数据获取工具，支持任意市场股票代码。

## 特性

- ✅ 支持任意股票代码（美股、A股、港股等）
- ✅ 灵活的时间配置（预设周期或自定义日期范围）
- ✅ 多种K线类型（1分钟到月线）
- ✅ 多种导出格式（CSV、JSON、SQLite）
- ✅ 简洁的配置文件
- ✅ 最小化输出

## 快速开始

### 1. 安装依赖

```bash
pip install yfinance pandas
```

### 2. 配置参数

编辑 `config.py` 文件：

```python
# 股票代码
SYMBOL = 'TSLA'

# 时间周期
PERIOD = '1y'

# K线类型
INTERVAL = '1d'

# 导出格式
EXPORT_CSV = True
EXPORT_JSON = True
EXPORT_SQLITE = False  # SQLite数据库
EXPORT_MYSQL = True    # MySQL数据库

# MySQL配置（如果使用MySQL）
MYSQL_HOST = '101.37.164.75'
MYSQL_PORT = 3307
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'your_password'
MYSQL_DATABASE = 'ry-vue'
MYSQL_TABLE = 'stock_data'
```

### 3. 运行

```bash
python3 main.py
```

## 配置说明

### 股票代码

支持任意市场的股票代码：

```python
# 美股
SYMBOL = 'AAPL'    # 苹果
SYMBOL = 'TSLA'    # 特斯拉
SYMBOL = 'MSFT'    # 微软

# A股（需要加后缀）
SYMBOL = '000001.SZ'  # 平安银行（深圳）
SYMBOL = '600000.SS'  # 浦发银行（上海）

# 港股
SYMBOL = '0700.HK'    # 腾讯
```

### 时间配置

#### 方式1：预设周期

```python
PERIOD = '1d'    # 1天
PERIOD = '5d'    # 5天
PERIOD = '1mo'   # 1个月
PERIOD = '3mo'   # 3个月
PERIOD = '6mo'   # 6个月
PERIOD = '1y'    # 1年
PERIOD = '2y'    # 2年
PERIOD = '5y'    # 5年
PERIOD = 'max'   # 所有历史数据
```

#### 方式2：自定义日期范围

```python
START_DATE = '2024-01-01'
END_DATE = '2024-12-31'
```

### K线类型

```python
INTERVAL = '1m'    # 1分钟
INTERVAL = '5m'    # 5分钟
INTERVAL = '15m'   # 15分钟
INTERVAL = '30m'   # 30分钟
INTERVAL = '1h'    # 1小时
INTERVAL = '1d'    # 日线
INTERVAL = '1wk'   # 周线
INTERVAL = '1mo'   # 月线
```

**注意**：分钟级数据仅支持最近7天。

### 导出格式

```python
EXPORT_CSV = True       # 导出CSV文件
EXPORT_JSON = True      # 导出JSON文件
EXPORT_SQLITE = False   # 导出到SQLite数据库
EXPORT_MYSQL = True     # 导出到MySQL数据库
```

### MySQL配置

如果使用MySQL导出，需要配置以下参数：

```python
MYSQL_HOST = '101.37.164.75'    # MySQL主机地址
MYSQL_PORT = 3307                # MySQL端口
MYSQL_USER = 'root'              # MySQL用户名
MYSQL_PASSWORD = 'your_password' # MySQL密码
MYSQL_DATABASE = 'ry-vue'        # MySQL数据库名
MYSQL_TABLE = 'stock_data'       # MySQL表名
```

**表结构**：程序会自动创建表，包含以下字段：
- `symbol` - 股票代码
- `trade_date` - 交易日期
- `open_price` - 开盘价
- `high_price` - 最高价
- `low_price` - 最低价
- `close_price` - 收盘价
- `volume` - 成交量
- `dividends` - 分红
- `stock_splits` - 拆股
- `interval_type` - K线类型

## 输出示例

```
============================================================
股票数据获取工具
============================================================

股票代码: TSLA
时间周期: 1y
K线类型: 1d
导出格式: CSV, JSON, SQLite

------------------------------------------------------------

正在获取数据...
[OK] TSLA 获取 250 条数据
     时间范围: 2024-11-11 至 2025-11-10

正在导出数据...
[OK] 已保存到: output/TSLA_1d.csv
[OK] 已保存到: output/TSLA_1d.json
[OK] 已保存到数据库: output/stock_data.db (表: stock_tsla)

============================================================
[OK] 完成！成功导出 3 个文件
============================================================
```

## 项目结构

```
stock_data_tool/
├── main.py              # 主程序入口
├── stock_fetcher.py     # 数据获取器
├── config.py            # 配置文件
├── output/              # 输出目录（自动创建）
├── docs/                # 文档目录
└── README.md            # 说明文档
```

## 使用示例

### 示例1：获取特斯拉1年日线数据

```python
# config.py
SYMBOL = 'TSLA'
PERIOD = '1y'
INTERVAL = '1d'
EXPORT_CSV = True
```

### 示例2：获取苹果6个月小时线数据

```python
# config.py
SYMBOL = 'AAPL'
PERIOD = '6mo'
INTERVAL = '1h'
EXPORT_JSON = True
```

### 示例3：获取A股指定日期范围数据

```python
# config.py
SYMBOL = '000001.SZ'
START_DATE = '2024-01-01'
END_DATE = '2024-12-31'
INTERVAL = '1d'
EXPORT_SQLITE = True
```

## 常见问题

### Q: 如何获取A股数据？

A: A股代码需要加后缀：
- 深圳股票：`000001.SZ`
- 上海股票：`600000.SS`

### Q: 分钟数据为什么只有7天？

A: yfinance的限制，分钟级数据仅支持最近7天。

### Q: 如何查看SQLite数据？

A: 使用SQLite客户端或命令行：

```bash
sqlite3 output/stock_data.db
sqlite> SELECT * FROM stock_tsla LIMIT 5;
```

## 依赖

- Python 3.8+
- yfinance
- pandas

## 许可

MIT License
