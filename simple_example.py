#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版双均线策略示例
快速上手使用
"""

import backtrader as bt
import pandas as pd


class SimpleMAStrategy(bt.Strategy):
    """
    简单的双均线交叉策略
    """
    params = (
        ('fast', 5),    # 快线周期
        ('slow', 20),   # 慢线周期
    )

    def __init__(self):
        """初始化"""
        # 计算移动平均线
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.p.fast)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow)
        
        # 交叉信号
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        """策略逻辑"""
        if not self.position:  # 没有持仓
            if self.crossover > 0:  # 金叉：买入
                self.buy()
                print(f'{self.data.datetime.date(0)}: 买入 @ {self.data.close[0]:.2f}')
        else:  # 已持仓
            if self.crossover < 0:  # 死叉：卖出
                self.sell()
                print(f'{self.data.datetime.date(0)}: 卖出 @ {self.data.close[0]:.2f}')


if __name__ == '__main__':
    # 创建引擎
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(SimpleMAStrategy)
    
    # 读取数据
    df = pd.read_csv('sz000001.csv', encoding='gbk', skiprows=1)
    df.rename(columns={'交易日期': 'date', '开盘价': 'open', '最高价': 'high', 
                       '最低价': 'low', '收盘价': 'close', '成交量': 'volume'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # 添加数据
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    
    # 设置初始资金
    cerebro.broker.setcash(100000.0)
    
    # 设置手续费
    cerebro.broker.setcommission(commission=0.001)
    
    # 设置交易量
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)
    
    # 打印初始资金
    print(f'初始资金: {cerebro.broker.getvalue():.2f}')
    
    # 运行回测
    cerebro.run()
    
    # 打印最终资金
    final_value = cerebro.broker.getvalue()
    print(f'期末资金: {final_value:.2f}')
    print(f'收益率: {((final_value - 100000) / 100000 * 100):.2f}%')
    
    # 绘图
    cerebro.plot()
