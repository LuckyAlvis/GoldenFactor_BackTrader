#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV数据加载器 - 统一处理不同来源的CSV格式

支持的数据源：
1. 邢不行整理的A股数据（中文列名，GBK编码）
2. yfinance获取的美股数据（英文列名，UTF-8编码）
3. 其他标准格式的股票数据

功能：
- 自动识别编码格式
- 统一列名映射
- 数据清洗和验证
- 返回标准化的DataFrame
"""

import pandas as pd
import os
from datetime import datetime


class CSVDataLoader:
    """
    CSV数据加载器类
    
    统一处理不同来源和格式的CSV文件
    """
    
    # 列名映射字典 - 将不同来源的列名映射到标准列名
    COLUMN_MAPPING = {
        # A股数据（邢不行格式）
        '股票代码': 'symbol',
        '股票名称': 'name',
        '交易日期': 'date',
        '开盘价': 'open',
        '最高价': 'high',
        '最低价': 'low',
        '收盘价': 'close',
        '前收盘价': 'pre_close',
        '成交量': 'volume',
        '成交额': 'amount',
        '流通市值': 'float_market_cap',
        '总市值': 'total_market_cap',
        
        # 美股数据（yfinance格式）
        'Symbol': 'symbol',
        'Date': 'date',
        'Datetime': 'date',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume',
        'Dividends': 'dividends',
        'Stock Splits': 'stock_splits',
        
        # 通用格式
        'symbol': 'symbol',
        'date': 'date',
        'datetime': 'date',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'volume',
    }
    
    # 必需的列
    REQUIRED_COLUMNS = ['date', 'open', 'high', 'low', 'close', 'volume']
    
    @staticmethod
    def detect_encoding(file_path):
        """
        检测文件编码
        
        @param file_path 文件路径
        @return 编码格式
        """
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read()
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        return 'utf-8'  # 默认返回utf-8
    
    @staticmethod
    def detect_skip_rows(file_path, encoding='utf-8'):
        """
        检测需要跳过的行数（通常是说明文字）
        
        @param file_path 文件路径
        @param encoding 编码格式
        @return 需要跳过的行数
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                first_line = f.readline().strip()
                
                # 如果第一行包含"邢不行"或其他说明文字，跳过
                if '邢不行' in first_line or '说明' in first_line or '数据' in first_line:
                    return 1
        except Exception:
            pass
        
        return 0
    
    @staticmethod
    def standardize_columns(df):
        """
        标准化列名
        
        @param df 原始DataFrame
        @return 标准化后的DataFrame
        """
        # 创建列名映射
        rename_dict = {}
        for col in df.columns:
            if col in CSVDataLoader.COLUMN_MAPPING:
                rename_dict[col] = CSVDataLoader.COLUMN_MAPPING[col]
        
        # 重命名列
        df = df.rename(columns=rename_dict)
        
        return df
    
    @staticmethod
    def parse_date(df):
        """
        解析日期列
        
        @param df DataFrame
        @return 处理后的DataFrame
        """
        if 'date' not in df.columns:
            raise ValueError('缺少日期列')
        
        # 转换为datetime类型
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # 移除时区信息（如果有）
        try:
            if hasattr(df['date'].dtype, 'tz') and df['date'].dt.tz is not None:
                df['date'] = df['date'].dt.tz_localize(None)
        except (AttributeError, TypeError):
            # 如果已经是无时区的datetime，跳过
            pass
        
        return df
    
    @staticmethod
    def validate_data(df):
        """
        验证数据完整性
        
        @param df DataFrame
        @return 是否有效
        """
        # 检查必需列
        missing_cols = [col for col in CSVDataLoader.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f'缺少必需列: {missing_cols}')
        
        # 检查数据是否为空
        if df.empty:
            raise ValueError('数据为空')
        
        # 检查价格和成交量是否为正数
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if (df[col] <= 0).any():
                print(f'[WARN]  警告: {col}列存在非正数值')
        
        return True
    
    @staticmethod
    def clean_data(df):
        """
        清洗数据
        
        @param df DataFrame
        @return 清洗后的DataFrame
        """
        # 删除重复行
        df = df.drop_duplicates(subset=['date'], keep='last')
        
        # 按日期排序
        df = df.sort_values('date').reset_index(drop=True)
        
        # 删除缺失值
        df = df.dropna(subset=CSVDataLoader.REQUIRED_COLUMNS)
        
        return df
    
    @staticmethod
    def load_csv(file_path, encoding=None, skiprows=None, verbose=True):
        """
        加载CSV文件（主方法）
        
        @param file_path CSV文件路径
        @param encoding 编码格式（None表示自动检测）
        @param skiprows 跳过的行数（None表示自动检测）
        @param verbose 是否显示详细信息
        @return 标准化的DataFrame
        """
        if verbose:
            print(f'正在加载CSV文件: {file_path}')
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'文件不存在: {file_path}')
        
        # 自动检测编码
        if encoding is None:
            encoding = CSVDataLoader.detect_encoding(file_path)
            if verbose:
                print(f'检测到编码: {encoding}')
        
        # 自动检测跳过行数
        if skiprows is None:
            skiprows = CSVDataLoader.detect_skip_rows(file_path, encoding)
            if skiprows > 0 and verbose:
                print(f'跳过前 {skiprows} 行')
        
        # 读取CSV
        try:
            df = pd.read_csv(file_path, encoding=encoding, skiprows=skiprows)
        except Exception as e:
            raise Exception(f'读取CSV失败: {e}')
        
        if verbose:
            print(f'原始数据: {len(df)} 行, {len(df.columns)} 列')
            print(f'原始列名: {df.columns.tolist()}')
        
        # 标准化列名
        df = CSVDataLoader.standardize_columns(df)
        
        if verbose:
            print(f'标准化列名: {df.columns.tolist()}')
        
        # 解析日期
        df = CSVDataLoader.parse_date(df)
        
        # 清洗数据
        df = CSVDataLoader.clean_data(df)
        
        # 验证数据
        CSVDataLoader.validate_data(df)
        
        if verbose:
            print(f'[OK] 数据加载成功: {len(df)} 行')
            print(f'日期范围: {df["date"].min()} 至 {df["date"].max()}')
            print(f'\n数据预览:')
            print(df.head())
        
        return df
    
    @staticmethod
    def save_standardized_csv(df, output_path, verbose=True):
        """
        保存标准化的CSV文件
        
        @param df DataFrame
        @param output_path 输出文件路径
        @param verbose 是否显示详细信息
        """
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        if verbose:
            print(f'[OK] 标准化数据已保存到: {output_path}')
    
    @staticmethod
    def convert_to_backtrader_format(df):
        """
        转换为Backtrader所需的格式
        
        @param df 标准化的DataFrame
        @return Backtrader格式的DataFrame
        """
        # 选择必需的列
        bt_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        # 检查列是否存在
        missing = [col for col in bt_columns if col not in df.columns]
        if missing:
            raise ValueError(f'缺少必需列: {missing}')
        
        # 创建新DataFrame
        bt_df = df[bt_columns].copy()
        
        # 重命名为Backtrader期望的列名（首字母大写）
        bt_df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        
        # 设置日期为索引
        bt_df.set_index('Date', inplace=True)
        
        return bt_df


def test_loader():
    """
    测试数据加载器
    """
    print('='*80)
    print('CSV数据加载器测试')
    print('='*80)
    
    # 测试文件列表
    test_files = [
        'sh601668.csv',      # A股数据
        'tsla_data.csv',     # 美股数据
        'sz301622.csv',      # A股数据
    ]
    
    for file_name in test_files:
        if os.path.exists(file_name):
            print(f'\n{"="*80}')
            print(f'测试文件: {file_name}')
            print('='*80)
            
            try:
                # 加载数据
                df = CSVDataLoader.load_csv(file_name, verbose=True)
                
                # 转换为Backtrader格式
                print(f'\n转换为Backtrader格式:')
                bt_df = CSVDataLoader.convert_to_backtrader_format(df)
                print(bt_df.head())
                
                # 保存标准化数据
                output_file = f'standardized_{file_name}'
                CSVDataLoader.save_standardized_csv(df, output_file, verbose=True)
                
            except Exception as e:
                print(f'[ERROR] 加载失败: {e}')
        else:
            print(f'\n[WARN]  文件不存在: {file_name}')


if __name__ == '__main__':
    test_loader()
