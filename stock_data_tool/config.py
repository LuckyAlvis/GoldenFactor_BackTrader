#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件

在这里修改股票代码、时间段、K线类型和导出格式
"""

# ==================== 股票配置 ====================

# 股票代码（支持任意市场）
# 美股示例：AAPL, TSLA, MSFT, GOOGL
# A股示例：000001.SZ, 600000.SS, 000858.SZ
SYMBOL = 'TSLA'

# ==================== 时间配置 ====================

# 方式1：使用预设周期
# 可选值：1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
PERIOD = '1y'

# 方式2：使用自定义日期范围（如果设置，将覆盖PERIOD）
# 格式：YYYY-MM-DD
START_DATE = None  # 例如：'2024-01-01'
END_DATE = None    # 例如：'2024-12-31'

# ==================== K线类型 ====================

# K线类型
# 可选值：1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
# 注意：分钟级数据仅支持最近7天
INTERVAL = '1d'

# ==================== 导出配置 ====================

# 导出格式（可以同时选择多个）
EXPORT_CSV = True       # 导出CSV文件
EXPORT_JSON = True      # 导出JSON文件
EXPORT_SQLITE = False   # 导出到SQLite数据库
EXPORT_MYSQL = True     # 导出到MySQL数据库

# 输出文件配置
OUTPUT_DIR = 'output'           # 输出目录
CSV_FILENAME = None              # CSV文件名（None则自动生成）
JSON_FILENAME = None             # JSON文件名（None则自动生成）

# SQLite配置
SQLITE_DB = 'stock_data.db'     # SQLite数据库文件名
SQLITE_TABLE = None              # 表名（None则自动生成）

# MySQL配置
MYSQL_HOST = '101.xx.xxx.xx'    # MySQL主机
MYSQL_PORT = 3307                # MySQL端口
MYSQL_USER = 'root'              # MySQL用户名
MYSQL_PASSWORD = 'xxxxxx'  # MySQL密码 自行更换
MYSQL_DATABASE = 'ry-vue'        # MySQL数据库名
MYSQL_TABLE = 'stock_data'       # MySQL表名

# ==================== 其他配置 ====================

# 是否显示详细信息
VERBOSE = True
