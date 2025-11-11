# 策略回测代码

本目录包含各种量化交易策略的回测代码。

## 策略列表

### 1. dual_ma_strategy.py
**双均线策略（通用版）**

- 策略类型：趋势跟踪
- 适用市场：股票、期货
- 信号：
  - 买入：短期均线上穿长期均线
  - 卖出：短期均线下穿长期均线

### 2. tesla_dual_ma_strategy.py
**特斯拉双均线策略**

- 专门针对特斯拉股票优化的双均线策略
- 包含详细的回测报告和参数优化

### 3. monthly_swing_strategy.py
**月级波段策略**

- 策略类型：波段交易
- 时间周期：月线
- 适用：长期投资

### 4. monthly_swing_optimized.py
**月级波段策略（优化版）**

- 在原策略基础上优化参数
- 提高收益风险比

### 5. csv_data_loader.py
**CSV数据加载器**

- 用于加载本地CSV数据进行回测
- 支持数据标准化和清洗

## 使用方法

### 基本使用

```python
import backtrader as bt
from dual_ma_strategy import DualMovingAverageStrategy

# 创建Cerebro引擎
cerebro = bt.Cerebro()

# 添加策略
cerebro.addstrategy(DualMovingAverageStrategy)

# 添加数据
data = bt.feeds.YahooFinanceData(
    dataname='AAPL',
    fromdate=datetime(2020, 1, 1),
    todate=datetime(2024, 12, 31)
)
cerebro.adddata(data)

# 运行回测
cerebro.run()
```

## 依赖

```bash
pip install backtrader pandas numpy matplotlib
```

## 注意事项

1. 这些策略仅供学习和研究使用
2. 实盘交易前请充分测试
3. 历史表现不代表未来收益
