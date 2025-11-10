#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双均线交叉策略回测
使用backtrader框架实现经典的双均线交叉策略
"""

import backtrader as bt
import pandas as pd
import os
from datetime import datetime


class DualMovingAverageStrategy(bt.Strategy):
    """
    双均线交叉策略
    当短期均线上穿长期均线时买入
    当短期均线下穿长期均线时卖出
    """
    
    params = (
        ('fast_period', 5),   # 短期均线周期
        ('slow_period', 20),  # 长期均线周期
        ('printlog', True),   # 是否打印日志
    )

    def __init__(self):
        """
        初始化策略
        """
        # 保存收盘价引用
        self.dataclose = self.datas[0].close
        
        # 记录订单和价格
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        # 添加移动平均线指标
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.fast_period)
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.slow_period)
        
        # 添加交叉信号指标
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def log(self, txt, dt=None, doprint=False):
        """
        日志打印函数
        @param txt 日志内容
        @param dt 日期时间
        @param doprint 是否强制打印
        """
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}, {txt}')

    def notify_order(self, order):
        """
        订单状态通知
        @param order 订单对象
        """
        if order.status in [order.Submitted, order.Accepted]:
            # 订单已提交/已接受 - 无需操作
            return

        # 检查订单是否完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'买入执行, 价格: {order.executed.price:.2f}, '
                    f'成本: {order.executed.value:.2f}, '
                    f'手续费: {order.executed.comm:.2f}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # 卖出
                self.log(
                    f'卖出执行, 价格: {order.executed.price:.2f}, '
                    f'成本: {order.executed.value:.2f}, '
                    f'手续费: {order.executed.comm:.2f}')

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 重置订单
        self.order = None

    def notify_trade(self, trade):
        """
        交易通知
        @param trade 交易对象
        """
        if not trade.isclosed:
            return

        self.log(f'交易利润, 毛利润: {trade.pnl:.2f}, 净利润: {trade.pnlcomm:.2f}')

    def next(self):
        """
        策略主逻辑
        """
        # 记录收盘价
        self.log(f'收盘价: {self.dataclose[0]:.2f}')

        # 检查是否有订单在处理中
        if self.order:
            return

        # 检查是否持仓
        if not self.position:
            # 没有持仓，检查是否买入
            if self.crossover > 0:  # 快线上穿慢线
                self.log(f'买入信号, 快线: {self.fast_ma[0]:.2f}, 慢线: {self.slow_ma[0]:.2f}')
                # 计算可以买入的股数（使用95%的可用资金）
                self.order = self.buy()
        else:
            # 已持仓，检查是否卖出
            if self.crossover < 0:  # 快线下穿慢线
                self.log(f'卖出信号, 快线: {self.fast_ma[0]:.2f}, 慢线: {self.slow_ma[0]:.2f}')
                self.order = self.sell()

    def stop(self):
        """
        策略结束时调用
        """
        self.log(
            f'(快线周期: {self.params.fast_period}, 慢线周期: {self.params.slow_period}) '
            f'期末总值: {self.broker.getvalue():.2f}', 
            doprint=True)


def run_backtest(csv_file, initial_cash=100000.0, commission=0.001):
    """
    运行回测
    @param csv_file CSV数据文件路径
    @param initial_cash 初始资金
    @param commission 手续费率
    @return 回测结果
    """
    print(f'\n{"="*60}')
    print(f'开始回测: {os.path.basename(csv_file)}')
    print(f'{"="*60}')
    
    # 创建Cerebro引擎
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(DualMovingAverageStrategy)
    
    # 读取数据
    try:
        # 尝试使用GBK编码读取，跳过第一行说明文字
        df = pd.read_csv(csv_file, encoding='gbk', skiprows=1)
    except:
        # 如果失败，尝试UTF-8
        df = pd.read_csv(csv_file, encoding='utf-8', skiprows=1)
    
    print(f'\n数据列名: {df.columns.tolist()}')
    print(f'数据形状: {df.shape}')
    print(f'\n前5行数据:')
    print(df.head())
    
    # 根据实际列名调整（假设列名可能是中文）
    # 常见的列名映射
    column_mapping = {
        '日期': 'date',
        '交易日期': 'date',
        '开盘价': 'open',
        '最高价': 'high', 
        '最低价': 'low',
        '收盘价': 'close',
        '前收盘价': 'preclose',
        '成交量': 'volume',
        '成交额': 'amount'
    }
    
    # 重命名列
    df.rename(columns=column_mapping, inplace=True)
    
    # 确保有必需的列
    required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    for col in required_columns:
        if col not in df.columns:
            print(f'警告: 缺少必需列 {col}')
            print(f'可用列: {df.columns.tolist()}')
            return None
    
    # 转换日期格式
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)
    
    # 创建数据源
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
        openinterest=-1
    )
    
    # 添加数据到Cerebro
    cerebro.adddata(data)
    
    # 设置初始资金
    cerebro.broker.setcash(initial_cash)
    
    # 设置手续费
    cerebro.broker.setcommission(commission=commission)
    
    # 设置每次交易的股数
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 打印初始资金
    print(f'\n初始资金: {cerebro.broker.getvalue():.2f}')
    
    # 运行回测
    results = cerebro.run()
    strat = results[0]
    
    # 打印最终资金
    final_value = cerebro.broker.getvalue()
    print(f'期末资金: {final_value:.2f}')
    print(f'收益率: {((final_value - initial_cash) / initial_cash * 100):.2f}%')
    
    # 打印分析结果
    print(f'\n{"="*60}')
    print('回测分析结果')
    print(f'{"="*60}')
    
    # 夏普比率
    sharpe = strat.analyzers.sharpe.get_analysis()
    print(f'夏普比率: {sharpe.get("sharperatio", "N/A")}')
    
    # 最大回撤
    drawdown = strat.analyzers.drawdown.get_analysis()
    print(f'最大回撤: {drawdown.max.drawdown:.2f}%')
    
    # 收益分析
    returns = strat.analyzers.returns.get_analysis()
    print(f'总收益率: {returns.get("rtot", 0) * 100:.2f}%')
    print(f'年化收益率: {returns.get("rnorm100", 0):.2f}%')
    
    # 交易分析
    trades = strat.analyzers.trades.get_analysis()
    print(f'\n交易统计:')
    total_closed = trades.get('total', {}).get('closed', 0) if isinstance(trades, dict) else getattr(trades.get('total', {}), 'closed', 0)
    print(f'总交易次数: {total_closed}')
    if total_closed > 0:
        won_total = trades.get('won', {}).get('total', 0) if isinstance(trades, dict) else 0
        lost_total = trades.get('lost', {}).get('total', 0) if isinstance(trades, dict) else 0
        print(f'盈利交易: {won_total}')
        print(f'亏损交易: {lost_total}')
        if won_total > 0:
            print(f'胜率: {(won_total / total_closed * 100):.2f}%')
    
    # 绘制结果
    print(f'\n正在生成回测图表...')
    cerebro.plot(style='candlestick')
    
    return {
        'final_value': final_value,
        'return': (final_value - initial_cash) / initial_cash * 100,
        'sharpe': sharpe.get('sharperatio', None),
        'max_drawdown': drawdown.max.drawdown,
        'trades': total_closed
    }


def main():
    """
    主函数
    """
    # 设置参数
    initial_cash = 100000.0  # 初始资金10万
    commission = 0.001  # 手续费0.1%
    
    # 获取当前目录下的所有CSV文件
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_files = [f for f in os.listdir(current_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print('未找到CSV文件')
        return
    
    print(f'找到 {len(csv_files)} 个CSV文件')
    
    # 对每个CSV文件运行回测
    results = {}
    for csv_file in csv_files:
        csv_path = os.path.join(current_dir, csv_file)
        result = run_backtest(csv_path, initial_cash, commission)
        if result:
            results[csv_file] = result
    
    # 汇总结果
    if results:
        print(f'\n{"="*60}')
        print('回测结果汇总')
        print(f'{"="*60}')
        print(f'{"股票代码":<15} {"期末资金":<15} {"收益率":<10} {"夏普比率":<10} {"最大回撤":<10} {"交易次数":<10}')
        print(f'{"-"*60}')
        for csv_file, result in results.items():
            print(f'{csv_file:<15} '
                  f'{result["final_value"]:<15.2f} '
                  f'{result["return"]:<10.2f}% '
                  f'{result["sharpe"] if result["sharpe"] else "N/A":<10} '
                  f'{result["max_drawdown"]:<10.2f}% '
                  f'{result["trades"]:<10}')


if __name__ == '__main__':
    main()
