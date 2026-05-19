"""
东方财富数据中心 Web API 备用源

Base URL: https://datacenter-web.eastmoney.com/api/data/v1/get
支持: 龙虎榜、融资融券、大宗交易、股东人数、限售解禁、分红
"""

import requests
from datetime import datetime, timedelta


_BASE_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
_HEADERS = {'Referer': 'https://data.eastmoney.com/'}
_PROXIES = {'http': None, 'https': None}


def _dc_get(report_name, filter_str='', sort_columns='UPDATE_DATE',
            page_size=50, page_number=1, extra_params=None):
    """通用 datacenter-web 查询"""
    params = {
        'reportName': report_name,
        'sortColumns': sort_columns,
        'sortTypes': '-1',
        'pageSize': str(page_size),
        'pageNumber': str(page_number),
        'columns': 'ALL',
        'source': 'WEB',
        'client': 'WEB',
    }
    if filter_str:
        params['filter'] = filter_str
    if extra_params:
        params.update(extra_params)

    r = requests.get(_BASE_URL, params=params, headers=_HEADERS,
                     timeout=15, proxies=_PROXIES)
    data = r.json()
    result = data.get('result', {}) or {}
    return result.get('data', []) or []


def get_lhb_data(days=5, limit=30):
    """
    龙虎榜

    Returns
    -------
    list of dict: [{'date': ..., 'code': ..., 'name': ..., 'close': ..., 'chg_pct': ..., 'reason': ..., 'net_buy': ..., 'buy_total': ..., 'sell_total': ...}]
    """
    records = _dc_get('RPT_DAILYBILLBOARD_DETAILSNEW',
                      page_size=limit, sort_columns='TRADE_DATE')

    rows = []
    for r in records:
        rows.append({
            'date': (r.get('TRADE_DATE', '') or '')[:10],
            'code': r.get('SECURITY_CODE', ''),
            'name': r.get('SECURITY_NAME_ABBR', ''),
            'close': float(r.get('CLOSE_PRICE', 0) or 0),
            'chg_pct': float(r.get('CHANGE_RATE', 0) or 0),
            'reason': r.get('EXPLANATION', ''),
            'net_buy': float(r.get('BILLBOARD_NET_AMT', 0) or 0) / 10000,
            'buy_total': float(r.get('BILLBOARD_BUY_AMT', 0) or 0) / 10000,
            'sell_total': float(r.get('BILLBOARD_SELL_AMT', 0) or 0) / 10000,
        })

    return rows


def get_margin_data(days=30):
    """
    融资融券汇总

    Returns
    -------
    list of dict: [{'date': ..., 'rzye': ..., 'rzmre': ..., 'rzche': ..., 'rqye': ..., 'rqmcl': ..., 'rzrqye': ...}]
    """
    end = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    records = _dc_get('RPTA_WEB_RZRQ_GGMX',
                      filter_str=f"(TRADE_DATE>='{start}')(TRADE_DATE<='{end}')",
                      page_size=days, sort_columns='TRADE_DATE')

    # 按日期汇总
    date_map = {}
    for r in records:
        date = (r.get('TRADE_DATE', '') or '')[:10]
        if date not in date_map:
            date_map[date] = {
                'date': date,
                'rzye': 0, 'rzmre': 0, 'rzche': 0,
                'rqye': 0, 'rqmcl': 0, 'rzrqye': 0,
            }
        d = date_map[date]
        d['rzye'] += float(r.get('RZYE', 0) or 0)
        d['rzmre'] += float(r.get('RZMRE', 0) or 0)
        d['rzche'] += float(r.get('RZCHE', 0) or 0)
        d['rqye'] += float(r.get('RQYE', 0) or 0)
        d['rqmcl'] += float(r.get('RQMCL', 0) or 0)
        d['rzrqye'] += float(r.get('RZRQYE', 0) or 0)

    return list(date_map.values())


