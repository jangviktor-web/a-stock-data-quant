"""
akshare 数据层 — 资金流向、北向资金、板块行情、融资融券

依赖 akshare >= 1.18.x
"""

import warnings
warnings.filterwarnings("ignore")

try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False


def _require_akshare():
    """检查 akshare 是否已安装"""
    if not HAS_AKSHARE:
        raise RuntimeError("akshare 未安装，请运行: pip3 install akshare")


def _safe_call(func, *args, **kwargs):
    """安全调用 akshare 函数，统一异常处理"""
    _require_akshare()
    try:
        return func(*args, **kwargs)
    except Exception as e:
        raise RuntimeError(f"akshare 接口调用失败: {e}") from e


# ── 个股资金流向 ──────────────────────────────────────────

def get_fund_flow(code, market=None):
    """
    获取个股主力资金流向

    Parameters
    ----------
    code : str - 股票代码 (纯数字，如 '600519')
    market : str - 市场 ('sh' 或 'sz')，不传则自动判断

    Returns
    -------
    dict: {'rows': [...], 'summary': {...}}
    """
    _require_akshare()
    if market is None:
        market = 'sz' if code.startswith(('0', '3')) else 'sh'
    try:
        df = ak.stock_individual_fund_flow(stock=code, market=market)
    except Exception as e:
        return {'rows': [], 'summary': {}, 'error': str(e)}

    if df is None or df.empty:
        return {'rows': [], 'summary': {}}

    rows = []
    for _, r in df.tail(5).iterrows():
        rows.append({
            'date': str(r.get('日期', '')),
            'close': r.get('收盘价', 0),
            'chg_pct': r.get('涨跌幅', 0),
            'main_net': r.get('主力净流入-净额', 0),
            'main_pct': r.get('主力净流入-净占比', 0),
            'super_large_net': r.get('超大单净流入-净额', 0),
            'super_large_pct': r.get('超大单净流入-净占比', 0),
            'large_net': r.get('大单净流入-净额', 0),
            'mid_net': r.get('中单净流入-净额', 0),
            'small_net': r.get('小单净流入-净额', 0),
        })

    last = rows[-1] if rows else {}
    recent3 = rows[-3:] if len(rows) >= 3 else rows
    summary = {
        'main_net_1d': last.get('main_net', 0),
        'main_pct_1d': last.get('main_pct', 0),
        'super_large_1d': last.get('super_large_net', 0),
        'main_net_3d': sum(r['main_net'] for r in recent3),
        'super_large_3d': sum(r['super_large_net'] for r in recent3),
    }
    return {'rows': rows, 'summary': summary}


# ── 北向资金 ──────────────────────────────────────────────

def get_north_flow(symbol="沪股通", days=10):
    """
    获取北向资金（沪股通/深股通）历史数据

    Parameters
    ----------
    symbol : str - '沪股通' 或 '深股通'
    days : int - 返回最近 N 天数据

    Returns
    -------
    list of dict: [{'date': ..., 'net_buy': ..., 'fund_flow': ..., 'leader': ...}, ...]
    """
    _require_akshare()
    try:
        df = ak.stock_hsgt_hist_em(symbol=symbol)
    except Exception as e:
        return [{'error': f"北向资金数据获取失败: {e}"}]

    if df is None or df.empty:
        return []

    rows = []
    for _, r in df.tail(days).iterrows():
        net_buy = r.get('当日成交净买额', 0)
        fund_flow = r.get('当日资金流入', 0)
        # 处理 NaN
        if net_buy != net_buy:  # NaN check
            net_buy = 0
        if fund_flow != fund_flow:
            fund_flow = 0
        rows.append({
            'date': str(r.get('日期', '')),
            'net_buy': float(net_buy),
            'fund_flow': float(fund_flow),
            'leader': str(r.get('领涨股', '')),
        })
    return rows


# ── 板块行情 ──────────────────────────────────────────────

def get_sector_hot(top_n=10):
    """
    获取行业板块涨跌幅排名

    Parameters
    ----------
    top_n : int - 返回涨幅前N和后N

    Returns
    -------
    dict: {'hot': [...], 'cold': [...]}
    """
    _require_akshare()
    try:
        df = ak.stock_board_industry_name_em()
    except Exception as e:
        return {'hot': [], 'cold': [], 'error': str(e)}

    if df is None or df.empty:
        return {'hot': [], 'cold': []}

    df_sorted = df.sort_values('涨跌幅', ascending=False)
    hot, cold = [], []
    for _, r in df_sorted.head(top_n).iterrows():
        hot.append({
            'name': r.get('板块名称', ''),
            'chg_pct': r.get('涨跌幅', 0),
            'leader': r.get('领涨股票', ''),
        })
    for _, r in df_sorted.tail(top_n).iterrows():
        cold.append({
            'name': r.get('板块名称', ''),
            'chg_pct': r.get('涨跌幅', 0),
        })
    return {'hot': hot, 'cold': cold}


def get_sector_list():
    """
    获取全部行业板块列表（含涨跌幅和最新价）

    Returns
    -------
    list of dict: [{'name': ..., 'code': ..., 'chg_pct': ..., 'price': ...}, ...]
    """
    _require_akshare()
    try:
        df = ak.stock_board_industry_name_em()
    except Exception as e:
        return []

    if df is None or df.empty:
        return []

    sectors = []
    for _, r in df.iterrows():
        sectors.append({
            'name': str(r.get('板块名称', '')),
            'code': str(r.get('板块代码', '')),
            'chg_pct': float(r.get('涨跌幅', 0) if r.get('涨跌幅', 0) == r.get('涨跌幅', 0) else 0),
            'price': float(r.get('最新价', 0) if r.get('最新价', 0) == r.get('最新价', 0) else 0),
        })
    return sectors


# ── 融资融券 ──────────────────────────────────────────────

def get_margin_data(days=30):
    """
    获取融资融券数据（上交所）

    Parameters
    ----------
    days : int - 获取最近 N 天数据

    Returns
    -------
    list of dict: [{'date': ..., 'margin_balance': ..., 'margin_buy': ..., 'short_balance': ...}, ...]
    """
    _require_akshare()
    from datetime import datetime, timedelta

    end = datetime.now().strftime('%Y%m%d')
    start = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

    try:
        df = ak.stock_margin_sse(start_date=start, end_date=end)
    except Exception as e:
        return []

    if df is None or df.empty:
        return []

    rows = []
    for _, r in df.iterrows():
        rows.append({
            'date': str(r.get('信用交易日期', '')),
            'margin_balance': r.get('融资余额', 0),
            'margin_buy': r.get('融资买入额', 0),
            'short_balance': r.get('融券余量金额', 0),
        })
    return rows
