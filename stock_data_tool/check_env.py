#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境检查脚本

用于检查Python环境和依赖包是否正确配置
"""

import sys

def check_python_version():
    """
    检查Python版本
    
    @return 是否符合要求
    """
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    print(f"Python路径: {sys.executable}")
    
    if version.major == 3 and version.minor >= 8:
        print("[OK] Python版本符合要求 (>=3.8)")
        return True
    else:
        print("[ERROR] Python版本过低，需要3.8+")
        return False


def check_packages():
    """
    检查依赖包
    
    @return 是否全部安装
    """
    packages = {
        'yfinance': 'yfinance',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'pymysql': 'pymysql'
    }
    
    all_ok = True
    for name, import_name in packages.items():
        try:
            module = __import__(import_name)
            version = getattr(module, '__version__', 'unknown')
            
            # 检查numpy版本
            if name == 'numpy':
                major = int(version.split('.')[0])
                if major >= 2:
                    print(f"[WARN] {name}: {version} (建议使用1.x版本)")
                    print(f"       运行: pip install 'numpy<2' --upgrade")
                    all_ok = False
                else:
                    print(f"[OK] {name}: {version}")
            else:
                print(f"[OK] {name}: {version}")
                
        except ImportError:
            print(f"[ERROR] {name}: 未安装")
            print(f"        运行: pip install {name}")
            all_ok = False
    
    return all_ok


def test_yfinance():
    """
    测试yfinance连接
    
    @return 是否成功
    """
    try:
        import yfinance as yf
        print("正在测试yfinance连接...")
        ticker = yf.Ticker('AAPL')
        info = ticker.info
        
        if info and 'longName' in info:
            print(f"[OK] yfinance连接成功")
            print(f"     测试股票: {info.get('longName', 'N/A')}")
            return True
        else:
            print("[WARN] yfinance连接成功但数据不完整")
            return True
    except Exception as e:
        print(f"[ERROR] yfinance测试失败: {e}")
        return False


def test_mysql_connection():
    """
    测试MySQL连接（可选）
    
    @return 是否成功
    """
    try:
        import pymysql
        print("正在测试MySQL连接...")
        
        # 这里使用你的数据库配置
        conn = pymysql.connect(
            host='101.37.164.75',
            port=3307,
            user='root',
            password='Cd40k1SKIXBQ',
            database='ry-vue',
            connect_timeout=5
        )
        conn.close()
        print("[OK] MySQL连接成功")
        return True
    except Exception as e:
        print(f"[WARN] MySQL连接失败: {e}")
        print("       如果不使用MySQL功能，可以忽略此警告")
        return False


def check_encoding():
    """
    检查编码设置
    
    @return 是否正确
    """
    import locale
    
    encoding = sys.stdout.encoding
    locale_encoding = locale.getpreferredencoding()
    
    print(f"标准输出编码: {encoding}")
    print(f"系统默认编码: {locale_encoding}")
    
    if encoding.lower() in ['utf-8', 'utf8']:
        print("[OK] 编码设置正确")
        return True
    else:
        print(f"[WARN] 编码为{encoding}，可能在Windows上遇到问题")
        print("       已将emoji替换为ASCII字符，应该不影响使用")
        return True


def main():
    """主函数"""
    print("="*70)
    print("美股数据获取器 - 环境检查")
    print("="*70)
    
    results = {}
    
    # 1. 检查Python版本
    print("\n[1/5] 检查Python版本...")
    print("-"*70)
    results['python'] = check_python_version()
    
    # 2. 检查依赖包
    print("\n[2/5] 检查依赖包...")
    print("-"*70)
    results['packages'] = check_packages()
    
    # 3. 检查编码
    print("\n[3/5] 检查编码设置...")
    print("-"*70)
    results['encoding'] = check_encoding()
    
    # 4. 测试yfinance
    print("\n[4/5] 测试yfinance...")
    print("-"*70)
    results['yfinance'] = test_yfinance()
    
    # 5. 测试MySQL（可选）
    print("\n[5/5] 测试MySQL连接（可选）...")
    print("-"*70)
    results['mysql'] = test_mysql_connection()
    
    # 总结
    print("\n" + "="*70)
    print("检查结果总结")
    print("="*70)
    
    required_checks = ['python', 'packages', 'yfinance']
    optional_checks = ['encoding', 'mysql']
    
    required_ok = all(results.get(k, False) for k in required_checks)
    
    print("\n必需项:")
    for key in required_checks:
        status = "[OK]" if results.get(key, False) else "[ERROR]"
        print(f"  {status} {key}")
    
    print("\n可选项:")
    for key in optional_checks:
        status = "[OK]" if results.get(key, False) else "[WARN]"
        print(f"  {status} {key}")
    
    print("\n" + "="*70)
    if required_ok:
        print("[SUCCESS] 环境配置正确，可以运行项目！")
        print("\n快速开始:")
        print("  python3 auto_save_tesla_to_mysql.py  # 保存特斯拉数据到MySQL")
        print("  python3 us_stock_examples.py         # 运行示例程序")
    else:
        print("[ERROR] 环境配置有问题，请按照上面的提示修复")
        print("\n常见解决方案:")
        print("  pip3 install yfinance pandas pymysql 'numpy<2'")
    print("="*70)


if __name__ == '__main__':
    main()
