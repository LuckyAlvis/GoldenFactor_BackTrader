#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国建筑（601668.SH）月级波段交易策略 - 优化版
降低入场条件严格度，增加交易机会
"""

import backtrader as bt
import pandas as pd
import datetime


class MonthlySwingOptimized(bt.Strategy):
    """
    月级波段交易策略 - 优化版
    
    优化点：
    1. 降低成交量放大阈值（从30%降至20%）
    2. 入场条件改为满足2/3即可（更灵活）
    3. 增加趋势确认机制
    """
    
    params = (
        # MACD参数
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        
        # 均线参数
        ('ma_short', 60),
        ('ma_long', 120),
        
        # RSI参数
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        
        # 成交量参数（优化：降低阈值）
        ('volume_period', 3),
        ('volume_threshold', 1.2),  # 从1.3降至1.2（放大20%）
        
        # 止盈止损参数
        ('stop_loss_pct', 0.08),
        ('take_profit_pct', 0.15),
        ('trailing_stop_pct', 0.05),
        ('pullback_pct', 0.03),
        
        # 仓位管理参数
        ('initial_position', 0.30),
        ('add_position', 0.20),
        ('max_position', 0.50),
        
        # 入场条件模式（优化：增加灵活性）
        ('entry_mode', 'flexible'),  # 'strict'(严格) 或 'flexible'(灵活)
        ('min_conditions', 2),       # 灵活模式下最少满足的条件数
        
        # 日志开关
        ('printlog', True),
    )

    def __init__(self):
        """初始化策略"""
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.datavolume = self.datas[0].volume
        
        self.order = None
        self.entry_price = None
        self.highest_price = None
        self.has_added_position = False
        self.current_position_pct = 0.0
        
        # 计算MACD指标
        self.macd = bt.indicators.MACD(
            self.datas[0].close,
            period_me1=self.params.macd_fast,
            period_me2=self.params.macd_slow,
            period_signal=self.params.macd_signal
        )
        self.macd_line = self.macd.macd
        self.signal_line = self.macd.signal
        
        # 计算移动平均线
        self.ma60 = bt.indicators.SimpleMovingAverage(
            self.datas[0].close, 
            period=self.params.ma_short
        )
        self.ma120 = bt.indicators.SimpleMovingAverage(
            self.datas[0].close, 
            period=self.params.ma_long
        )
        
        # 计算RSI指标
        self.rsi = bt.indicators.RSI(
            self.datas[0].close,
            period=self.params.rsi_period
        )
        
        # 计算成交量均值
        self.volume_ma = bt.indicators.SimpleMovingAverage(
            self.datas[0].volume,
            period=self.params.volume_period
        )
        
        # MACD交叉信号
        self.macd_crossover = bt.indicators.CrossOver(
            self.macd_line, 
            self.signal_line
        )

    def log(self, txt, dt=None, doprint=None):
        """日志输出函数"""
        if doprint is None:
            doprint = self.params.printlog
        
        if doprint:
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
                
                if self.entry_price is None:
                    self.entry_price = order.executed.price
                    self.highest_price = order.executed.price
                    self.log(f'📍 首次建仓 - 入场价: {self.entry_price:.2f}')
                else:
                    self.log(f'📍 加仓成功 - 原入场价: {self.entry_price:.2f}')
                    
            else:
                self.log(
                    f'[ERROR] 卖出执行 - 价格: {order.executed.price:.2f}, '
                    f'数量: {order.executed.size:.0f}, '
                    f'成本: {order.executed.value:.2f}, '
                    f'手续费: {order.executed.comm:.2f}'
                )

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'[WARN]  订单异常 - 状态: {order.getstatusname()}')

        self.order = None

    def notify_trade(self, trade):
        """交易通知"""
        if not trade.isclosed:
            return

        profit_pct = (trade.pnlcomm / trade.value * 100) if trade.value != 0 else 0
        emoji = '💰' if trade.pnlcomm > 0 else '📉'
        
        self.log(
            f'{emoji} 交易完成 - 毛利润: {trade.pnl:.2f}, '
            f'净利润: {trade.pnlcomm:.2f}, '
            f'收益率: {profit_pct:.2f}%'
        )
        
        self.entry_price = None
        self.highest_price = None
        self.has_added_position = False
        self.current_position_pct = 0.0

    def check_entry_signal(self):
        """
        检查入场信号（优化版）
        支持严格模式和灵活模式
        """
        if len(self.datas[0]) < self.params.ma_long:
            return False
        
        # 三个核心条件
        condition1_macd = self.macd_crossover[0] > 0  # MACD金叉
        condition2_ma = self.dataclose[0] > self.ma60[0]  # 价格>MA60
        condition3_volume = (
            len(self.datavolume) > self.params.volume_period and
            self.datavolume[0] > self.volume_ma[0] * self.params.volume_threshold
        )  # 成交量放大
        
        conditions = [condition1_macd, condition2_ma, condition3_volume]
        satisfied_count = sum(conditions)
        
        # 打印详细信号
        if satisfied_count >= self.params.min_conditions:
            self.log(
                f'🔔 入场信号检查 ({satisfied_count}/3条件满足):\n'
                f'   ├─ MACD金叉: {"[OK]" if condition1_macd else "[ERROR]"} '
                f'(DIF:{self.macd_line[0]:.4f}, DEA:{self.signal_line[0]:.4f})\n'
                f'   ├─ 价格>MA60: {"[OK]" if condition2_ma else "[ERROR]"} '
                f'(价格:{self.dataclose[0]:.2f}, MA60:{self.ma60[0]:.2f})\n'
                f'   └─ 成交量放大: {"[OK]" if condition3_volume else "[ERROR]"} '
                f'(当前:{self.datavolume[0]:.0f}, 均值:{self.volume_ma[0]:.0f}, '
                f'比率:{self.datavolume[0]/self.volume_ma[0]:.2f})',
                doprint=True
            )
        
        # 根据模式判断
        if self.params.entry_mode == 'strict':
            return all(conditions)  # 严格模式：所有条件都满足
        else:
            return satisfied_count >= self.params.min_conditions  # 灵活模式：满足N个条件

    def check_exit_signal(self):
        """检查出场信号"""
        if not self.position:
            return False, None
        
        if self.dataclose[0] > self.highest_price:
            self.highest_price = self.dataclose[0]
        
        # 条件1：MACD死叉 + RSI超买
        macd_death_cross = self.macd_crossover[0] < 0
        rsi_overbought = self.rsi[0] > self.params.rsi_overbought
        
        if macd_death_cross and rsi_overbought:
            return True, f'MACD死叉+RSI超买 (RSI:{self.rsi[0]:.2f})'
        
        # 条件2：动态止盈
        if self.highest_price is not None:
            drawdown = (self.highest_price - self.dataclose[0]) / self.highest_price
            if drawdown >= self.params.trailing_stop_pct:
                return True, f'动态止盈 (最高:{self.highest_price:.2f}, 回撤:{drawdown*100:.2f}%)'
        
        # 条件3：固定止盈
        if self.entry_price is not None:
            profit = (self.dataclose[0] - self.entry_price) / self.entry_price
            if profit >= self.params.take_profit_pct:
                return True, f'固定止盈 (盈利:{profit*100:.2f}%)'
        
        return False, None

    def check_stop_loss(self):
        """检查止损信号"""
        if not self.position or self.entry_price is None:
            return False, None
        
        # 条件1：固定止损
        loss = (self.entry_price - self.dataclose[0]) / self.entry_price
        if loss >= self.params.stop_loss_pct:
            return True, f'固定止损 (亏损:{loss*100:.2f}%)'
        
        # 条件2：跌破MA120
        if self.dataclose[0] < self.ma120[0]:
            return True, f'跌破MA120 (价格:{self.dataclose[0]:.2f}, MA120:{self.ma120[0]:.2f})'
        
        return False, None

    def check_add_position_signal(self):
        """检查加仓信号"""
        if self.has_added_position or not self.position or self.entry_price is None:
            return False
        
        if self.current_position_pct >= self.params.max_position:
            return False
        
        pullback = (self.entry_price - self.dataclose[0]) / self.entry_price
        will_stop_loss, _ = self.check_stop_loss()
        
        if pullback >= self.params.pullback_pct and not will_stop_loss:
            self.log(f'📈 加仓信号 - 回调:{pullback*100:.2f}%')
            return True
        
        return False

    def next(self):
        """策略主逻辑"""
        # 简化日志（只显示关键信息）
        if self.position:
            profit = (self.dataclose[0] - self.entry_price) / self.entry_price * 100 if self.entry_price else 0
            self.log(
                f'持仓中 - 价格:{self.dataclose[0]:.2f}, '
                f'盈亏:{profit:+.2f}%, '
                f'最高:{self.highest_price:.2f}'
            )
        
        if self.order:
            return
        
        # 止损检查
        should_stop_loss, reason = self.check_stop_loss()
        if should_stop_loss:
            self.log(f'🛑 触发止损: {reason}', doprint=True)
            self.order = self.sell(size=self.position.size)
            return
        
        # 出场检查
        should_exit, reason = self.check_exit_signal()
        if should_exit:
            self.log(f'🚪 触发出场: {reason}', doprint=True)
            self.order = self.sell(size=self.position.size)
            return
        
        # 加仓检查
        if self.check_add_position_signal():
            cash = self.broker.getcash()
            add_value = cash * self.params.add_position / (1 - self.params.add_position)
            add_size = int(add_value / self.dataclose[0] / 100) * 100
            
            if add_size > 0:
                self.log(f'➕ 执行加仓 - 数量: {add_size}股', doprint=True)
                self.order = self.buy(size=add_size)
                self.has_added_position = True
                self.current_position_pct = self.params.max_position
            return
        
        # 入场检查
        if not self.position:
            if self.check_entry_signal():
                cash = self.broker.getcash()
                total_value = self.broker.getvalue()
                position_value = total_value * self.params.initial_position
                size = int(position_value / self.dataclose[0] / 100) * 100
                
                if size > 0:
                    self.log(
                        f'🎯 执行入场 - 建仓{self.params.initial_position*100:.0f}% '
                        f'(数量:{size}股, 价格:{self.dataclose[0]:.2f})',
                        doprint=True
                    )
                    self.order = self.buy(size=size)
                    self.current_position_pct = self.params.initial_position

    def stop(self):
        """策略结束"""
        final_value = self.broker.getvalue()
        self.log(f'🏁 策略结束 - 期末总值: {final_value:,.2f}', doprint=True)


def run_backtest():
    """运行回测"""
    print('='*80)
    print('中国建筑（601668.SH）月级波段交易策略 - 优化版')
    print('='*80)
    
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MonthlySwingOptimized)
    
    # 加载数据
    print('\n📊 正在加载数据...')
    df = pd.read_csv('sh601668.csv', encoding='gbk', skiprows=1)
    df.rename(columns={
        '交易日期': 'date', '开盘价': 'open', '最高价': 'high',
        '最低价': 'low', '收盘价': 'close', '成交量': 'volume'
    }, inplace=True)
    
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)
    
    # 转换为月线
    df_monthly = df.resample('M').agg({
        'open': 'first', 'high': 'max', 'low': 'min',
        'close': 'last', 'volume': 'sum'
    })
    df_monthly.dropna(inplace=True)
    
    print(f'[OK] 数据加载完成 - 月线数据: {len(df_monthly)}条')
    print(f'   日期范围: {df_monthly.index[0].date()} 至 {df_monthly.index[-1].date()}')
    
    # 创建数据源
    data = bt.feeds.PandasData(
        dataname=df_monthly,
        timeframe=bt.TimeFrame.Months,
        compression=1
    )
    
    cerebro.adddata(data)
    
    # 设置回测参数
    initial_cash = 1000000.0
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=0.00025)
    cerebro.broker.set_slippage_perc(perc=0.001)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Months)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    print(f'\n⚙️  回测配置:')
    print(f'   初始资金: {initial_cash:,.0f}元')
    print(f'   入场模式: 灵活模式（满足2/3条件）')
    print(f'   成交量阈值: {MonthlySwingOptimized.params.volume_threshold*100:.0f}%（已优化）')
    
    print(f'\n🚀 开始回测...\n')
    print('='*80)
    
    results = cerebro.run()
    strat = results[0]
    
    final_value = cerebro.broker.getvalue()
    
    # 打印结果
    print('\n' + '='*80)
    print('📈 回测结果')
    print('='*80)
    print(f'初始资金: {initial_cash:,.2f}元')
    print(f'期末资金: {final_value:,.2f}元')
    print(f'总收益: {final_value - initial_cash:,.2f}元')
    print(f'收益率: {((final_value - initial_cash) / initial_cash * 100):.2f}%')
    
    # 分析器结果
    print(f'\n📊 绩效指标')
    print('='*80)
    
    sharpe = strat.analyzers.sharpe.get_analysis()
    print(f'夏普比率: {sharpe.get("sharperatio", "N/A")}')
    
    drawdown = strat.analyzers.drawdown.get_analysis()
    print(f'最大回撤: {drawdown.max.drawdown:.2f}%')
    
    returns = strat.analyzers.returns.get_analysis()
    print(f'年化收益率: {returns.get("rnorm100", 0):.2f}%')
    
    trades = strat.analyzers.trades.get_analysis()
    total_closed = trades.get('total', {}).get('closed', 0) if isinstance(trades, dict) else 0
    
    print(f'\n📝 交易统计')
    print('='*80)
    print(f'总交易次数: {total_closed}')
    
    if total_closed > 0:
        won = trades.get('won', {}).get('total', 0)
        lost = trades.get('lost', {}).get('total', 0)
        print(f'盈利交易: {won}')
        print(f'亏损交易: {lost}')
        if won > 0:
            print(f'胜率: {(won / total_closed * 100):.2f}%')
    
    print(f'\n📉 正在生成图表...')
    cerebro.plot(style='candlestick', volume=True)
    
    print(f'\n[OK] 回测完成！')


if __name__ == '__main__':
    run_backtest()
