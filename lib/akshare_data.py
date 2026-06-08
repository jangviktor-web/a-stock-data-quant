"""
akshare 数据层 — 资金流向、北向资金、板块行情、融资融券

依赖 akshare >= 1.18.x
支持多数据源降级: akshare → 备用源 (百度/mootdx/datacenter/同花顺)
"""

import warnings
import sys
import os
warnings.filterwarnings("ignore")

try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False


def _require_akshare():
    """检查 akshare 是否已安装"""
    if not HAS_AKSHARE or os.environ.get('AKSHARE_MOCK_FAIL'):
        raise RuntimeError("akshare 未安装或被禁用")


def _safe_call(func, *args, **kwargs):
    """安全调用 akshare 函数，统一异常处理"""
    _require_akshare()
    try:
        return func(*args, **kwargs)
    except Exception as e:
        raise RuntimeError(f"akshare 接口调用失败: {e}") from e


def _with_fallback(primary_fn, *backup_fns):
    """
    多数据源降级包装器

    Parameters
    ----------
    primary_fn : callable - 主数据源函数
    *backup_fns : (name, callable) 备用数据源
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 尝试主数据源
            try:
                result = primary_fn(*args, **kwargs)
                if result is not None and result != [] and result != {}:
                    if isinstance(result, list) and len(result) > 0:
                        if isinstance(result[0], dict) and 'error' in result[0]:
                            raise RuntimeError(result[0]['error'])
                    if isinstance(result, dict):
                        if 'error' in result:
                            raise RuntimeError(result['error'])
                        # dict 全部值为空也视为无效结果
                        if all(not v for v in result.values()):
                            raise RuntimeError('空结果')
                    return result
            except Exception as e:
                print(f"  [降级] akshare 不可用({e})，尝试备用源", file=sys.stderr)

            # 尝试备用源
            for name, backup_fn in backup_fns:
                try:
                    result = backup_fn(*args, **kwargs)
                    if result is not None and result != [] and result != {}:
                        print(f"  [降级] 已切换到备用源: {name}", file=sys.stderr)
                        return result
                except Exception as e2:
                    print(f"  [降级] {name} 也失败: {e2}", file=sys.stderr)

            # 全部失败，返回空结果
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator


# ── 个股资金流向 ──────────────────────────────────────────

def _ak_fund_flow(code, market=None):
    """akshare 资金流向"""
    _require_akshare()
    if market is None:
        market = 'sz' if code.startswith(('0', '3')) else 'sh'
    df = ak.stock_individual_fund_flow(stock=code, market=market)

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


def _baidu_fund_flow(code, market=None):
    """百度 资金流向"""
    from lib.sources_baidu import get_fund_flow as baidu_ff
    mkt = market or ('sz' if code.startswith(('0', '3')) else 'sh')
    return baidu_ff(code, market=mkt)


@_with_fallback(_ak_fund_flow, ('百度', _baidu_fund_flow))
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
    return {'rows': [], 'summary': {}}


# ── 北向资金 ──────────────────────────────────────────────

def _ak_north_flow(symbol="沪股通", days=10):
    """akshare 北向资金"""
    _require_akshare()
    df = ak.stock_hsgt_hist_em(symbol=symbol)

    if df is None or df.empty:
        return []

    rows = []
    for _, r in df.tail(days).iterrows():
        net_buy = r.get('当日成交净买额', 0)
        fund_flow = r.get('当日资金流入', 0)
        if net_buy != net_buy:  # NaN check
            net_buy = 0
        if fund_flow != fund_flow:
            fund_flow = 0
        # 跳过全为 NaN 的行（上游数据缺失）
        if net_buy == 0 and fund_flow == 0:
            continue
        rows.append({
            'date': str(r.get('日期', '')),
            'net_buy': float(net_buy),
            'fund_flow': float(fund_flow),
            'leader': str(r.get('领涨股', '')),
        })
    return rows


def _dc_north_flow(symbol="沪股通", days=10):
    """东财数据中心 北向资金 (akshare NaN 时的备用源)"""
    import requests as _req
    type_map = {'沪股通': '001', '深股通': '002'}
    mt = type_map.get(symbol, '001')

    url = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
    params = {
        'reportName': 'RPT_MUTUAL_DEAL_HISTORY',
        'columns': 'ALL',
        'filter': f'(MUTUAL_TYPE="{mt}")',
        'pageNumber': 1,
        'pageSize': days,
        'sortColumns': 'TRADE_DATE',
        'sortTypes': -1,
        'source': 'WEB',
        'client': 'WEB',
    }
    s = _req.Session()
    s.trust_env = False
    r = s.get(url, params=params, timeout=10)
    d = r.json()
    if not d.get('result'):
        return []

    items = d['result'].get('data', []) or []
    rows = []
    for i in items:
        net = i.get('NET_DEAL_AMT')
        if net is None:
            net = 0
        leader = i.get('LEAD_STOCKS_NAME', '') or ''
        date_str = (i.get('TRADE_DATE', '') or '')[:10]
        rows.append({
            'date': date_str,
            'net_buy': float(net),
            'fund_flow': 0,
            'leader': leader,
        })
    return rows


def _hexin_north_flow(symbol="沪股通", days=10):
    """同花顺 北向资金"""
    from lib.sources_hexin import get_north_flow as hexin_nf
    return hexin_nf(symbol=symbol, days=days)


@_with_fallback(_ak_north_flow, ('东财数据中心', _dc_north_flow), ('同花顺', _hexin_north_flow))
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
    return []


# ── 板块行情 ──────────────────────────────────────────────

def _ak_sector_hot(top_n=10):
    """akshare 板块涨跌"""
    _require_akshare()
    df = ak.stock_board_industry_name_em()

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


@_with_fallback(_ak_sector_hot)
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
    return {'hot': [], 'cold': []}


def _ak_sector_list():
    """akshare 板块列表"""
    _require_akshare()
    df = ak.stock_board_industry_name_em()

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


@_with_fallback(_ak_sector_list)
def get_sector_list():
    """
    获取全部行业板块列表（含涨跌幅和最新价）

    Returns
    -------
    list of dict: [{'name': ..., 'code': ..., 'chg_pct': ..., 'price': ...}, ...]
    """
    return []


# ── 融资融券 ──────────────────────────────────────────────

def _ak_margin_data(days=30):
    """akshare 融资融券"""
    _require_akshare()
    from datetime import datetime, timedelta

    end = datetime.now().strftime('%Y%m%d')
    start = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

    df = ak.stock_margin_sse(start_date=start, end_date=end)

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


def _dc_margin_data(days=30):
    """datacenter 融资融券"""
    from lib.sources_datacenter import get_margin_data as dc_md
    return dc_md(days=days)


@_with_fallback(_ak_margin_data, ('datacenter', _dc_margin_data))
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
    return []


# ── 股票综合诊断数据 ────────────────────────────────────────

def get_stock_diagnosis_data(code):
    """
    获取股票诊断所需的基本面+估值数据
    """
    _require_akshare()
    result = {'code': code}

    try:
        df = ak.stock_financial_abstract(symbol=code)
        if df is not None and not df.empty:
            latest = df.iloc[0]
            result['financial'] = {str(k): v for k, v in latest.items()}
    except Exception:
        result['financial'] = {}

    try:
        df = ak.stock_financial_analysis_indicator(symbol=code)
        if df is not None and not df.empty:
            latest = df.iloc[0]
            result['valuation'] = {str(k): v for k, v in latest.items()}
    except Exception:
        result['valuation'] = {}

    return result


# ── 宏观经济数据 ──────────────────────────────────────────

def get_macro_data(indicator='cpi'):
    """
    获取中国宏观经济数据
    indicator: cpi/ppi/gdp/pmi/m2/lpr/unemployment/trade/industrial
    """
    _require_akshare()

    func_map = {
        'cpi': ak.macro_china_cpi,
        'ppi': ak.macro_china_ppi,
        'gdp': ak.macro_china_gdp,
        'pmi': ak.macro_china_pmi,
        'm2': ak.macro_china_money_supply,
        'lpr': ak.macro_china_lpr,
        'unemployment': ak.macro_china_urban_unemployment,
        'trade': ak.macro_china_trade_balance,
        'industrial': ak.macro_china_gyzjz,
    }

    if indicator not in func_map:
        return {'indicator': indicator, 'data': [], 'error': f'未知指标，可选: {", ".join(func_map.keys())}'}

    try:
        df = _safe_call(func_map[indicator])
    except Exception as e:
        return {'indicator': indicator, 'data': [], 'error': str(e)}

    if df is None or df.empty:
        return {'indicator': indicator, 'data': []}

    df = df.head(12)
    rows = []
    for _, r in df.iterrows():
        row = {}
        for col in df.columns:
            val = r[col]
            try:
                import math
                if isinstance(val, float) and math.isnan(val):
                    val = None
            except (TypeError, ValueError):
                pass
            row[str(col)] = val
        rows.append(row)

    return {'indicator': indicator, 'data': rows, 'columns': list(df.columns)}


# ── 涨停/跌停/强势池 ──────────────────────────────────────

def _recent_trade_date(date=''):
    """获取最近交易日（周末回退到周五）"""
    if date:
        return date
    from datetime import datetime, timedelta
    dt = datetime.now()
    # 如果是周末或下午3点前，回退
    if dt.weekday() >= 5:  # 周六=5, 周日=6
        dt -= timedelta(days=dt.weekday() - 4)  # 回到周五
    elif dt.weekday() == 0 and dt.hour < 15:  # 周一还没收盘
        dt -= timedelta(days=3)  # 回到周五
    elif dt.hour < 15:  # 工作日还没收盘
        dt -= timedelta(days=1)
    return dt.strftime('%Y%m%d')


def get_zt_pool(date='', limit=30):
    """
    获取涨停股票池

    Parameters
    ----------
    date : str - 日期 YYYYMMDD (空=自动取最近交易日)
    limit : int - 返回数量

    Returns
    -------
    list of dict
    """
    _require_akshare()
    date = _recent_trade_date(date)
    try:
        df = ak.stock_zt_pool_em(date=date)
    except Exception as e:
        return []

    if df is None or df.empty:
        return []

    rows = []
    for _, r in df.head(limit).iterrows():
        rows.append({
            'code': str(r.get('代码', '')),
            'name': str(r.get('名称', '')),
            'chg_pct': r.get('涨跌幅', 0),
            'price': r.get('最新价', 0),
            'amount': r.get('成交额', 0),
            'turnover': r.get('换手率', 0),
            'seal_amount': r.get('封板资金', 0),
            'first_seal': str(r.get('首次封板时间', '')),
            'last_seal': str(r.get('最后封板时间', '')),
            'break_count': r.get('炸板次数', 0),
            'zt_stat': str(r.get('涨停统计', '')),
            'streak': r.get('连板数', 0),
            'industry': str(r.get('所属行业', '')),
        })
    return rows


def get_dt_pool(date='', limit=30):
    """
    获取跌停股票池

    Parameters
    ----------
    date : str - 日期 YYYYMMDD (空=自动取最近交易日)
    limit : int - 返回数量

    Returns
    -------
    list of dict
    """
    _require_akshare()
    date = _recent_trade_date(date)
    try:
        df = ak.stock_zt_pool_dtgc_em(date=date)
    except Exception as e:
        return []

    if df is None or df.empty:
        return []

    rows = []
    for _, r in df.head(limit).iterrows():
        rows.append({
            'code': str(r.get('代码', '')),
            'name': str(r.get('名称', '')),
            'chg_pct': r.get('涨跌幅', 0),
            'price': r.get('最新价', 0),
            'amount': r.get('成交额', 0),
            'turnover': r.get('换手率', 0),
            'seal_amount': r.get('封单资金', 0),
            'consecutive': r.get('连续跌停', 0),
            'industry': str(r.get('所属行业', '')),
        })
    return rows


# ── 龙虎榜统计 ──────────────────────────────────────────────

def _ak_lhb_data(days=5, limit=30):
    """akshare 龙虎榜"""
    _require_akshare()
    df = ak.stock_lhb_ggtj_sina(symbol=str(days))

    if df is None or df.empty:
        return []

    rows = []
    for _, r in df.head(limit).iterrows():
        rows.append({
            'code': str(r.get('股票代码', '')),
            'name': str(r.get('股票名称', '')),
            'count': r.get('上榜次数', 0),
            'buy_amt': r.get('累积购买额', 0),
            'sell_amt': r.get('累积卖出额', 0),
            'net_buy': r.get('净额', 0),
            'buy_seats': r.get('买入席位数', 0),
            'sell_seats': r.get('卖出席位数', 0),
        })
    return rows


def _dc_lhb_data(days=5, limit=30):
    """datacenter 龙虎榜"""
    from lib.sources_datacenter import get_lhb_data as dc_lhb
    return dc_lhb(days=days, limit=limit)


@_with_fallback(_ak_lhb_data, ('datacenter', _dc_lhb_data))
def get_lhb_data(days=5, limit=30):
    """
    获取龙虎榜统计

    Parameters
    ----------
    days : str - 最近 N 天: '5'/'10'/'30'/'60'
    limit : int - 返回数量

    Returns
    -------
    list of dict
    """
    return []


# ── 板块资金流排名 ──────────────────────────────────────────

def get_sector_fund_rank(days='今日', category='行业资金流', limit=20):
    """
    获取板块资金流排名

    Parameters
    ----------
    days : str - '今日' / '5日' / '10日'
    category : str - '行业资金流' / '概念资金流' / '地域资金流'
    limit : int - 返回数量

    Returns
    -------
    list of dict
    """
    _require_akshare()
    try:
        df = ak.stock_sector_fund_flow_rank(indicator=days, sector_type=category)
    except Exception as e:
        return []

    if df is None or df.empty:
        return []

    rows = []
    for _, r in df.head(limit).iterrows():
        rows.append({
            'name': str(r.get('名称', '')),
            'chg_pct': r.get('涨跌幅', 0),
            'main_net': r.get('主力净流入-净额', 0),
            'main_pct': r.get('主力净流入-净占比', 0),
            'super_large_net': r.get('超大单净流入-净额', 0),
            'large_net': r.get('大单净流入-净额', 0),
        })
    return rows


# ── 限售解禁 ──────────────────────────────────────────────

def _ak_locked_shares(code='', limit=20):
    """akshare 限售解禁"""
    _require_akshare()
    if not code:
        code = '600000'
    df = ak.stock_restricted_release_queue_sina(symbol=code)

    if df is None or df.empty:
        return []

    rows = []
    for _, r in df.head(limit).iterrows():
        rows.append({
            'date': str(r.get('解禁日期', '')),
            'code': str(r.get('代码', '')),
            'name': str(r.get('名称', '')),
            'release_amount': r.get('解禁数量', 0),
            'release_value': r.get('解禁股流通市值', 0),
        })
    return rows


def _dc_locked_shares(code='', limit=20):
    """datacenter 限售解禁"""
    from lib.sources_datacenter import get_locked_shares as dc_ls
    return dc_ls(code=code, limit=limit)


@_with_fallback(_ak_locked_shares, ('datacenter', _dc_locked_shares))
def get_locked_shares(code='', limit=20):
    """
    获取限售解禁日历

    Parameters
    ----------
    code : str - 股票代码 (纯数字，如 '600519')，不传则查默认股票
    limit : int - 返回数量

    Returns
    -------
    list of dict
    """
    return []


# ── 股东人数 ──────────────────────────────────────────────

def _ak_holder_num(code):
    """akshare 股东人数"""
    _require_akshare()
    df = ak.stock_zh_a_gdhs_detail_em(symbol=code)

    if df is None or df.empty:
        return []

    rows = []
    for _, r in df.iterrows():
        rows.append({
            'date': str(r.get('股东户数统计截止日', '')),
            'holder_count': r.get('股东户数-本次', 0),
            'avg_amount': r.get('户均持股市值', 0),
            'avg_shares': r.get('户均持股数量', 0),
            'total_market': r.get('总市值', 0),
            'change': r.get('股东户数-增减', 0),
            'change_pct': r.get('股东户数-增减比例', 0),
        })
    return rows


def _dc_holder_num(code):
    """datacenter 股东人数"""
    from lib.sources_datacenter import get_holder_num as dc_hn
    return dc_hn(code=code)


@_with_fallback(_ak_holder_num, ('datacenter', _dc_holder_num))
def get_holder_num(code):
    """
    获取股东人数变化

    Parameters
    ----------
    code : str - 股票代码 (纯数字)

    Returns
    -------
    list of dict
    """
    return []


# ── 十大股东 ──────────────────────────────────────────────

def get_top10_holders(code, holder_type='circulate'):
    """
    获取十大股东

    Parameters
    ----------
    code : str - 股票代码 (纯数字，如 '600519')
    holder_type : str - 'main'(十大股东) / 'circulate'(十大流通股东)

    Returns
    -------
    dict with 'holdings'
    """
    _require_akshare()
    result = {'holdings': []}

    # 确定市场前缀
    if code.startswith(('0', '3')):
        symbol = f'sz{code}'
    elif code.startswith('6'):
        symbol = f'sh{code}'
    else:
        symbol = f'sh{code}'

    try:
        if holder_type == 'main':
            df = ak.stock_gdfx_top_10_em(symbol=symbol)
        else:
            df = ak.stock_gdfx_free_top_10_em(symbol=symbol)
    except Exception as e:
        return result

    if df is None or df.empty:
        return result

    for _, r in df.head(10).iterrows():
        result['holdings'].append({
            'rank': r.get('名次', 0),
            'holder': str(r.get('股东名称', '')),
            'nature': str(r.get('股东性质', '')),
            'shares': r.get('持股数', 0),
            'ratio': r.get('占总流通股本持股比例', 0),
            'type': str(r.get('股份类型', '')),
            'change': str(r.get('增减', '')),
            'change_pct': r.get('变动比率', 0),
        })
    return result


# ── 基金重仓 ──────────────────────────────────────────────

def get_institutional_holdings(limit=20):
    """
    获取基金重仓股（基金持仓报告）

    Parameters
    ----------
    limit : int - 返回数量

    Returns
    -------
    list of dict
    """
    _require_akshare()
    try:
        df = ak.stock_report_fund_hold(symbol='基金持仓')
    except Exception as e:
        return []

    if df is None or df.empty:
        return []

    rows = []
    for _, r in df.head(limit).iterrows():
        rows.append({
            'code': str(r.get('股票代码', '')),
            'name': str(r.get('股票简称', '')),
            'fund_count': r.get('持有基金家数', 0),
            'shares': r.get('持股总数', 0),
            'market_value': r.get('持股市值', 0),
            'change': str(r.get('持股变化', '')),
            'change_value': r.get('持股变动数值', 0),
            'change_pct': r.get('持股变动比例', 0),
        })
    return rows


# ── 行业PE对比 ──────────────────────────────────────────────

def get_industry_pe(limit=20):
    """
    获取行业PE对比（证监会行业分类，一级行业）

    Returns
    -------
    list of dict
    """
    _require_akshare()
    from datetime import datetime, timedelta

    # 尝试最近的日期，cninfo数据有延迟
    df = None
    for delta in [0, 7, 30, 90, 180]:
        try:
            date = (datetime.now() - timedelta(days=delta)).strftime('%Y%m%d')
            df = ak.stock_industry_pe_ratio_cninfo(symbol='证监会行业分类', date=date)
            if df is not None and not df.empty:
                break
        except Exception:
            continue

    if df is None or df.empty:
        return []

    # 只取一级行业 (行业层级=1)
    if '行业层级' in df.columns:
        df = df[df['行业层级'] == 1.0]

    rows = []
    for _, r in df.head(limit).iterrows():
        rows.append({
            'industry': str(r.get('行业名称', '')),
            'company_count': r.get('公司数量', 0),
            'pe_weighted': r.get('静态市盈率-加权平均', 0),
            'pe_median': r.get('静态市盈率-中位数', 0),
            'market_cap': r.get('总市值-静态', 0),
        })
    return rows


# ── 市场PE分位 ──────────────────────────────────────────────

def get_market_pe_percentile():
    """
    获取市场估值分位

    Returns
    -------
    dict
    """
    _require_akshare()
    result = {}
    try:
        df = ak.stock_a_pe_and_target(symbol='上证A股')
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            result['index'] = '上证A股'
            result['pe'] = latest.get('滚动PE', latest.get('PE', 0))
    except Exception:
        pass

    try:
        result['pe_median'] = ak.stock_a_all_pe()
    except Exception:
        pass

    return result


# ── 大宗交易 ──────────────────────────────────────────────

def _ak_block_trade(code='', limit=20):
    """akshare 大宗交易"""
    _require_akshare()
    from datetime import datetime, timedelta

    end = datetime.now().strftime('%Y%m%d')
    start = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')

    df = ak.stock_dzjy_mrtj(start_date=start, end_date=end)

    if df is None or df.empty:
        return []

    if code:
        df = df[df['证券代码'].astype(str).str.contains(code)]

    rows = []
    for _, r in df.head(limit).iterrows():
        rows.append({
            'date': str(r.get('交易日期', '')),
            'code': str(r.get('证券代码', '')),
            'name': str(r.get('证券简称', '')),
            'close': r.get('收盘价', 0),
            'deal_price': r.get('成交价', 0),
            'discount': r.get('折溢率', 0),
            'amount': r.get('成交总额', 0),
            'count': r.get('成交笔数', 0),
            'volume': r.get('成交总量', 0),
        })
    return rows


def _dc_block_trade(code='', limit=20):
    """datacenter 大宗交易"""
    from lib.sources_datacenter import get_block_trade as dc_bt
    return dc_bt(code=code, limit=limit)


@_with_fallback(_ak_block_trade, ('datacenter', _dc_block_trade))
def get_block_trade(code='', limit=20):
    """
    获取大宗交易

    Parameters
    ----------
    code : str - 股票代码 (纯数字，空=全市场)
    limit : int - 返回数量

    Returns
    -------
    list of dict
    """
    return []


# ── 融资融券 (个股) ──────────────────────────────────────────

def _ak_margin_detail(code, market='sh', days=10):
    """akshare 个股融资融券"""
    _require_akshare()
    from datetime import datetime, timedelta

    df = None
    try:
        end = datetime.now().strftime('%Y%m%d')
        start = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')
        if market == 'sh':
            df = ak.stock_margin_detail_sse(date=end)
        else:
            df = ak.stock_margin_detail_szse(date=end)

        if df is not None and not df.empty:
            code_col = '标的证券代码' if '标的证券代码' in df.columns else '证券代码'
            if code_col in df.columns:
                df = df[df[code_col].astype(str).str.contains(code)]
    except Exception:
        pass

    if df is None or df.empty:
        return []

    rows = []
    for _, r in df.head(days).iterrows():
        row = {}
        for col in df.columns:
            row[str(col)] = r[col]
        rows.append(row)
    return rows


def _dc_margin_detail(code, market='sh', days=10):
    """datacenter 个股融资融券"""
    from lib.sources_datacenter import get_margin_detail as dc_md
    return dc_md(code=code, market=market, days=days)


@_with_fallback(_ak_margin_detail, ('datacenter', _dc_margin_detail))
def get_margin_detail(code, market='sh', days=10):
    """
    获取个股融资融券数据

    Parameters
    ----------
    code : str - 股票代码
    market : str - 'sh' / 'sz'
    days : int - 返回天数

    Returns
    -------
    list of dict
    """
    return []


# ── 市场热点 ──────────────────────────────────────────────

def _ak_market_hotspot(top_n=20):
    """akshare 市场热点"""
    _require_akshare()
    result = {'hot_ranks': [], 'concept_hot': [], 'industry_hot': []}

    try:
        df = ak.stock_hot_rank_em()
        if df is not None and not df.empty:
            for _, r in df.head(top_n).iterrows():
                result['hot_ranks'].append({
                    'code': str(r.get('股票代码', '')),
                    'name': str(r.get('股票名称', '')),
                    'price': r.get('最新价', 0),
                    'chg_pct': r.get('涨跌幅', 0),
                    'rank': r.get('当前排名', 0),
                    'heat': r.get('人气值', 0),
                })
    except Exception:
        pass

    try:
        df = ak.stock_board_concept_name_em()
        if df is not None and not df.empty:
            for _, r in df.sort_values('涨跌幅', ascending=False).head(top_n).iterrows():
                result['concept_hot'].append({
                    'name': str(r.get('板块名称', '')),
                    'chg_pct': r.get('涨跌幅', 0),
                    'leader': str(r.get('领涨股票', '')),
                })
    except Exception:
        pass

    try:
        df = ak.stock_board_industry_name_em()
        if df is not None and not df.empty:
            for _, r in df.sort_values('涨跌幅', ascending=False).head(top_n).iterrows():
                result['industry_hot'].append({
                    'name': str(r.get('板块名称', '')),
                    'chg_pct': r.get('涨跌幅', 0),
                    'leader': str(r.get('领涨股票', '')),
                })
    except Exception:
        pass

    return result


def _em_direct_hotspot(top_n=20):
    """东财直接 API 市场热点 (akshare 失败时的备用源)"""
    import requests as _req

    result = {'hot_ranks': [], 'concept_hot': [], 'industry_hot': []}
    base = 'https://push2.eastmoney.com/api/qt/clist/get'
    s = _req.Session()
    s.trust_env = False
    common = {'pn': 1, 'np': 1, 'ut': 'bd1d9ddb04089700cf9c27f6f7426281', 'fltt': 2, 'invt': 2}

    # 概念板块
    try:
        r = s.get(base, params={**common, 'pz': top_n, 'po': 1, 'fid': 'f3', 'fs': 'm:90+t:3+f:!50', 'fields': 'f2,f3,f4,f12,f14'}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        items = r.json().get('data', {}).get('diff', []) or []
        for i in items:
            result['concept_hot'].append({'name': i.get('f14', ''), 'chg_pct': i.get('f3', 0), 'leader': ''})
    except Exception:
        pass

    # 行业板块
    try:
        r = s.get(base, params={**common, 'pz': top_n, 'po': 1, 'fid': 'f3', 'fs': 'm:90+t:2+f:!50', 'fields': 'f2,f3,f4,f12,f14'}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        items = r.json().get('data', {}).get('diff', []) or []
        for i in items:
            result['industry_hot'].append({'name': i.get('f14', ''), 'chg_pct': i.get('f3', 0), 'leader': ''})
    except Exception:
        pass

    return result


@_with_fallback(_ak_market_hotspot, ('东财直连', _em_direct_hotspot))
def get_market_hotspot(top_n=20):
    """获取市场热点：人气榜 + 概念板块 + 行业板块"""
    return {'hot_ranks': [], 'concept_hot': [], 'industry_hot': []}
