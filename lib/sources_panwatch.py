"""
PanWatch 数据接口移植

从 https://github.com/TNT-Likely/PanWatch 移植/改写的热门榜、资金流向、基本面快照等轻量接口。
这些接口基于东方财富 push2/push2his 和腾讯 qt.gtimg.cn，不依赖 akshare。
"""

from __future__ import annotations

import sys
import time

import requests


def _safe_float(value, default=0.0) -> float:
    if value is None or value == "" or value == "-":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _cn_exchange_prefix(code: str) -> str:
    """sh / sz / bj"""
    if code.startswith("920") or code.startswith(("83", "87", "88")):
        return "bj"
    if code.startswith(("5", "6")) or code.startswith("900"):
        return "sh"
    return "sz"


def _normalize_diff(data: dict | None) -> list[dict]:
    """东财 clist diff 可能是 dict(index 为 key) 或 list。统一成 list。"""
    diff = ((data or {}).get("data") or {}).get("diff") or []
    if isinstance(diff, dict):
        return list(diff.values())
    return diff


# ---------------------------------------------------------------------------
# 1. 热门股票排行
# ---------------------------------------------------------------------------

def get_hot_stocks(mode: str = "turnover", limit: int = 20) -> list[dict]:
    """
    A股热门股票排行 (东财 push2 clist)

    Parameters
    ----------
    mode : str - 'turnover' 按成交额, 'gainers' 按涨幅, 'losers' 按跌幅
    limit : int - 返回数量 (最大 100)
    """
    fid = "f6" if mode == "turnover" else "f3"
    sort_order = "1" if mode == "losers" else "1"  # 涨幅倒序=涨幅最大在前, 跌幅需要fid=f3且排序需验证
    if mode == "losers":
        fid = "f3"

    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1,
        "pz": max(1, min(int(limit), 100)),
        "po": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "fid": fid,
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": "f12,f14,f2,f3,f4,f5,f6,f7,f8",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://quote.eastmoney.com/",
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10,
                         proxies={"http": None, "https": None})
        r.raise_for_status()
        data = r.json()
        items = _normalize_diff(data)
        results = []
        for it in items:
            results.append({
                "code": str(it.get("f12") or "").strip(),
                "name": str(it.get("f14") or "").strip(),
                "price": _safe_float(it.get("f2"), None),
                "change_pct": _safe_float(it.get("f3"), None),
                "change_amount": _safe_float(it.get("f4"), None),
                "volume": _safe_float(it.get("f5"), None),
                "turnover": _safe_float(it.get("f6"), None),
                "amplitude": _safe_float(it.get("f7"), None),
                "turnover_rate": _safe_float(it.get("f8"), None),
            })
        return results
    except Exception as e:
        print(f"[sources_panwatch] get_hot_stocks failed: {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# 2. 热门板块排行
# ---------------------------------------------------------------------------

def get_hot_boards(mode: str = "gainers", limit: int = 12) -> list[dict]:
    """
    A股热门板块排行 (东财 push2 clist)

    Parameters
    ----------
    mode : str - 'gainers' 涨幅榜, 'turnover' 成交额榜, 'losers' 跌幅榜
    limit : int - 返回数量
    """
    fid = "f3" if mode in ("gainers", "losers") else "f6"
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1,
        "pz": max(1, min(int(limit), 100)),
        "po": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "fid": fid,
        "fs": "m:90+t:2",
        "fields": "f12,f14,f2,f3,f4,f6,f8",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://quote.eastmoney.com/",
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10,
                         proxies={"http": None, "https": None})
        r.raise_for_status()
        data = r.json()
        items = _normalize_diff(data)
        results = []
        for it in items:
            results.append({
                "code": str(it.get("f12") or "").strip(),
                "name": str(it.get("f14") or "").strip(),
                "price": _safe_float(it.get("f2"), None),
                "change_pct": _safe_float(it.get("f3"), None),
                "change_amount": _safe_float(it.get("f4"), None),
                "turnover": _safe_float(it.get("f6"), None),
                "turnover_rate": _safe_float(it.get("f8"), None),
            })
        return results
    except Exception as e:
        print(f"[sources_panwatch] get_hot_boards failed: {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# 3. 板块成分股
# ---------------------------------------------------------------------------

def get_board_stocks(board_code: str, mode: str = "gainers", limit: int = 20) -> list[dict]:
    """
    查询某个东财板块的成分股 (东财 push2 clist)

    Parameters
    ----------
    board_code : str - 东财板块代码, 如 'BK0892'
    mode : str - 'gainers' 涨幅, 'turnover' 成交额
    limit : int - 返回数量
    """
    fid = "f3" if mode in ("gainers", "losers") else "f6"
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1,
        "pz": max(1, min(int(limit), 100)),
        "po": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "fid": fid,
        "fs": f"b:{board_code}",
        "fields": "f12,f14,f2,f3,f4,f5,f6,f7,f8",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://quote.eastmoney.com/",
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10,
                         proxies={"http": None, "https": None})
        r.raise_for_status()
        data = r.json()
        items = _normalize_diff(data)
        results = []
        for it in items:
            results.append({
                "code": str(it.get("f12") or "").strip(),
                "name": str(it.get("f14") or "").strip(),
                "price": _safe_float(it.get("f2"), None),
                "change_pct": _safe_float(it.get("f3"), None),
                "change_amount": _safe_float(it.get("f4"), None),
                "volume": _safe_float(it.get("f5"), None),
                "turnover": _safe_float(it.get("f6"), None),
                "amplitude": _safe_float(it.get("f7"), None),
                "turnover_rate": _safe_float(it.get("f8"), None),
            })
        return results
    except Exception as e:
        print(f"[sources_panwatch] get_board_stocks failed: {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# 4. 资金流向细分
# ---------------------------------------------------------------------------

def get_capital_flow_detail(code: str) -> dict | None:
    """
    获取个股资金流向细分 (东财 push2his fflow)

    Returns
    -------
    {
        'code': '600519',
        'name': '贵州茅台',
        'main_net_inflow': 123456789.0,    # 主力净流入 (超大+大单)
        'main_net_inflow_pct': 5.2,        # 主力净流入占比 (%)
        'super_net_inflow': 98765432.0,    # 超大单净流入
        'big_net_inflow': 24691357.0,      # 大单净流入
        'mid_net_inflow': -12345678.0,     # 中单净流入
        'small_net_inflow': -111111111.0,  # 小单净流入
        'main_net_5d': 999999999.0,        # 5日主力净流入
    }
    """
    code = code.replace("sh", "").replace("sz", "").replace(".", "")
    prefix = _cn_exchange_prefix(code)
    secid = f"{1 if prefix == 'sh' else 0}.{code}"

    url = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
    params = {
        "lmt": "0",
        "klt": "101",
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
        "_": int(time.time() * 1000),
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://quote.eastmoney.com/",
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10,
                         proxies={"http": None, "https": None})
        r.raise_for_status()
        data = r.json()
        d = data.get("data")
        if not d:
            return None
        klines = d.get("klines", [])
        if not klines:
            return None

        # 最新一天
        last = str(klines[-1]).split(",")
        if len(last) < 13:
            return None

        # 最近5日主力净流入求和
        main_net_5d = 0.0
        for line in klines[-5:]:
            parts = str(line).split(",")
            if len(parts) >= 2:
                main_net_5d += _safe_float(parts[1])

        return {
            "code": str(d.get("code") or code),
            "name": str(d.get("name") or ""),
            "main_net_inflow": _safe_float(last[1]),
            "main_net_inflow_pct": _safe_float(last[6]),
            "super_net_inflow": _safe_float(last[5]),
            "big_net_inflow": _safe_float(last[4]),
            "mid_net_inflow": _safe_float(last[3]),
            "small_net_inflow": _safe_float(last[2]),
            "main_net_5d": main_net_5d,
        }
    except Exception as e:
        print(f"[sources_panwatch] get_capital_flow_detail failed: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# 5. 基本面快照 (腾讯 qt.gtimg.cn)
# ---------------------------------------------------------------------------

def get_fundamentals_snapshot(code: str) -> dict | None:
    """
    腾讯 qt.gtimg.cn 个股基本面快照 (PE/PB/市值)

    Returns
    -------
    {
        'code': '600519',
        'name': '贵州茅台',
        'pe_ttm': 19.77,
        'pe_static': 21.34,
        'pb': 6.04,
        'total_market_value': 16351.07,    # 亿元
        'circulating_market_value': 16351.07,  # 亿元
    }
    """
    code = code.replace("sh", "").replace("sz", "").replace(".", "")
    prefix = _cn_exchange_prefix(code)
    tencent_code = f"{prefix}{code}"
    url = f"https://qt.gtimg.cn/q={tencent_code}"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10,
                         proxies={"http": None, "https": None})
        r.encoding = "gbk"
        text = r.text
        if '=""' in text or not text.strip():
            return None

        # 解析 ~ 分隔数组
        _, value = text.split('="', 1)
        parts = value.rstrip('";\n').split("~")
        if len(parts) < 3:
            return None

        symbol = parts[2]
        if "." in symbol and not symbol.startswith("."):
            symbol = symbol.split(".")[0]

        name = parts[1] if len(parts) > 1 else ""
        pe_ttm = _safe_float(parts[39]) if len(parts) > 39 else None
        circ_mv = _safe_float(parts[44]) if len(parts) > 45 else None
        total_mv = _safe_float(parts[45]) if len(parts) > 45 else None
        pb = _safe_float(parts[46]) if len(parts) > 46 else None
        pe_static = _safe_float(parts[52]) if len(parts) > 52 else None

        return {
            "code": symbol,
            "name": name,
            "pe_ttm": pe_ttm,
            "pe_static": pe_static,
            "pb": pb,
            "total_market_value": total_mv,
            "circulating_market_value": circ_mv,
        }
    except Exception as e:
        print(f"[sources_panwatch] get_fundamentals_snapshot failed: {e}", file=sys.stderr)
        return None


def format_capital_flow(data: dict) -> str:
    """资金流向细分格式化"""
    if not data:
        return "资金流向数据获取失败"

    def _fmt_money(v: float) -> str:
        if abs(v) >= 1e8:
            return f"{v/1e8:.2f}亿"
        return f"{v/1e4:.2f}万"

    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"  资金流向细分: {data.get('code', '')} {data.get('name', '')}")
    lines.append(f"{'='*60}")
    main = data.get("main_net_inflow", 0)
    main_pct = data.get("main_net_inflow_pct", 0)
    status = "主力流入" if main > 0 else "主力流出"
    lines.append(f"  主力净流入: {_fmt_money(main)} ({main_pct:+.2f}%)  [{status}]")
    lines.append(f"  超大单: {_fmt_money(data.get('super_net_inflow', 0))}")
    lines.append(f"  大单:   {_fmt_money(data.get('big_net_inflow', 0))}")
    lines.append(f"  中单:   {_fmt_money(data.get('mid_net_inflow', 0))}")
    lines.append(f"  小单:   {_fmt_money(data.get('small_net_inflow', 0))}")
    lines.append(f"  5日主力净流入: {_fmt_money(data.get('main_net_5d', 0))}")
    lines.append(f"{'='*60}")
    return "\n".join(lines)


def format_fundamentals(data: dict) -> str:
    """基本面快照格式化"""
    if not data:
        return "基本面数据获取失败"
    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"  基本面快照: {data.get('code', '')} {data.get('name', '')}")
    lines.append(f"{'='*60}")
    lines.append(f"  PE(TTM): {data.get('pe_ttm')}")
    lines.append(f"  PE(静态): {data.get('pe_static')}")
    lines.append(f"  PB:      {data.get('pb')}")
    total = data.get('total_market_value')
    circ = data.get('circulating_market_value')
    if total is not None:
        lines.append(f"  总市值: {total:.2f} 亿")
    if circ is not None:
        lines.append(f"  流通市值: {circ:.2f} 亿")
    lines.append(f"{'='*60}")
    return "\n".join(lines)
