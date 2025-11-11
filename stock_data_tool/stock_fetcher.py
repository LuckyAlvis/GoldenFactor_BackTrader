#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用股票数据获取器

支持任意股票代码（美股、A股等）
支持多种时间段和K线类型
支持多种导出格式（CSV、JSON、数据库）
"""

import yfinance as yf
import pandas as pd
import json
import sqlite3
import pymysql
from datetime import datetime
from pathlib import Path


class StockDataFetcher:
    """
    通用股票数据获取器
    
    @param symbol 股票代码
    @param verbose 是否显示详细信息
    """
    
    def __init__(self, symbol, verbose=True):
        self.symbol = symbol.upper()
        self.verbose = verbose
        self.data = None
        
    def fetch(self, period='1y', interval='1d', start=None, end=None):
        """
        获取股票数据
        
        @param period 时间周期：1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        @param interval K线类型：1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        @param start 开始日期（YYYY-MM-DD）
        @param end 结束日期（YYYY-MM-DD）
        @return DataFrame
        """
        try:
            ticker = yf.Ticker(self.symbol)
            
            if start and end:
                df = ticker.history(start=start, end=end, interval=interval)
            else:
                df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                if self.verbose:
                    print(f'[WARN] {self.symbol} 未获取到数据')
                return None
            
            # 重置索引，将Date作为列
            df.reset_index(inplace=True)
            
            self.data = df
            
            if self.verbose:
                print(f'[OK] {self.symbol} 获取 {len(df)} 条数据')
                print(f'     时间范围: {df["Date"].min()} 至 {df["Date"].max()}')
            
            return df
            
        except Exception as e:
            if self.verbose:
                print(f'[ERROR] 获取失败: {e}')
            return None
    
    def save_csv(self, output_path=None):
        """
        保存为CSV文件
        
        @param output_path 输出路径
        @return 保存的文件路径
        """
        if self.data is None or self.data.empty:
            print('[ERROR] 没有数据可保存')
            return None
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'{self.symbol}_{timestamp}.csv'
        
        self.data.to_csv(output_path, index=False)
        
        if self.verbose:
            print(f'[OK] 已保存到: {output_path}')
        
        return output_path
    
    def save_json(self, output_path=None):
        """
        保存为JSON文件
        
        @param output_path 输出路径
        @return 保存的文件路径
        """
        if self.data is None or self.data.empty:
            print('[ERROR] 没有数据可保存')
            return None
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'{self.symbol}_{timestamp}.json'
        
        # 转换日期为字符串
        df_copy = self.data.copy()
        df_copy['Date'] = df_copy['Date'].astype(str)
        
        data_dict = df_copy.to_dict(orient='records')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)
        
        if self.verbose:
            print(f'[OK] 已保存到: {output_path}')
        
        return output_path
    
    def save_sqlite(self, db_path='stock_data.db', table_name=None):
        """
        保存到SQLite数据库
        
        @param db_path 数据库路径
        @param table_name 表名
        @return 是否成功
        """
        if self.data is None or self.data.empty:
            print('[ERROR] 没有数据可保存')
            return False
        
        if table_name is None:
            table_name = f'stock_{self.symbol.lower()}'
        
        try:
            conn = sqlite3.connect(db_path)
            self.data.to_sql(table_name, conn, if_exists='replace', index=False)
            conn.close()
            
            if self.verbose:
                print(f'[OK] 已保存到数据库: {db_path} (表: {table_name})')
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f'[ERROR] 保存失败: {e}')
            return False
    
    def save_mysql(self, host, port, user, password, database, table_name='stock_data'):
        """
        保存到MySQL数据库
        
        @param host MySQL主机
        @param port MySQL端口
        @param user MySQL用户名
        @param password MySQL密码
        @param database MySQL数据库名
        @param table_name 表名
        @return 是否成功
        """
        if self.data is None or self.data.empty:
            print('[ERROR] 没有数据可保存')
            return False
        
        try:
            # 连接MySQL
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                charset='utf8mb4'
            )
            cursor = conn.cursor()
            
            # 创建表（如果不存在）
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
              `id` BIGINT AUTO_INCREMENT,
              `symbol` VARCHAR(20) NOT NULL COMMENT '股票代码',
              `trade_date` DATETIME NOT NULL COMMENT '交易日期',
              `open_price` DECIMAL(20,4) COMMENT '开盘价',
              `high_price` DECIMAL(20,4) COMMENT '最高价',
              `low_price` DECIMAL(20,4) COMMENT '最低价',
              `close_price` DECIMAL(20,4) COMMENT '收盘价',
              `volume` BIGINT COMMENT '成交量',
              `dividends` DECIMAL(20,4) DEFAULT 0 COMMENT '分红',
              `stock_splits` DECIMAL(20,4) DEFAULT 0 COMMENT '拆股',
              `interval_type` VARCHAR(10) DEFAULT '1d' COMMENT 'K线类型',
              `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
              `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
              PRIMARY KEY (`id`),
              UNIQUE KEY `uk_symbol_date_interval` (`symbol`, `trade_date`, `interval_type`),
              KEY `idx_symbol` (`symbol`),
              KEY `idx_trade_date` (`trade_date`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票历史数据表'
            """
            cursor.execute(create_table_sql)
            conn.commit()
            
            # 准备插入SQL
            insert_sql = f"""
            INSERT INTO {table_name} 
            (symbol, trade_date, open_price, high_price, low_price, close_price, 
             volume, dividends, stock_splits, interval_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                open_price = VALUES(open_price),
                high_price = VALUES(high_price),
                low_price = VALUES(low_price),
                close_price = VALUES(close_price),
                volume = VALUES(volume),
                dividends = VALUES(dividends),
                stock_splits = VALUES(stock_splits)
            """
            
            # 准备数据
            data_list = []
            for _, row in self.data.iterrows():
                trade_date = pd.to_datetime(row['Date'])
                if hasattr(trade_date, 'tz_localize'):
                    trade_date = trade_date.tz_localize(None)
                
                data_list.append((
                    self.symbol,
                    trade_date,
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    int(row['Volume']),
                    float(row.get('Dividends', 0)),
                    float(row.get('Stock Splits', 0)),
                    '1d'  # 默认日线，可以后续优化为参数
                ))
            
            # 批量插入
            cursor.executemany(insert_sql, data_list)
            conn.commit()
            
            cursor.close()
            conn.close()
            
            if self.verbose:
                print(f'[OK] 已保存到MySQL: {host}:{port}/{database} (表: {table_name}, {len(data_list)}条)')
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f'[ERROR] 保存到MySQL失败: {e}')
            return False
    
    def get_data(self):
        """
        获取DataFrame数据
        
        @return DataFrame
        """
        return self.data


def main():
    """示例用法"""
    # 创建获取器
    fetcher = StockDataFetcher('AAPL')
    
    # 获取数据
    df = fetcher.fetch(period='1mo', interval='1d')
    
    if df is not None:
        # 保存为CSV
        fetcher.save_csv('output.csv')
        
        # 保存为JSON
        fetcher.save_json('output.json')
        
        # 保存到数据库
        fetcher.save_sqlite('stock_data.db')


if __name__ == '__main__':
    main()
