"""
同花顺北向资金数据备用源

无认证，返回 JSON 格式
"""

import requests
from datetime import datetime, timedelta


_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://data.10jqka.com.cn/',
}
_PROXIES = {'http': None, 'https': None}


def get_north_flow(symbol='沪股通', days=10):
    """
    同花顺北向资金

    Parameters
    ----------
    symbol : str - '沪股通' 或 '深股通'
    days : int - 获取天数

    Returns
    -------
    list of dict: [{'date': ..., 'net_buy': ..., 'fund_flow': ..., 'leader': ''}]
    """
    symbol_map = {'沪股通': 'hgt', '深股通': 'sgt'}
    code = symbol_map.get(symbol, 'hgt')

    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days + 10)).strftime('%Y-%m-%d')

    url = (
        f"https://data.hexin.cn/market/hsgtApi/method/dayChart/"
        f"?token=&param={code}&start={start_date}&end={end_date}"
    )
    s = requests.Session()
    s.trust_env = False
    r = s.get(url, headers=_HEADERS, timeout=15)
    data = r.json()

    items = data.get(code, []) or []
    rows = []
    for item in items[-days:]:
        rows.append({
            'date': item.get('date', ''),
            'net_buy': float(item.get('value', 0) or 0),
            'fund_flow': 0,
            'leader': '',
        })

    return rows
