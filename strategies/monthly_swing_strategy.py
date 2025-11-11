#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国建筑（601668.SH）月级波段交易策略
基于MACD、均线、成交量和RSI的综合策略
"""

import backtrader as bt
import pandas as pd
import datetime


class MonthlySwingStrategy(bt.Strategy):
    """
    月级波段交易策略
    
    入场信号：
    1. 月线MACD金叉（快线突破慢线）
    2. 收盘价站稳月线MA60
    3. 当月成交量较前3个月均值放大30%以上
    
    出场信号（满足任一条件）：
    1. 月线MACD死叉 + RSI(14)超买(>70)
    2. 股价从波段高点回撤5%（动态止盈）
    3. 达到15%固定止盈
    
    止损规则（满足任一条件）：
    1. 买入后股价跌破入场价8%
    2. 跌破月线MA120
    
    仓位管理：
    - 首次建仓30%仓位
    - 若股价回调3%且未触发止损，加仓20%（总仓位不超过50%）
    """
    
    params = (
        # MACD参数
        ('macd_fast', 12),          # MACD快线周期
        ('macd_slow', 26),          # MACD慢线周期
        ('macd_signal', 9),         # MACD信号线周期
        
        # 均线参数
        ('ma_short', 60),           # 短期均线（MA60）
        ('ma_long', 120),           # 长期均线（MA120）
        
        # RSI参数
        ('rsi_period', 14),         # RSI周期
        ('rsi_overbought', 70),     # RSI超买阈值
        
        # 成交量参数
        ('volume_period', 3),       # 成交量对比周期（月）
        ('volume_threshold', 1.3),  # 成交量放大倍数（130%）
        
        # 止盈止损参数
        ('stop_loss_pct', 0.08),    # 固定止损比例（8%）
        ('take_profit_pct', 0.15),  # 固定止盈比例（15%）
        ('trailing_stop_pct', 0.05), # 动态止盈回撤比例（5%）
        ('pullback_pct', 0.03),     # 加仓回调比例（3%）
        
        # 仓位管理参数
        ('initial_position', 0.30), # 首次建仓比例（30%）
        ('add_position', 0.20),     # 加仓比例（20%）
        ('max_position', 0.50),     # 最大仓位（50%）
        
        # 日志开关
        ('printlog', True),
    )

    def __init__(self):
        """
        初始化策略，计算所需指标
        """
        # 保存数据引用
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.datavolume = self.datas[0].volume
        
        # 订单和交易状态
        self.order = None
        self.entry_price = None          # 入场价格
        self.highest_price = None        # 波段最高价
        self.has_added_position = False  # 是否已加仓
        self.current_position_pct = 0.0  # 当前仓位比例
        
        # 计算MACD指标
        self.macd = bt.indicators.MACD(
            self.datas[0].close,
            period_me1=self.params.macd_fast,
            period_me2=self.params.macd_slow,
            period_signal=self.params.macd_signal
        )
        self.macd_line = self.macd.macd        # MACD快线（DIF）
        self.signal_line = self.macd.signal    # MACD慢线（DEA）
        
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
        
        # 计算成交量均值（用于判断放量）
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
        """
        日志输出函数
        @param txt 日志内容
        @param dt 日期时间
        @param doprint 是否强制打印
        """
        if doprint is None:
            doprint = self.params.printlog
        
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}, {txt}')

    def notify_order(self, order):
        """
        订单状态通知
        @param order 订单对象
        """
        if order.status in [order.Submitted, order.Accepted]:
            # 订单已提交/已接受
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'买入执行 - 价格: {order.executed.price:.2f}, '
                    f'数量: {order.executed.size:.0f}, '
                    f'成本: {order.executed.value:.2f}, '
                    f'手续费: {order.executed.comm:.2f}'
                )
                
                # 记录入场价格
                if self.entry_price is None:
                    self.entry_price = order.executed.price
                    self.highest_price = order.executed.price
                    self.log(f'首次建仓 - 入场价: {self.entry_price:.2f}')
                else:
                    self.log(f'加仓成功 - 原入场价: {self.entry_price:.2f}, 当前价: {order.executed.price:.2f}')
                    
            else:  # 卖出
                self.log(
                    f'卖出执行 - 价格: {order.executed.price:.2f}, '
                    f'数量: {order.executed.size:.0f}, '
                    f'成本: {order.executed.value:.2f}, '
                    f'手续费: {order.executed.comm:.2f}'
                )

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'订单异常 - 状态: {order.getstatusname()}')

        # 重置订单
        self.order = None

    def notify_trade(self, trade):
        """
        交易通知
        @param trade 交易对象
        """
        if not trade.isclosed:
            return

        self.log(
            f'交易完成 - 毛利润: {trade.pnl:.2f}, '
            f'净利润: {trade.pnlcomm:.2f}, '
            f'收益率: {(trade.pnlcomm / trade.value * 100):.2f}%'
        )
        
        # 重置交易状态
        self.entry_price = None
        self.highest_price = None
        self.has_added_position = False
        self.current_position_pct = 0.0

    def check_entry_signal(self):
        """
        检查入场信号
        @return True表示满足入场条件
        """
        # 确保有足够的数据
        if len(self.datas[0]) < self.params.ma_long:
            return False
        
        # 条件1：MACD金叉（快线上穿慢线）
        macd_golden_cross = self.macd_crossover[0] > 0
        
        # 条件2：收盘价站稳MA60（收盘价 > MA60）
        price_above_ma60 = self.dataclose[0] > self.ma60[0]
        
        # 条件3：成交量放大（当前成交量 > 前3月均值 * 1.3）
        volume_surge = (
            len(self.datavolume) > self.params.volume_period and
            self.datavolume[0] > self.volume_ma[0] * self.params.volume_threshold
        )
        
        # 打印信号检查详情
        if macd_golden_cross or volume_surge:
            self.log(
                f'信号检查 - MACD金叉: {macd_golden_cross}, '
                f'价格>MA60: {price_above_ma60} (价格:{self.dataclose[0]:.2f}, MA60:{self.ma60[0]:.2f}), '
                f'成交量放大: {volume_surge} (当前:{self.datavolume[0]:.0f}, 均值:{self.volume_ma[0]:.0f})',
                doprint=True
            )
        
        # 所有条件都满足才返回True
        return macd_golden_cross and price_above_ma60 and volume_surge

    def check_exit_signal(self):
        """
        检查出场信号
        @return (是否出场, 出场原因)
        """
        if not self.position:
            return False, None
        
        # 更新波段最高价
        if self.dataclose[0] > self.highest_price:
            self.highest_price = self.dataclose[0]
        
        # 条件1：MACD死叉 + RSI超买
        macd_death_cross = self.macd_crossover[0] < 0
        rsi_overbought = self.rsi[0] > self.params.rsi_overbought
        
        if macd_death_cross and rsi_overbought:
            return True, f'MACD死叉+RSI超买 (RSI:{self.rsi[0]:.2f})'
        
        # 条件2：从波段高点回撤5%（动态止盈）
        if self.highest_price is not None:
            drawdown_from_high = (self.highest_price - self.dataclose[0]) / self.highest_price
            if drawdown_from_high >= self.params.trailing_stop_pct:
                return True, f'动态止盈 (最高:{self.highest_price:.2f}, 当前:{self.dataclose[0]:.2f}, 回撤:{drawdown_from_high*100:.2f}%)'
        
        # 条件3：达到15%固定止盈
        if self.entry_price is not None:
            profit_pct = (self.dataclose[0] - self.entry_price) / self.entry_price
            if profit_pct >= self.params.take_profit_pct:
                return True, f'固定止盈 (入场:{self.entry_price:.2f}, 当前:{self.dataclose[0]:.2f}, 盈利:{profit_pct*100:.2f}%)'
        
        return False, None

    def check_stop_loss(self):
        """
        检查止损信号
        @return (是否止损, 止损原因)
        """
        if not self.position or self.entry_price is None:
            return False, None
        
        # 条件1：跌破入场价8%
        loss_pct = (self.entry_price - self.dataclose[0]) / self.entry_price
        if loss_pct >= self.params.stop_loss_pct:
            return True, f'固定止损 (入场:{self.entry_price:.2f}, 当前:{self.dataclose[0]:.2f}, 亏损:{loss_pct*100:.2f}%)'
        
        # 条件2：跌破MA120
        if self.dataclose[0] < self.ma120[0]:
            return True, f'跌破MA120 (当前:{self.dataclose[0]:.2f}, MA120:{self.ma120[0]:.2f})'
        
        return False, None

    def check_add_position_signal(self):
        """
        检查加仓信号
        @return True表示满足加仓条件
        """
        # 如果已经加仓过，不再加仓
        if self.has_added_position:
            return False
        
        # 如果没有持仓或没有入场价，不加仓
        if not self.position or self.entry_price is None:
            return False
        
        # 如果当前仓位已达到最大仓位，不加仓
        if self.current_position_pct >= self.params.max_position:
            return False
        
        # 股价回调3%且未触发止损
        pullback_pct = (self.entry_price - self.dataclose[0]) / self.entry_price
        
        # 检查是否会触发止损
        will_stop_loss, _ = self.check_stop_loss()
        
        if pullback_pct >= self.params.pullback_pct and not will_stop_loss:
            self.log(
                f'加仓信号 - 回调:{pullback_pct*100:.2f}% '
                f'(入场:{self.entry_price:.2f}, 当前:{self.dataclose[0]:.2f})'
            )
            return True
        
        return False

    def next(self):
        """
        策略主逻辑（每个月K线收盘后执行）
        """
        # 记录当前状态
        self.log(
            f'收盘价: {self.dataclose[0]:.2f}, '
            f'MACD: {self.macd_line[0]:.4f}, '
            f'Signal: {self.signal_line[0]:.4f}, '
            f'RSI: {self.rsi[0]:.2f}, '
            f'持仓: {self.position.size if self.position else 0}'
        )
        
        # 如果有订单在处理中，等待
        if self.order:
            return
        
        # 检查止损（优先级最高）
        should_stop_loss, stop_loss_reason = self.check_stop_loss()
        if should_stop_loss:
            self.log(f'触发止损: {stop_loss_reason}', doprint=True)
            self.order = self.sell(size=self.position.size)
            return
        
        # 检查出场信号
        should_exit, exit_reason = self.check_exit_signal()
        if should_exit:
            self.log(f'触发出场: {exit_reason}', doprint=True)
            self.order = self.sell(size=self.position.size)
            return
        
        # 检查加仓信号
        if self.check_add_position_signal():
            # 计算加仓数量
            cash = self.broker.getcash()
            add_value = cash * self.params.add_position / (1 - self.params.add_position)
            add_size = int(add_value / self.dataclose[0] / 100) * 100  # 按手（100股）计算
            
            if add_size > 0:
                self.log(f'执行加仓 - 数量: {add_size}股', doprint=True)
                self.order = self.buy(size=add_size)
                self.has_added_position = True
                self.current_position_pct = self.params.max_position
            return
        
        # 检查入场信号（只在没有持仓时）
        if not self.position:
            if self.check_entry_signal():
                # 计算首次建仓数量
                cash = self.broker.getcash()
                total_value = self.broker.getvalue()
                position_value = total_value * self.params.initial_position
                size = int(position_value / self.dataclose[0] / 100) * 100  # 按手（100股）计算
                
                if size > 0:
                    self.log(
                        f'触发入场信号 - 建仓{self.params.initial_position*100:.0f}% '
                        f'(数量: {size}股, 价格: {self.dataclose[0]:.2f})',
                        doprint=True
                    )
                    self.order = self.buy(size=size)
                    self.current_position_pct = self.params.initial_position

    def stop(self):
        """
        策略结束时调用
        """
        self.log(
            f'策略结束 - 期末总值: {self.broker.getvalue():.2f}',
            doprint=True
        )


def run_backtest():
    """
    运行回测主函数
    """
    print('='*80)
    print('中国建筑（601668.SH）月级波段交易策略回测')
    print('='*80)
    
    # 创建Cerebro引擎
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(MonthlySwingStrategy)
    
    # 读取数据
    print('\n正在加载数据...')
    df = pd.read_csv('sh601668.csv', encoding='gbk', skiprows=1)
    
    # 列名映射
    df.rename(columns={
        '交易日期': 'date',
        '开盘价': 'open',
        '最高价': 'high',
        '最低价': 'low',
        '收盘价': 'close',
        '成交量': 'volume'
    }, inplace=True)
    
    # 转换日期格式
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)
    
    print(f'数据加载完成 - 总行数: {len(df)}, 日期范围: {df.index[0]} 至 {df.index[-1]}')
    
    # 将日线数据重采样为月线数据
    print('正在将日线数据转换为月线数据...')
    df_monthly = df.resample('M').agg({
        'open': 'first',      # 月开盘价：取第一个交易日的开盘价
        'high': 'max',        # 月最高价：取最高值
        'low': 'min',         # 月最低价：取最低值
        'close': 'last',      # 月收盘价：取最后一个交易日的收盘价
        'volume': 'sum'       # 月成交量：求和
    })
    
    # 删除包含NaN的行
    df_monthly.dropna(inplace=True)
    
    print(f'月线数据生成完成 - 总行数: {len(df_monthly)}, 日期范围: {df_monthly.index[0]} 至 {df_monthly.index[-1]}')
    print(f'\n月线数据样本（前5行）:')
    print(df_monthly.head())
    
    # 创建数据源（明确指定为月线数据）
    data = bt.feeds.PandasData(
        dataname=df_monthly,
        datetime=None,
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
        openinterest=-1,
        timeframe=bt.TimeFrame.Months,  # 明确指定时间框架为月线
        compression=1
    )
    
    # 添加数据到Cerebro
    cerebro.adddata(data)
    
    # 设置初始资金：100万
    initial_cash = 1000000.0
    cerebro.broker.setcash(initial_cash)
    
    # 设置佣金：万2.5（0.00025）
    cerebro.broker.setcommission(commission=0.00025)
    
    # 设置滑点：0.1%
    cerebro.broker.set_slippage_perc(perc=0.001)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Months)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 打印初始信息
    print(f'\n{"="*80}')
    print('回测配置')
    print(f'{"="*80}')
    print(f'初始资金: {initial_cash:,.2f}元')
    print(f'佣金费率: 万2.5 (0.025%)')
    print(f'滑点: 0.1%')
    print(f'数据周期: 月线')
    print(f'策略参数:')
    print(f'  - MACD: ({MonthlySwingStrategy.params.macd_fast}, {MonthlySwingStrategy.params.macd_slow}, {MonthlySwingStrategy.params.macd_signal})')
    print(f'  - 均线: MA{MonthlySwingStrategy.params.ma_short}, MA{MonthlySwingStrategy.params.ma_long}')
    print(f'  - RSI周期: {MonthlySwingStrategy.params.rsi_period}')
    print(f'  - 止损: {MonthlySwingStrategy.params.stop_loss_pct*100}%')
    print(f'  - 固定止盈: {MonthlySwingStrategy.params.take_profit_pct*100}%')
    print(f'  - 动态止盈: {MonthlySwingStrategy.params.trailing_stop_pct*100}%')
    print(f'  - 首次建仓: {MonthlySwingStrategy.params.initial_position*100}%')
    print(f'  - 加仓比例: {MonthlySwingStrategy.params.add_position*100}%')
    print(f'  - 最大仓位: {MonthlySwingStrategy.params.max_position*100}%')
    
    print(f'\n{"="*80}')
    print('开始回测...')
    print(f'{"="*80}\n')
    
    # 运行回测
    results = cerebro.run()
    strat = results[0]
    
    # 获取最终资金
    final_value = cerebro.broker.getvalue()
    
    # 打印回测结果
    print(f'\n{"="*80}')
    print('回测结果')
    print(f'{"="*80}')
    print(f'初始资金: {initial_cash:,.2f}元')
    print(f'期末资金: {final_value:,.2f}元')
    print(f'总收益: {final_value - initial_cash:,.2f}元')
    print(f'收益率: {((final_value - initial_cash) / initial_cash * 100):.2f}%')
    
    # 分析器结果
    print(f'\n{"="*80}')
    print('绩效指标')
    print(f'{"="*80}')
    
    # 夏普比率
    sharpe = strat.analyzers.sharpe.get_analysis()
    sharpe_ratio = sharpe.get('sharperatio', None)
    print(f'夏普比率: {sharpe_ratio if sharpe_ratio else "N/A"}')
    
    # 最大回撤
    drawdown = strat.analyzers.drawdown.get_analysis()
    print(f'最大回撤: {drawdown.max.drawdown:.2f}%')
    print(f'最长回撤期: {drawdown.max.len}个月')
    
    # 收益分析
    returns = strat.analyzers.returns.get_analysis()
    print(f'总收益率: {returns.get("rtot", 0) * 100:.2f}%')
    print(f'年化收益率: {returns.get("rnorm100", 0):.2f}%')
    
    # 交易分析
    trades = strat.analyzers.trades.get_analysis()
    print(f'\n{"="*80}')
    print('交易统计')
    print(f'{"="*80}')
    
    total_closed = trades.get('total', {}).get('closed', 0) if isinstance(trades, dict) else 0
    print(f'总交易次数: {total_closed}')
    
    if total_closed > 0:
        won_total = trades.get('won', {}).get('total', 0) if isinstance(trades, dict) else 0
        lost_total = trades.get('lost', {}).get('total', 0) if isinstance(trades, dict) else 0
        
        print(f'盈利交易: {won_total}')
        print(f'亏损交易: {lost_total}')
        
        if won_total > 0:
            print(f'胜率: {(won_total / total_closed * 100):.2f}%')
            
            won_pnl_total = trades.get('won', {}).get('pnl', {}).get('total', 0)
            won_pnl_avg = trades.get('won', {}).get('pnl', {}).get('average', 0)
            print(f'平均盈利: {won_pnl_avg:,.2f}元')
        
        if lost_total > 0:
            lost_pnl_total = trades.get('lost', {}).get('pnl', {}).get('total', 0)
            lost_pnl_avg = trades.get('lost', {}).get('pnl', {}).get('average', 0)
            print(f'平均亏损: {lost_pnl_avg:,.2f}元')
    
    # 绘制结果
    print(f'\n正在生成回测图表...')
    cerebro.plot(style='candlestick', volume=True)
    
    print(f'\n{"="*80}')
    print('回测完成！')
    print(f'{"="*80}')
    
    # 参数优化建议
    print(f'\n{"="*80}')
    print('参数优化建议')
    print(f'{"="*80}')
    print('1. MACD参数优化：')
    print('   - 可尝试不同的快慢线周期组合，如(8,17,9)、(12,26,9)、(19,39,9)')
    print('   - 使用cerebro.optstrategy()进行参数网格搜索')
    print('')
    print('2. 止盈止损优化：')
    print('   - 根据历史波动率动态调整止损比例')
    print('   - 测试不同的固定止盈比例(10%-20%)')
    print('   - 调整动态止盈的回撤阈值(3%-8%)')
    print('')
    print('3. 仓位管理优化：')
    print('   - 根据波动率调整初始仓位(20%-40%)')
    print('   - 实现金字塔式加仓(多次小额加仓)')
    print('   - 考虑凯利公式计算最优仓位')
    print('')
    print('4. 信号过滤优化：')
    print('   - 结合市场大盘指数(如上证指数)过滤信号')
    print('   - 增加基本面指标(PE、PB、ROE等)作为过滤条件')
    print('   - 添加市场情绪指标(如VIX、换手率等)')
    print('')
    print('5. 多因子增强：')
    print('   - 增加动量因子(如20日涨跌幅)')
    print('   - 增加波动率因子(如ATR、布林带宽度)')
    print('   - 增加量价因子(如OBV、量比等)')
    print('   - 使用机器学习模型整合多个因子')
    print('')
    print('6. 风险管理优化：')
    print('   - 设置单笔交易最大亏损限额')
    print('   - 实现账户总资金回撤保护')
    print('   - 添加时间止损(持仓超过N个月自动平仓)')
    print(f'{"="*80}')


if __name__ == '__main__':
    run_backtest()
