"""
mootdx 备用数据源 — 通达信 TCP 7709 协议

无认证，无 IP 限制，适合做备用
依赖: pip install mootdx
"""

import pandas as pd

_client = None


def _get_client():
    global _client
    if _client is None:
        from mootdx.quotes import Quotes
        _client = Quotes.factory(market='std')
    return _client


def _to_pure_code(code):
    """sh600519 → 600519"""
    return code.replace('sh', '').replace('sz', '').replace('SH', '').replace('SZ', '')


def _to_market(code):
    """判断市场: 0=深圳, 1=上海"""
    pure = _to_pure_code(code)
    if pure.startswith(('6', '9', '5')):
        return 1  # 上海
    return 0  # 深圳


def get_realtime(codes):
    """
    mootdx 实时行情

    Returns
    -------
    list of dict: [{'code': 'SH600519', 'name': '贵州茅台', 'now': 1800.0, ...}]
    """
    client = _get_client()
    pure_codes = [_to_pure_code(c) for c in codes]

    results = []
    for code in pure_codes:
        market = _to_market(code)
        df = client.quotes(symbol=[code], market=market)
        if df is not None and len(df) > 0:
            row = df.iloc[0]
            results.append({
                'code': ('SH' if market == 1 else 'SZ') + code,
                'name': str(row.get('name', '')),
                'now': float(row.get('price', 0) or 0),
                'open': float(row.get('open', 0) or 0),
                'high': float(row.get('high', 0) or 0),
                'low': float(row.get('low', 0) or 0),
                'close': float(row.get('last_close', 0) or 0),
                'volume': float(row.get('vol', 0) or 0),
                'amount': float(row.get('amount', 0) or 0),
                'change': float(row.get('price', 0) or 0) - float(row.get('last_close', 0) or 0),
                'change_pct': round(
                    (float(row.get('price', 0) or 0) / float(row.get('last_close', 1) or 1) - 1) * 100, 2
                ) if float(row.get('last_close', 0) or 0) > 0 else 0,
            })

    return results


def get_kline(code, frequency=9, offset=100):
    """
    mootdx K线数据

    Parameters
    ----------
    code : str - 股票代码
    frequency : int - 0=5m, 1=15m, 2=30m, 3=60m, 9=日线
    offset : int - 数据条数

    Returns
    -------
    DataFrame with columns: open, close, high, low, volume
    """
    client = _get_client()
    pure_code = _to_pure_code(code)
    market = _to_market(code)

    df = client.bars(symbol=pure_code, frequency=frequency, offset=offset, market=market)
    if df is None or len(df) == 0:
        raise RuntimeError(f"mootdx K线: 无数据 ({code})")

    # mootdx 返回列: open, close, high, low, vol, amount, datetime
    result = pd.DataFrame()
    result['open'] = df['open'].astype(float)
    result['close'] = df['close'].astype(float)
    result['high'] = df['high'].astype(float)
    result['low'] = df['low'].astype(float)
    result['volume'] = df['vol'].astype(float)

    if 'datetime' in df.columns:
        result['time'] = pd.to_datetime(df['datetime'])
        result.set_index('time', inplace=True)
        result.index.name = ''

    return result
