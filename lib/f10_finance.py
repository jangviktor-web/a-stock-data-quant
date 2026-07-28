"""
F10 财务指标模块
移植自 go-stock (github.com/ArvinLovegood/go-stock) f10_data_api.go
数据源：东方财富 datacenter.eastmoney.com/securities/api/data/v1/get

功能：
- 主要财务指标（营收/净利润/ROE/毛利率等）
- 杜邦分析
- 机构预测（盈利预测）
"""

import requests
from typing import List, Dict, Optional

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0',
    'Referer': 'https://emweb.securities.eastmoney.com/',
    'Origin': 'https://emweb.securities.eastmoney.com',
    'Host': 'datacenter.eastmoney.com',
}

_BASE_URL = "https://datacenter.eastmoney.com/securities/api/data/v1/get"

# 字段中文映射
_FIELD_CN = {
    'SECUCODE': '证券代码',
    'SECURITY_CODE': '股票代码',
    'SECURITY_NAME_ABBR': '股票简称',
    'REPORT_DATE': '报告日期',
    'REPORT_TYPE': '报告类型',
    'EPSJB': '基本每股收益',
    'EPSKCJB': '扣非每股收益',
    'BPS': '每股净资产',
    'MGZBGJ': '每股资本公积',
    'MGWFPLR': '每股未分配利润',
    'MGJYXJJE': '每股经营现金流',
    'TOTAL_OPERATEINCOME': '营业总收入',
    'PARENT_NETPROFIT': '归属净利润',
    'KCFJCXSYJLR': '扣非净利润',
    'ROEJQ': 'ROE(加权)',
    'XSMLL': '销售毛利率',
    'ZCFZL': '资产负债率',
    'TOTALOPERATEREVETZ': '营收同比增长',
    'PARENTNETPROFITTZ': '净利同比增长',
    'KCFJCXSYJLRTZ': '扣非净利同比增长',
    'TOTAL_SHARE': '总股本',
    'FREE_SHARE': '流通股',
    'GROSS_PROFIT_RATIO': '毛利率',
    'NET_PROFIT_RATIO': '净利率',
    'ROE_DILUTED': 'ROE(摊薄)',
    'JROA': '总资产净利率',
}


def _safe_float(val, default=None):
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _normalize_code(stock_code: str) -> str:
    """转换为东财datacenter格式: 600519.SH"""
    code = stock_code.replace('sh', '').replace('sz', '').replace('bj', '')
    if '.' in code:
        return code
    if code.startswith(('6', '9')):
        return f"{code}.SH"
    elif code.startswith(('0', '3')):
        return f"{code}.SZ"
    elif code.startswith(('4', '8')):
        return f"{code}.BJ"
    elif code.startswith('5'):
        return f"{code}.SH"
    return f"{code}.SZ"


def _f10_request(report_name: str, secucode: str, page_size: int = 5,
                 columns: str = 'ALL', sort_columns: str = 'REPORT_DATE',
                 sort_types: str = '-1') -> List[Dict]:
    """通用F10请求"""
    params = {
        'reportName': report_name,
        'columns': columns,
        'filter': f'(SECUCODE="{secucode}")',
        'pageSize': str(page_size),
        'sortColumns': sort_columns,
        'sortTypes': sort_types,
        'source': 'HSF10',
        'client': 'PC',
    }

    try:
        resp = requests.get(_BASE_URL, params=params, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] F10请求失败: {e}")
        return []

    if not data.get('success'):
        return []

    result = data.get('result', {})
    return result.get('data', []) or []


