#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CSV文件格式
"""

import sys

# 测试读取CSV文件
csv_files = ['sz301622.csv', 'sz301628.csv']

for csv_file in csv_files:
    print(f'\n{"="*60}')
    print(f'测试文件: {csv_file}')
    print(f'{"="*60}')
    
    # 尝试不同的编码
    encodings = ['gbk', 'gb2312', 'utf-8', 'gb18030']
    
    for encoding in encodings:
        try:
            with open(csv_file, 'r', encoding=encoding) as f:
                lines = f.readlines()[:5]
                print(f'\n使用编码 {encoding} 成功读取:')
                for i, line in enumerate(lines):
                    print(f'第{i+1}行: {line.strip()}')
                break
        except Exception as e:
            print(f'编码 {encoding} 失败: {e}')
            continue
