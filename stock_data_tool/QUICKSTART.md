# 快速开始指南

## 3步获取股票数据

### 第1步：修改配置

打开 `config.py`，修改以下参数：

```python
SYMBOL = 'TSLA'      # 改成你要的股票代码
PERIOD = '1y'        # 改成你要的时间周期
INTERVAL = '1d'      # 改成你要的K线类型
```

### 第2步：运行程序

```bash
python3 main.py
```

### 第3步：查看结果

数据保存在 `output/` 目录下。

---

## 常用配置示例

### 获取美股数据

```python
SYMBOL = 'AAPL'      # 苹果
SYMBOL = 'TSLA'      # 特斯拉
SYMBOL = 'MSFT'      # 微软
SYMBOL = 'GOOGL'     # 谷歌
```

### 获取A股数据

```python
SYMBOL = '000001.SZ'  # 平安银行
SYMBOL = '600000.SS'  # 浦发银行
SYMBOL = '000858.SZ'  # 五粮液
```

### 时间周期

```python
PERIOD = '1mo'   # 1个月
PERIOD = '3mo'   # 3个月
PERIOD = '6mo'   # 6个月
PERIOD = '1y'    # 1年
PERIOD = '5y'    # 5年
```

### K线类型

```python
INTERVAL = '1h'   # 小时线
INTERVAL = '1d'   # 日线
INTERVAL = '1wk'  # 周线
INTERVAL = '1mo'  # 月线
```

### 导出格式

```python
EXPORT_CSV = True       # 导出CSV
EXPORT_JSON = True      # 导出JSON
EXPORT_SQLITE = True    # 导出数据库
```

---

## 完整示例

### 示例1：获取特斯拉1年日线

```python
# config.py
SYMBOL = 'TSLA'
PERIOD = '1y'
INTERVAL = '1d'
EXPORT_CSV = True
```

运行：
```bash
python3 main.py
```

结果：
```
output/TSLA_1d.csv
```

### 示例2：获取苹果6个月小时线

```python
# config.py
SYMBOL = 'AAPL'
PERIOD = '6mo'
INTERVAL = '1h'
EXPORT_JSON = True
```

运行：
```bash
python3 main.py
```

结果：
```
output/AAPL_1h.json
```

### 示例3：获取A股指定日期数据

```python
# config.py
SYMBOL = '000001.SZ'
START_DATE = '2024-01-01'
END_DATE = '2024-12-31'
INTERVAL = '1d'
EXPORT_SQLITE = True
```

运行：
```bash
python3 main.py
```

结果：
```
output/stock_data.db
```

---

就这么简单！
