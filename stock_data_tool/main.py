#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据获取工具 - 主程序

使用方法：
1. 修改 config.py 中的配置
2. 运行：python3 main.py
"""

import sys
from pathlib import Path
from stock_fetcher import StockDataFetcher
import config


def main():
    """主函数"""
    print('='*60)
    print('股票数据获取工具')
    print('='*60)
    
    # 显示配置
    print(f'\n股票代码: {config.SYMBOL}')
    
    if config.START_DATE and config.END_DATE:
        print(f'时间范围: {config.START_DATE} 至 {config.END_DATE}')
    else:
        print(f'时间周期: {config.PERIOD}')
    
    print(f'K线类型: {config.INTERVAL}')
    
    export_formats = []
    if config.EXPORT_CSV:
        export_formats.append('CSV')
    if config.EXPORT_JSON:
        export_formats.append('JSON')
    if config.EXPORT_SQLITE:
        export_formats.append('SQLite')
    if config.EXPORT_MYSQL:
        export_formats.append('MySQL')
    print(f'导出格式: {", ".join(export_formats)}')
    
    print('\n' + '-'*60)
    
    # 创建获取器
    fetcher = StockDataFetcher(config.SYMBOL, verbose=config.VERBOSE)
    
    # 获取数据
    print('\n正在获取数据...')
    df = fetcher.fetch(
        period=config.PERIOD,
        interval=config.INTERVAL,
        start=config.START_DATE,
        end=config.END_DATE
    )
    
    if df is None or df.empty:
        print('[ERROR] 未获取到数据')
        return 1
    
    # 创建输出目录
    output_dir = Path(config.OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)
    
    # 导出数据
    print('\n正在导出数据...')
    success_count = 0
    
    if config.EXPORT_CSV:
        csv_path = config.CSV_FILENAME
        if csv_path is None:
            csv_path = output_dir / f'{config.SYMBOL}_{config.INTERVAL}.csv'
        else:
            csv_path = output_dir / csv_path
        
        if fetcher.save_csv(str(csv_path)):
            success_count += 1
    
    if config.EXPORT_JSON:
        json_path = config.JSON_FILENAME
        if json_path is None:
            json_path = output_dir / f'{config.SYMBOL}_{config.INTERVAL}.json'
        else:
            json_path = output_dir / json_path
        
        if fetcher.save_json(str(json_path)):
            success_count += 1
    
    if config.EXPORT_SQLITE:
        db_path = output_dir / config.SQLITE_DB
        table_name = config.SQLITE_TABLE
        if table_name is None:
            table_name = f'stock_{config.SYMBOL.lower()}'
        
        if fetcher.save_sqlite(str(db_path), table_name):
            success_count += 1
    
    if config.EXPORT_MYSQL:
        if fetcher.save_mysql(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            table_name=config.MYSQL_TABLE
        ):
            success_count += 1
    
    # 显示结果
    print('\n' + '='*60)
    print(f'[OK] 完成！成功导出 {success_count} 项')
    print('='*60)
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\n\n[WARN] 用户中断')
        sys.exit(1)
    except Exception as e:
        print(f'\n[ERROR] 发生错误: {e}')
        sys.exit(1)
