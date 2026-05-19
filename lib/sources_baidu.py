"""
百度财经 API 备用数据源

K线数据、资金流向、概念板块
无认证，纯 HTTP 请求
"""

import requests
import pandas as pd
from datetime import datetime


_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://gushitong.baidu.com/',
}


def _to_pure_code(code):
    """sh600519 → 600519"""
    return code.replace('sh', '').replace('sz', '').replace('SH', '').replace('SZ', '')


def get_kline(code, count=100, fqtype=1):
    """
    百度财经K线数据

    Parameters
    ----------
    code : str - 股票代码 (sh600519 或 600519)
    count : int - 数据条数
    fqtype : int - 1=前复权, 2=后复权, 3=不复权

    Returns
    -------
    DataFrame with columns: open, close, high, low, volume
    """
    pure_code = _to_pure_code(code)
    url = (
        f"https://finance.pae.baidu.com/selfselect/getstockquotation"
        f"?code={pure_code}&market=ab&is498=1&isBk=false&isBlock=false"
        f"&isFutures=false&isStock=true&newFormat=1&count={count}&fqtype={fqtype}"
    )
    r = requests.get(url, headers=_HEADERS, timeout=10,
                     proxies={'http': None, 'https': None})
    data = r.json()

    result = data.get('Result', []) or data.get('result', []) or []
    if not result:
        raise RuntimeError("百度K线: 无数据")

    # 解析分号分隔数据
    # 格式: 日期;开;收;高;低;成交量;成交额;振幅;涨跌幅;涨跌额;换手率;ma5;ma10;ma20
    rows = []
    for item in result:
        parts = item.split(';') if isinstance(item, str) else []
        if len(parts) >= 6:
            rows.append({
                'time': parts[0],
                'open': float(parts[1]),
                'close': float(parts[2]),
                'high': float(parts[3]),
                'low': float(parts[4]),
                'volume': float(parts[5]),
            })

    if not rows:
        raise RuntimeError("百度K线: 解析失败")

    df = pd.DataFrame(rows)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    df.index.name = ''
    return df


def get_fund_flow(code, market='ab'):
    """
    百度分钟级资金流向

    Returns
    -------
    dict: {'rows': [...], 'summary': {...}}
    """
    pure_code = _to_pure_code(code)
    today = datetime.now().strftime('%Y-%m-%d')
    url = (
        f"https://finance.pae.baidu.com/vapi/v1/fundflow"
        f"?code={pure_code}&market={market}&date={today}&finClientType=pc"
    )
    r = requests.get(url, headers=_HEADERS, timeout=10,
                     proxies={'http': None, 'https': None})
    data = r.json()

    result = data.get('result', {}) or {}
    stock_list = result.get('stockList', []) or []

    rows = []
    total_in = 0
    total_out = 0

    for item in stock_list:
        name = item.get('name', '')
        chg_pct = float(item.get('rate', 0) or 0)
        main_in = float(item.get('superLargeIncome', 0) or 0)
        main_out = float(item.get('superLargePay', 0) or 0)
        main_net = main_in - main_out
        total_in += main_in
        total_out += main_out

        rows.append({
            'name': name,
            'chg_pct': chg_pct,
            'main_in': main_in,
            'main_out': main_out,
            'main_net': main_net,
        })

    summary = {
        'total_in': total_in,
        'total_out': total_out,
        'total_net': total_in - total_out,
    }

    return {'rows': rows, 'summary': summary}


def get_concept_blocks(code):
    """
    百度概念板块关联

    Returns
    -------
    list of dict: [{'name': ..., 'code': ..., 'chg_pct': ...}, ...]
    """
    pure_code = _to_pure_code(code)
    url = (
        f"https://finance.pae.baidu.com/api/getrelatedblock"
        f"?code={pure_code}&market=ab&typeCode=all&finClientType=pc"
    )
    r = requests.get(url, headers=_HEADERS, timeout=10,
                     proxies={'http': None, 'https': None})
    data = r.json()

    result = data.get('result', {}) or {}
    blocks = result.get('blockList', []) or []

    rows = []
    for item in blocks:
        rows.append({
            'name': item.get('blockName', ''),
            'code': item.get('blockCode', ''),
            'chg_pct': float(item.get('rate', 0) or 0),
        })

    return rows