def get_main_finance(stock_code: str, periods: int = 5) -> List[Dict]:
    """
    获取主要财务指标

    参数:
        stock_code: 股票代码（如 '600519' 或 'sh600519'）
        periods: 获取最近几期

    返回:
        [{'report_date': 报告日期, 'eps': 每股收益, 'bps': 每股净资产,
          'revenue': 营业总收入, 'net_profit': 归属净利润, 'roe': ROE,
          'gross_margin': 毛利率, 'debt_ratio': 资产负债率,
          'revenue_yoy': 营收同比增长, 'profit_yoy': 净利同比增长}, ...]
    """
    secucode = _normalize_code(stock_code)
    data = _f10_request('RPT_F10_FINANCE_MAINFINADATA', secucode, page_size=periods)

    results = []
    for item in data:
        results.append({
            'report_date': item.get('REPORT_DATE', '')[:10],
            'eps': _safe_float(item.get('EPSJB')),
            'eps_deducted': _safe_float(item.get('EPSKCJB')),
            'bps': _safe_float(item.get('BPS')),
            'revenue': _safe_float(item.get('TOTALOPERATEREVE')),
            'net_profit': _safe_float(item.get('PARENTNETPROFIT')),
            'net_profit_deducted': _safe_float(item.get('KCFJCXSYJLR')),
            'roe': _safe_float(item.get('ROEJQ')),
            'gross_margin': _safe_float(item.get('XSMLL')),
            'debt_ratio': _safe_float(item.get('ZCFZL')),
            'revenue_yoy': _safe_float(item.get('TOTALOPERATEREVETZ')),
            'profit_yoy': _safe_float(item.get('PARENTNETPROFITTZ')),
            'profit_yoy_deducted': _safe_float(item.get('KCFJCXSYJLRTZ')),
            'total_shares': _safe_float(item.get('TOTAL_SHARE')),
            'free_shares': _safe_float(item.get('FREE_SHARE')),
        })

    return results


def get_forecast(stock_code: str) -> List[Dict]:
    """
    获取机构盈利预测

    返回:
        [{'year': 预测年份, 'eps': 预测每股收益, 'pe': 预测市盈率}, ...]
    """
    secucode = _normalize_code(stock_code)
    data = _f10_request('RPT_F10_FINANCE_FORECAST', secucode, page_size=3,
                        sort_columns='REPORT_DATE', sort_types='-1')

    results = []
    for item in data:
        results.append({
            'report_date': item.get('REPORT_DATE', '')[:10],
            'year1': item.get('YEAR1'),
            'eps1': _safe_float(item.get('EPS1')),
            'pe1': _safe_float(item.get('PE1')),
            'year2': item.get('YEAR2'),
            'eps2': _safe_float(item.get('EPS2')),
            'pe2': _safe_float(item.get('PE2')),
            'year3': item.get('YEAR3'),
            'eps3': _safe_float(item.get('EPS3')),
            'pe3': _safe_float(item.get('PE3')),
        })

    return results


def format_main_finance(results: List[Dict], stock_code: str) -> str:
    """格式化主要财务指标输出"""
    if not results:
        return f"未获取到 {stock_code} 的财务数据"

    lines = [
        "=" * 80,
        f"  F10 主要财务指标: {stock_code}",
        "=" * 80,
    ]

    for item in results:
        rev = item.get('revenue')
        profit = item.get('net_profit')
        rev_str = f"{rev/1e8:.2f}亿" if rev is not None else "N/A"
        profit_str = f"{profit/1e8:.2f}亿" if profit is not None else "N/A"

        def _r(v, nd=2):
            return round(v, nd) if v is not None else 'N/A'

        lines.append(f"\n  📅 {item.get('report_date', 'N/A')}")
        lines.append(f"    每股收益: {_r(item.get('eps'))} 元 | 扣非: {_r(item.get('eps_deducted'))} 元")
        lines.append(f"    每股净资产: {_r(item.get('bps'))} 元")
        lines.append(f"    营业总收入: {rev_str} | 归属净利润: {profit_str}")
        lines.append(f"    ROE(加权): {_r(item.get('roe'))}% | 毛利率: {_r(item.get('gross_margin'))}%")
        lines.append(f"    资产负债率: {_r(item.get('debt_ratio'))}%")
        lines.append(f"    营收同比: {_r(item.get('revenue_yoy'))}% | 净利同比: {_r(item.get('profit_yoy'))}%")

    lines.append("\n" + "=" * 80)
    return "\n".join(lines)


def format_forecast(results: List[Dict], stock_code: str) -> str:
    """格式化机构预测输出"""
    if not results:
        return f"未获取到 {stock_code} 的机构预测数据"

    lines = [
        "=" * 60,
        f"  机构盈利预测: {stock_code}",
        "=" * 60,
    ]

    for item in results:
        lines.append(f"\n  📅 预测日期: {item.get('report_date', 'N/A')}")
        for i in [1, 2, 3]:
            year = item.get(f'year{i}')
            eps = item.get(f'eps{i}')
            pe = item.get(f'pe{i}')
            if year and eps:
                lines.append(f"    {year}年: 预测EPS {eps:.2f}元, 预测PE {pe:.1f}" if pe else f"    {year}年: 预测EPS {eps:.2f}元")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)
