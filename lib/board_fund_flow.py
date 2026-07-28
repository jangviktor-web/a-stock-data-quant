"""
板块/概念资金流向模块
移植自 go-stock (github.com/ArvinLovegood/go-stock) bk_fund_flow_api.go / concept_fund_flow_api.go
数据源：东方财富 data.eastmoney.com/dataapi/bkzj

功能：
- 行业板块资金流排名（实时）
- 概念板块资金流排名（实时）
- 个股资金流历史（日线级别，复用 push2his fflow）
"""

import requests
from typing import List, Dict, Optional

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Referer': 'https://data.eastmoney.com/',
}

# 行业板块资金流
_BK_INDUSTRY_URL = "https://data.eastmoney.com/dataapi/bkzj/getbkzj"
# 概念板块资金流
_BK_CONCEPT_URL = "https://data.eastmoney.com/dataapi/bkzj/getbkzj"


def _safe_float(val, default=0.0) -> float:
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def get_board_fund_flow(board_type: str = 'industry', top_n: int = 20) -> List[Dict]:
    """
    获取板块资金流排名

    参数:
        board_type: 'industry'(行业板块) 或 'concept'(概念板块)
        top_n: 返回前N名

    返回:
        [{'code': 板块代码, 'name': 板块名称, 'net_inflow': 主力净流入(元)}, ...]
    """
    # code参数: m:90+s:4 = 行业板块, m:90+t:3 = 概念板块
    code_param = "m:90+s:4" if board_type == 'industry' else "m:90+t:3"

    params = {
        'key': 'f62',
        'code': code_param,
    }

    try:
        resp = requests.get(_BK_INDUSTRY_URL, params=params, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] 获取板块资金流失败: {e}")
        return []

    if data.get('rc') != 0:
        print(f"  [WARN] 接口返回异常: rc={data.get('rc')}")
        return []

    diff = data.get('data', {}).get('diff', [])
    if not diff:
        return []

    results = []
    for item in diff:
        results.append({
            'code': item.get('f12', ''),
            'name': item.get('f14', ''),
            'net_inflow': _safe_float(item.get('f62')),
            'market': item.get('f13', 0),
        })

    # 按主力净流入排序
    results.sort(key=lambda x: x['net_inflow'], reverse=True)
    return results[:top_n]


def get_industry_fund_flow(top_n: int = 20) -> List[Dict]:
    """获取行业板块资金流排名"""
    return get_board_fund_flow('industry', top_n)


def get_concept_fund_flow(top_n: int = 20) -> List[Dict]:
    """获取概念板块资金流排名"""
    return get_board_fund_flow('concept', top_n)


def format_board_fund_flow(results: List[Dict], board_type: str = 'industry') -> str:
    """格式化板块资金流输出"""
    if not results:
        return "未获取到板块资金流数据"

    title = "行业板块" if board_type == 'industry' else "概念板块"
    lines = [
        "=" * 70,
        f"  {title}资金流排名 (主力净流入)",
        "=" * 70,
        f"  {'排名':<4} {'板块名称':<12} {'代码':<10} {'主力净流入':>14}",
        "-" * 70,
    ]

    for i, item in enumerate(results, 1):
        inflow = item['net_inflow']
        # 转换为亿
        inflow_yi = inflow / 1e8
        sign = "+" if inflow_yi >= 0 else ""
        arrow = "🟢" if inflow_yi >= 0 else "🔴"
        lines.append(f"  {i:<4} {item['name']:<12} {item['code']:<10} {arrow}{sign}{inflow_yi:>10.2f}亿")

    lines.append("=" * 70)

    # 统计
    inflow_count = sum(1 for r in results if r['net_inflow'] > 0)
    outflow_count = len(results) - inflow_count
    total_inflow = sum(r['net_inflow'] for r in results if r['net_inflow'] > 0) / 1e8
    total_outflow = sum(r['net_inflow'] for r in results if r['net_inflow'] < 0) / 1e8

    lines.append(f"  统计: {inflow_count}个流入 / {outflow_count}个流出")
    lines.append(f"  总流入: +{total_inflow:.2f}亿 | 总流出: {total_outflow:.2f}亿")

    return "\n".join(lines)


# ============ 个股资金流历史（复用 push2his fflow） ============

def get_stock_fund_flow_history(stock_code: str, days: int = 30) -> List[Dict]:
    """
    获取个股资金流历史（日线级别）
    使用东方财富 push2his fflow 接口

    参数:
        stock_code: 股票代码（纯数字，如 '600519'）
        days: 获取天数

    返回:
        [{'date': 日期, 'main_net': 主力净额, 'super_large': 超大单, 'large': 大单,
          'medium': 中单, 'small': 小单}, ...]
    """
    # 确定 secid
    code = stock_code.replace('sh', '').replace('sz', '').replace('bj', '')
    if code.startswith(('6', '9')):
        secid = f"1.{code}"
    elif code.startswith(('0', '3')):
        secid = f"0.{code}"
    elif code.startswith(('4', '8')):
        secid = f"0.{code}"
    else:
        secid = f"1.{code}"

    url = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
    params = {
        'lmt': str(days),
        'klt': '101',
        'secid': secid,
        'fields1': 'f1,f2,f3,f7',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65',
    }

    try:
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] 获取资金流历史失败: {e}")
        return []

    klines = data.get('data', {}).get('klines', [])
    if not klines:
        return []

    results = []
    for line in klines:
        parts = line.split(',')
        if len(parts) < 7:
            continue
        results.append({
            'date': parts[0],
            'main_net': _safe_float(parts[1]),       # 主力净额
            'small': _safe_float(parts[2]),          # 小单净额
            'medium': _safe_float(parts[3]),         # 中单净额
            'large': _safe_float(parts[4]),          # 大单净额
            'super_large': _safe_float(parts[5]),    # 超大单净额
        })

    return results


def format_stock_fund_flow_history(results: List[Dict], stock_code: str) -> str:
    """格式化个股资金流历史输出"""
    if not results:
        return f"未获取到 {stock_code} 的资金流历史数据"

    lines = [
        "=" * 75,
        f"  个股资金流历史: {stock_code} (最近{len(results)}个交易日)",
        "=" * 75,
        f"  {'日期':<12} {'主力净额':>12} {'超大单':>12} {'大单':>12} {'中单':>12} {'小单':>12}",
        "-" * 75,
    ]

    total_main = 0
    for item in results:
        main = item['main_net'] / 1e8
        total_main += item['main_net']
        sign = "+" if main >= 0 else ""
        arrow = "🟢" if main >= 0 else "🔴"
        lines.append(
            f"  {item['date']:<12} {arrow}{sign}{main:>9.2f}亿 "
            f"{item['super_large']/1e8:>10.2f}亿 "
            f"{item['large']/1e8:>10.2f}亿 "
            f"{item['medium']/1e8:>10.2f}亿 "
            f"{item['small']/1e8:>10.2f}亿"
        )

    lines.append("-" * 75)
    total_yi = total_main / 1e8
    sign = "+" if total_yi >= 0 else ""
    lines.append(f"  累计主力净流入: {sign}{total_yi:.2f}亿")
    lines.append("=" * 75)

    return "\n".join(lines)
