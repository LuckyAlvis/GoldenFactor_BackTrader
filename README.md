# 量化交易项目

基于Python的量化交易工具和策略集合。

## 项目结构

```
backtrader/
├── stock_data_tool/      # 股票数据获取工具
├── strategies/           # 量化策略代码
└── requirements.txt      # 项目依赖
```

## 模块说明

### 📊 stock_data_tool - 股票数据获取工具

通用的股票数据获取工具，支持任意市场股票代码。

**特性**：
- ✅ 支持美股、A股、港股等
- ✅ 多种时间周期和K线类型
- ✅ 导出CSV、JSON、SQLite格式
- ✅ 简洁的配置文件

**快速开始**：
```bash
cd stock_data_tool
python3 main.py
```

详见：[stock_data_tool/README.md](stock_data_tool/README.md)

---

### 📈 strategies - 量化策略

包含各种量化交易策略的回测代码。

**策略列表**：
- 双均线策略
- 月级波段策略
- 特斯拉专用策略

**使用方法**：
```python
import backtrader as bt
from strategies.dual_ma_strategy import DualMovingAverageStrategy

cerebro = bt.Cerebro()
cerebro.addstrategy(DualMovingAverageStrategy)
cerebro.run()
```

详见：[strategies/README.md](strategies/README.md)

---

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 获取股票数据

```bash
cd stock_data_tool
# 修改 config.py 配置
python3 main.py
```

### 2. 运行策略回测

```bash
cd strategies
python3 dual_ma_strategy.py
```

## 依赖

- Python 3.8+
- yfinance - 股票数据获取
- pandas - 数据处理
- backtrader - 策略回测
- matplotlib - 数据可视化

## 文档

- [股票数据工具文档](stock_data_tool/README.md)
- [策略说明文档](strategies/README.md)
- [历史文档](stock_data_tool/docs/)

## 许可

MIT License
