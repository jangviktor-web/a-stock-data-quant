"""
个股公告/研报/互动易模块
移植自 go-stock (github.com/ArvinLovegood/go-stock) market_news_api.go
数据源：
- 研报: reportapi.eastmoney.com/report/list2
- 公告: np-anotice-stock.eastmoney.com/api/security/ann
- 互动易: irm.cninfo.com.cn/newircs/index/search
"""

import requests
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
}


def _safe_str(val, default='') -> str:
    if val is None:
        return default
    return str(val).strip()


def _normalize_code(stock_code: str) -> str:
    """提取纯数字代码"""
    code = stock_code.replace('sh', '').replace('sz', '').replace('bj', '')
    code = code.replace('gb_', '').replace('us', '').replace('us_', '')
    if '.' in code:
        code = code.split('.')[0]
    return code


def get_research_reports(stock_code: str, days: int = 30, page_size: int = 10) -> List[Dict]:
    """
    获取个股研究报告

    参数:
        stock_code: 股票代码
        days: 最近N天
        page_size: 每页条数

    返回:
        [{'title': 研报标题, 'org': 机构, 'date': 日期, 'rating': 评级,
          'author': 作者, 'info_code': 研报编码}, ...]
    """
    code = _normalize_code(stock_code)
    begin_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    url = "https://reportapi.eastmoney.com/report/list2"
    headers = {
        **_HEADERS,
        'Host': 'reportapi.eastmoney.com',
        'Origin': 'https://data.eastmoney.com',
        'Referer': 'https://data.eastmoney.com/report/stock.jshtml',
        'Content-Type': 'application/json',
    }

    payload = {
        'code': code,
        'industryCode': '*',
        'beginTime': begin_date,
        'endTime': end_date,
        'pageNo': 1,
        'pageSize': page_size,
        'p': 1,
        'pageNum': 1,
        'pageNumber': 1,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] 获取研报失败: {e}")
        return []

    hits = data.get('data', [])
    results = []

    for item in hits:
        results.append({
            'title': _safe_str(item.get('title')),
            'org': _safe_str(item.get('orgSName')),
            'date': _safe_str(item.get('publishDate'))[:10],
            'rating': _safe_str(item.get('ratingName')),
            'author': _safe_str(item.get('researcher')),
            'info_code': _safe_str(item.get('infoCode')),
            'industry': _safe_str(item.get('industryName')),
        })

    return results


def get_stock_notices(stock_code: str, page_size: int = 20) -> List[Dict]:
    """
    获取上市公司公告

    参数:
        stock_code: 股票代码（支持多只，逗号分隔）
        page_size: 每页条数

    返回:
        [{'title': 公告标题, 'date': 公告日期, 'type': 公告类型}, ...]
    """
    codes = [_normalize_code(c) for c in stock_code.split(',')]
    stock_list = ','.join(codes)

    url = "https://np-anotice-stock.eastmoney.com/api/security/ann"
    params = {
        'page_size': str(page_size),
        'page_index': '1',
        'ann_type': 'SHA,CYB,SZA,BJA,INV',
        'client_source': 'web',
        'f_node': '0',
        'stock_list': stock_list,
    }
    headers = {
        **_HEADERS,
        'Host': 'np-anotice-stock.eastmoney.com',
        'Referer': 'https://data.eastmoney.com/notices/hsa/5.html',
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] 获取公告失败: {e}")
        return []

    items = data.get('data', {}).get('list', [])
    results = []

    for item in items:
        columns = item.get('columns', [{}])
        col_name = columns[0].get('column_name', '') if columns else ''

        results.append({
            'title': _safe_str(item.get('title')),
            'date': _safe_str(item.get('notice_date'))[:10],
            'type': col_name,
            'art_code': _safe_str(item.get('art_code')),
        })

    return results


def get_interactive_answers(keyword: str = '', page: int = 1, page_size: int = 20) -> List[Dict]:
    """
    获取互动易数据（投资者互动平台）

    参数:
        keyword: 搜索关键词（股票代码或公司名）
        page: 页码
        page_size: 每页条数

    返回:
        [{'question': 问题, 'answer': 回答, 'company': 公司, 'date': 日期}, ...]
    """
    url = f"https://irm.cninfo.com.cn/newircs/index/search?_t={int(time.time())}"
    headers = {
        **_HEADERS,
        'Host': 'irm.cninfo.com.cn',
        'Origin': 'https://irm.cninfo.com.cn',
        'Referer': 'https://irm.cninfo.com.cn/views/interactiveAnswer',
        'handleError': 'true',
    }
    form_data = {
        'pageNo': str(page),
        'pageSize': str(page_size),
        'searchTypes': '11',
        'highLight': 'true',
        'keyWord': keyword,
    }

    try:
        resp = requests.post(url, data=form_data, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] 获取互动易数据失败: {e}")
        return []

    rows = data.get('results', [])
    results = []

    for item in rows:
        results.append({
            'question': _safe_str(item.get('mainContent')),
            'answer': _safe_str(item.get('attachedContent')),
            'company': _safe_str(item.get('companyShortName')),
            'code': _safe_str(item.get('stockCode')),
            'date': _safe_str(item.get('pubDate'))[:10],
            'answer_date': _safe_str(item.get('attachedPubDate'))[:10],
        })

    return results


def format_research_reports(results: List[Dict], stock_code: str) -> str:
    """格式化研报输出"""
    if not results:
        return f"未获取到 {stock_code} 的研究报告"

    lines = [
        "=" * 75,
        f"  个股研究报告: {stock_code} (最近{len(results)}篇)",
        "=" * 75,
    ]

    for i, item in enumerate(results, 1):
        rating = item.get('rating', '')
        rating_str = f" [{rating}]" if rating else ""
        lines.append(f"\n  {i}. {item.get('title', 'N/A')}{rating_str}")
        lines.append(f"     {item.get('org', 'N/A')} | {item.get('author', 'N/A')} | {item.get('date', 'N/A')}")

    lines.append("\n" + "=" * 75)
    return "\n".join(lines)


def format_stock_notices(results: List[Dict], stock_code: str) -> str:
    """格式化公告输出"""
    if not results:
        return f"未获取到 {stock_code} 的公告"

    lines = [
        "=" * 75,
        f"  上市公司公告: {stock_code}",
        "=" * 75,
        f"  {'日期':<12} {'类型':<10} {'公告标题'}",
        "-" * 75,
    ]

    for item in results:
        lines.append(f"  {item.get('date', 'N/A'):<12} {item.get('type', 'N/A'):<10} {item.get('title', 'N/A')}")

    lines.append("=" * 75)
    return "\n".join(lines)


def format_interactive_answers(results: List[Dict], keyword: str) -> str:
    """格式化互动易输出"""
    if not results:
        return f"未获取到互动易数据 (关键词: {keyword})"

    lines = [
        "=" * 75,
        f"  互动易数据 (关键词: {keyword})",
        "=" * 75,
    ]

    for i, item in enumerate(results, 1):
        q = item.get('question', '')
        a = item.get('answer', '')
        if len(q) > 100:
            q = q[:100] + "..."
        if len(a) > 150:
            a = a[:150] + "..."

        lines.append(f"\n  {i}. [{item.get('company', 'N/A')}] {item.get('date', 'N/A')}")
        lines.append(f"     问: {q}")
        lines.append(f"     答: {a}")

    lines.append("\n" + "=" * 75)
    return "\n".join(lines)