def get_block_trade(code='', limit=20):
    """
    大宗交易

    Returns
    -------
    list of dict: [{'date': ..., 'code': ..., 'name': ..., 'price': ..., 'vol': ..., 'amount': ..., 'buyer': ..., 'seller': ...}]
    """
    records = _dc_get('RPT_DATA_OCCURTRADE', page_size=limit, sort_columns='TRADE_DATE')

    rows = []
    for r in records:
        stock_code = r.get('SECURITY_CODE', '')
        if code and stock_code != code:
            continue
        rows.append({
            'date': (r.get('TRADE_DATE', '') or '')[:10],
            'code': stock_code,
            'name': r.get('SECURITY_NAME_ABBR', ''),
            'price': float(r.get('DEAL_PRICE', 0) or 0),
            'vol': float(r.get('DEAL_VOLUME', 0) or 0),
            'amount': float(r.get('DEAL_AMOUNT', 0) or 0),
            'buyer': r.get('BUYER_NAME', ''),
            'seller': r.get('SELLER_NAME', ''),
        })

    return rows


def get_holder_num(code):
    """
    股东人数

    Returns
    -------
    list of dict: [{'date': ..., 'holder_num': ..., 'change': ..., 'change_pct': ...}]
    """
    records = _dc_get('RPT_HOLDERNUMLATEST',
                      filter_str=f"(SECURITY_CODE=\"{code}\")",
                      page_size=10, sort_columns='END_DATE')

    rows = []
    prev_num = None
    for r in records:
        num = float(r.get('HOLDER_NUM', 0) or 0)
        change = num - prev_num if prev_num else 0
        change_pct = round(change / prev_num * 100, 2) if prev_num else 0
        rows.append({
            'date': (r.get('END_DATE', '') or '')[:10],
            'holder_num': int(num),
            'change': int(change),
            'change_pct': change_pct,
        })
        prev_num = num

    return rows


def get_locked_shares(code='', limit=20):
    """
    限售解禁

    Returns
    -------
    list of dict: [{'date': ..., 'code': ..., 'name': ..., 'count': ..., 'market_value': ...}]
    """
    records = _dc_get('RPT_LIFT_STAGE', page_size=limit, sort_columns='FREE_DATE')

    rows = []
    for r in records:
        stock_code = r.get('SECURITY_CODE', '')
        if code and stock_code != code:
            continue
        rows.append({
            'date': (r.get('FREE_DATE', '') or '')[:10],
            'code': stock_code,
            'name': r.get('SECURITY_NAME_ABBR', ''),
            'count': float(r.get('FREE_NUM', 0) or 0),
            'market_value': float(r.get('MARKET_CAP', 0) or 0),
        })

    return rows


def get_margin_detail(code, market='sh', days=10):
    """
    个股融资融券明细

    Returns
    -------
    list of dict: [{'date': ..., 'rzye': ..., 'rzmre': ..., 'rzche': ..., 'rqye': ..., 'rqmcl': ...}]
    """
    end = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=days * 2)).strftime('%Y-%m-%d')
    records = _dc_get('RPTA_WEB_RZRQ_GGMX',
                      filter_str=f"(SCODE=\"{code}\")(TRADE_DATE>='{start}')(TRADE_DATE<='{end}')",
                      page_size=days, sort_columns='TRADE_DATE')

    rows = []
    for r in records:
        rows.append({
            'date': (r.get('TRADE_DATE', '') or '')[:10],
            'rzye': float(r.get('RZYE', 0) or 0),
            'rzmre': float(r.get('RZMRE', 0) or 0),
            'rzche': float(r.get('RZCHE', 0) or 0),
            'rqye': float(r.get('RQYE', 0) or 0),
            'rqmcl': float(r.get('RQMCL', 0) or 0),
        })

    return rows


def get_macro_data(indicator='cpi'):
    """
    宏观经济数据 (通过 datacenter-web 获取)

    Returns
    -------
    dict: {'indicator': ..., 'data': [...]}
    """
    # datacenter-web 没有直接的宏观数据接口
    # 这里作为占位，实际宏观数据仍以 akshare 为主
    raise RuntimeError("datacenter-web 暂不支持宏观数据")
