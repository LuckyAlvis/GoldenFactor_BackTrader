#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
特斯拉（TSLA）双均线交叉策略回测

策略逻辑：
- 入场信号：短期均线上穿长期均线（金叉）
- 出场信号：短期均线下穿长期均线（死叉）
- 仓位管理：每次使用95%可用资金

使用统一的CSV数据加载器处理数据
"""

import backtrader as bt
import pandas as pd
from datetime import datetime
from csv_data_loader import CSVDataLoader


class DualMAStrategy(bt.Strategy):
    """
    双均线交叉策略
    
    @param ma_short 短期均线周期
    @param ma_long 长期均线周期
    @param position_pct 每次交易使用的资金比例
    """
    
    params = (
        ('ma_short', 5),      # 短期均线周期
        ('ma_long', 20),      # 长期均线周期
        ('position_pct', 0.95),  # 仓位比例
        ('printlog', True),   # 是否打印日志
    )
    
    def __init__(self):
        """初始化策略"""
        # 保存收盘价引用
        self.dataclose = self.datas[0].close
        
        # 初始化订单和价格变量
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        # 添加均线指标
        self.ma_short = bt.indicators.SimpleMovingAverage(
            self.datas[0], 
            period=self.params.ma_short
        )
        self.ma_long = bt.indicators.SimpleMovingAverage(
            self.datas[0], 
            period=self.params.ma_long
        )
        
        # 添加交叉信号指标
        self.crossover = bt.indicators.CrossOver(self.ma_short, self.ma_long)
        
        # 记录交易次数
        self.trade_count = 0
    
    def log(self, txt, dt=None):
        """日志输出函数"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}, {txt}')
    
    def notify_order(self, order):
        """订单状态通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'[OK] 买入执行 - 价格: {order.executed.price:.2f}, '
                    f'数量: {order.executed.size:.0f}, '
                    f'成本: {order.executed.value:.2f}, '
                    f'手续费: {order.executed.comm:.2f}'
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(
                    f'[ERROR] 卖出执行 - 价格: {order.executed.price:.2f}, '
                    f'数量: {order.executed.size:.0f}, '
                    f'成本: {order.executed.value:.2f}, '
                    f'手续费: {order.executed.comm:.2f}'
                )
            
            self.bar_executed = len(self)
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('[WARN]  订单取消/保证金不足/拒绝')
        
        self.order = None
    
    def notify_trade(self, trade):
        """交易通知"""
        if not trade.isclosed:
            return
        
        self.trade_count += 1
        self.log(
            f'💰 交易完成 #{self.trade_count} - '
            f'毛利润: {trade.pnl:.2f}, '
            f'净利润: {trade.pnlcomm:.2f}'
        )
    
    def next(self):
        """策略主逻辑"""
        # 记录当前价格
        # self.log(f'收盘价: {self.dataclose[0]:.2f}')
        
        # 如果有订单在处理中，不操作
        if self.order:
            return
        
        # 检查是否持仓
        if not self.position:
            # 没有持仓，检查买入信号
            if self.crossover > 0:  # 金叉
                self.log(f'🔔 买入信号 - MA{self.params.ma_short}上穿MA{self.params.ma_long}')
                
                # 计算可买入的股数
                cash = self.broker.getcash()
                price = self.dataclose[0]
                size = int((cash * self.params.position_pct) / price)
                
                if size > 0:
                    self.log(f'🎯 执行买入 - 数量: {size}, 价格: {price:.2f}')
                    self.order = self.buy(size=size)
        else:
            # 持仓中，检查卖出信号
            if self.crossover < 0:  # 死叉
                self.log(f'🔔 卖出信号 - MA{self.params.ma_short}下穿MA{self.params.ma_long}')
                self.log(f'🎯 执行卖出 - 全部平仓')
                self.order = self.sell(size=self.position.size)
    
    def stop(self):
        """策略结束时调用"""
        self.log(
            f'🏁 策略结束 - MA({self.params.ma_short},{self.params.ma_long}) '
            f'期末总值: {self.broker.getvalue():.2f}',
            dt=self.datas[0].datetime.date(0)
        )


def run_backtest(csv_file='tsla_data.csv', initial_cash=100000.0, commission=0.001):
    """
    运行回测
    
    @param csv_file CSV文件路径
    @param initial_cash 初始资金
    @param commission 手续费率
    @return 回测结果字典
    """
    print('='*80)
    print('特斯拉（TSLA）双均线策略回测')
    print('='*80)
    
    # 使用统一的数据加载器加载数据
    print('\n📊 加载数据...')
    df = CSVDataLoader.load_csv(csv_file, verbose=True)
    
    # 转换为Backtrader格式
    print('\n🔄 转换数据格式...')
    bt_df = CSVDataLoader.convert_to_backtrader_format(df)
    
    # 创建Cerebro引擎
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(DualMAStrategy)
    
    # 添加数据
    data = bt.feeds.PandasData(dataname=bt_df)
    cerebro.adddata(data)
    
    # 设置初始资金
    cerebro.broker.setcash(initial_cash)
    
    # 设置手续费
    cerebro.broker.setcommission(commission=commission)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 打印初始信息
    print(f'\n💰 初始资金: {initial_cash:,.2f}')
    print(f'💵 手续费率: {commission*100:.2f}%')
    print(f'📅 回测期间: {bt_df.index[0]} 至 {bt_df.index[-1]}')
    print(f'📊 数据条数: {len(bt_df)} 条')
    
    print('\n🚀 开始回测...\n')
    print('='*80)
    
    # 运行回测
    results = cerebro.run()
    strat = results[0]
    
    # 打印最终信息
    final_value = cerebro.broker.getvalue()
    
    print('='*80)
    print('\n📈 回测结果')
    print('='*80)
    print(f'初始资金: {initial_cash:,.2f}')
    print(f'期末资金: {final_value:,.2f}')
    print(f'总收益: {final_value - initial_cash:,.2f}')
    print(f'收益率: {(final_value - initial_cash) / initial_cash * 100:.2f}%')
    
    # 获取分析结果
    print('\n📊 绩效指标')
    print('='*80)
    
    # 夏普比率
    sharpe = strat.analyzers.sharpe.get_analysis()
    sharpe_ratio = sharpe.get('sharperatio', None)
    if sharpe_ratio is not None:
        print(f'夏普比率: {sharpe_ratio:.3f}')
    else:
        print('夏普比率: N/A')
    
    # 最大回撤
    drawdown = strat.analyzers.drawdown.get_analysis()
    print(f'最大回撤: {drawdown.max.drawdown:.2f}%')
    
    # 收益率
    returns = strat.analyzers.returns.get_analysis()
    print(f'总收益率: {returns.get("rtot", 0) * 100:.2f}%')
    print(f'年化收益率: {returns.get("rnorm100", 0):.2f}%')
    
    # 交易统计
    trades = strat.analyzers.trades.get_analysis()
    print(f'\n📝 交易统计')
    print('='*80)
    total_closed = trades.get('total', {}).get('closed', 0) if isinstance(trades, dict) else 0
    print(f'总交易次数: {total_closed}')
    
    if total_closed > 0:
        won_total = trades.get('won', {}).get('total', 0) if isinstance(trades, dict) else 0
        lost_total = trades.get('lost', {}).get('total', 0) if isinstance(trades, dict) else 0
        print(f'盈利交易: {won_total}')
        print(f'亏损交易: {lost_total}')
        if won_total > 0:
            print(f'胜率: {(won_total / total_closed * 100):.2f}%')
            
            # 平均盈亏
            won_pnl = trades.get('won', {}).get('pnl', {})
            lost_pnl = trades.get('lost', {}).get('pnl', {})
            
            if isinstance(won_pnl, dict):
                avg_won = won_pnl.get('average', 0)
                print(f'平均盈利: {avg_won:.2f}')
            
            if isinstance(lost_pnl, dict):
                avg_lost = lost_pnl.get('average', 0)
                print(f'平均亏损: {avg_lost:.2f}')
    
    # 绘制图表
    print('\n📉 正在生成图表...')
    cerebro.plot(style='candlestick', barup='red', bardown='green')
    
    # 返回结果
    return {
        'initial_cash': initial_cash,
        'final_value': final_value,
        'return': (final_value - initial_cash) / initial_cash * 100,
        'sharpe': sharpe_ratio,
        'max_drawdown': drawdown.max.drawdown,
        'trades': total_closed
    }


def compare_strategies():
    """
    对比不同参数的策略表现
    """
    print('='*80)
    print('策略参数对比测试')
    print('='*80)
    
    # 不同的均线组合
    ma_combinations = [
        (5, 10),
        (5, 20),
        (10, 20),
        (10, 30),
        (20, 60),
    ]
    
    results = []
    
    for ma_short, ma_long in ma_combinations:
        print(f'\n测试参数: MA({ma_short}, {ma_long})')
        print('-'*80)
        
        # 加载数据
        df = CSVDataLoader.load_csv('tsla_data.csv', verbose=False)
        bt_df = CSVDataLoader.convert_to_backtrader_format(df)
        
        # 创建Cerebro
        cerebro = bt.Cerebro()
        
        # 添加策略（关闭日志）
        cerebro.addstrategy(
            DualMAStrategy,
            ma_short=ma_short,
            ma_long=ma_long,
            printlog=False
        )
        
        # 添加数据
        data = bt.feeds.PandasData(dataname=bt_df)
        cerebro.adddata(data)
        
        # 设置参数
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=0.001)
        
        # 添加分析器
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        # 运行
        strats = cerebro.run()
        strat = strats[0]
        
        # 获取结果
        final_value = cerebro.broker.getvalue()
        returns = strat.analyzers.returns.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        trades = strat.analyzers.trades.get_analysis()
        
        result = {
            'ma_short': ma_short,
            'ma_long': ma_long,
            'final_value': final_value,
            'return': (final_value - 100000) / 100000 * 100,
            'max_drawdown': drawdown.max.drawdown,
            'trades': trades.get('total', {}).get('closed', 0)
        }
        
        results.append(result)
        
        print(f'期末资金: {final_value:,.2f}')
        print(f'收益率: {result["return"]:.2f}%')
        print(f'最大回撤: {result["max_drawdown"]:.2f}%')
        print(f'交易次数: {result["trades"]}')
    
    # 汇总结果
    print('\n' + '='*80)
    print('策略对比汇总')
    print('='*80)
    print(f'{"参数":<15} {"期末资金":<15} {"收益率":<12} {"最大回撤":<12} {"交易次数":<10}')
    print('-'*80)
    
    for r in results:
        print(f'MA({r["ma_short"]},{r["ma_long"]:<2})    '
              f'{r["final_value"]:>12,.2f}    '
              f'{r["return"]:>8.2f}%    '
              f'{r["max_drawdown"]:>8.2f}%    '
              f'{r["trades"]:>8}')
    
    # 找出最佳策略
    best = max(results, key=lambda x: x['return'])
    print('\n' + '='*80)
    print(f'🏆 最佳策略: MA({best["ma_short"]}, {best["ma_long"]}) - 收益率: {best["return"]:.2f}%')
    print('='*80)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'compare':
        # 对比模式
        compare_strategies()
    else:
        # 单次回测模式
        run_backtest(
            csv_file='tsla_data.csv',
            initial_cash=100000.0,
            commission=0.001
        )
