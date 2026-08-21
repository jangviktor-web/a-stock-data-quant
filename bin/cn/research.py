#!/usr/bin/env python3
"""research: per-name research for CN A-share + HK + ETF / 可转债
+ high-signal CN market events.

Provider: AKShare. Lazy-imported — install only if needed:

    uv sync --frozen   # at skill root; then invoke via `uv run scripts/research.py …`

Subcommands grouped by topic:

  Fundamentals:
    fundamentals CODE [--quarterly]    income/balance/cashflow + key ratios
    forecast [--date YYYYMMDD]         业绩预告 (earnings pre-announcement)
    flash    [--date YYYYMMDD]         业绩快报 (earnings flash)
    report-calendar [--date YYYYMMDD]  财报披露计划

  Events (high signal):
    lhb [--date YYYYMMDD]              龙虎榜 daily list
    lhb-stock CODE                     龙虎榜 history for one stock
    block-trade [--date YYYYMMDD]      大宗交易 daily list
    unlock [--month YYYY-MM]           限售解禁日历
    shareholder-count CODE             股东户数 history
    insider-trade [--date YYYYMMDD]    高管增减持
    buyback                            回购实施进展
    dividend [--code CODE]             分红送转

  Primary market:
    ipo-calendar                       新股申购日历 (next N days)
    ipo-winning [--year YYYY]          中签率历史

  ETF / 可转债:
    etf-list                           ETF universe
    etf-quote CODE                     single ETF quote + premium
    cb-list                            可转债 list with premium
    cb-quote CODE                      single 可转债 detail

Output: JSON to stdout. Errors: JSON {"error": "..."} with exit code 1.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, NoReturn


def die(msg: str, *, install: str | None = None, code: int = 1) -> NoReturn:
    payload: dict[str, Any] = {"error": msg}
    if install:
        payload["install"] = install
    print(json.dumps(payload, ensure_ascii=False))
    sys.exit(code)


def _ak():
    try:
        import akshare as ak  # type: ignore
    except ImportError:
        die("akshare not installed", install="uv sync --frozen   # at skill root, then re-invoke via `uv run scripts/research.py …`", code=2)
    return ak


def _df(df) -> list[dict[str, Any]]:
    """DataFrame → list-of-dicts; NaN/NaT/NA/'NaT' string → None; date-like → 'YYYY-MM-DD'."""
    if df is None:
        return []
    try:
        if hasattr(df, "empty") and df.empty:
            return []
        import math
        import pandas as pd
        df2 = df.copy()
        # Stringify any datetime-typed columns, preserving null as None.
        for col in df2.columns:
            ser = df2[col]
            try:
                if hasattr(ser.dtype, "kind") and ser.dtype.kind == "M":  # datetime64
                    df2[col] = ser.dt.strftime("%Y-%m-%d").where(ser.notna(), None)
            except Exception:
                pass
        records = df2.to_dict(orient="records")
        # df.where(notna, None) is unreliable on float columns — sanitize the
        # records dict directly so the JSON output is RFC-8259 valid.
        out = []
        for rec in records:
            clean = {}
            for k, v in rec.items():
                if v is None:
                    clean[k] = None
                elif isinstance(v, float) and math.isnan(v):
                    clean[k] = None
                elif v is pd.NaT or v == "NaT":
                    clean[k] = None
                else:
                    try:
                        if pd.isna(v):  # catches pd.NA, NaT, etc.
                            clean[k] = None
                            continue
                    except (TypeError, ValueError):
                        pass
                    clean[k] = v
            out.append(clean)
        return out
    except Exception:
        return []


def _market_prefix(code: str) -> str:
    """A-share code → 'sh'/'sz'/'bj' (北交所) — used by AKShare for some fns."""
    c = code.strip()
    if c.startswith(("60", "68", "9")):  # 上证主板 + 科创板 + B股
        return "sh"
    if c.startswith(("0", "30", "2")):  # 深证主板 + 创业板 + 深B
        return "sz"
    if c.startswith(("4", "8", "92")):  # 北交所
        return "bj"
    return "sh"


# ---- Fundamentals ----

def cmd_fundamentals(args):
    ak = _ak()
    code = args.code.strip()
    period = "report" if args.quarterly else "by_year"
    out: dict[str, Any] = {"code": code, "source": "akshare"}
    try:
        # Eastmoney F10 financial statements (annual + quarterly)
        if args.quarterly:
            income = ak.stock_profit_sheet_by_quarterly_em(symbol=f"{_market_prefix(code).upper()}{code}")
            balance = ak.stock_balance_sheet_by_quarterly_em(symbol=f"{_market_prefix(code).upper()}{code}")
            cashflow = ak.stock_cash_flow_sheet_by_quarterly_em(symbol=f"{_market_prefix(code).upper()}{code}")
        else:
            income = ak.stock_profit_sheet_by_yearly_em(symbol=f"{_market_prefix(code).upper()}{code}")
            balance = ak.stock_balance_sheet_by_yearly_em(symbol=f"{_market_prefix(code).upper()}{code}")
            cashflow = ak.stock_cash_flow_sheet_by_yearly_em(symbol=f"{_market_prefix(code).upper()}{code}")
        out["income_statement"] = _df(income)
        out["balance_sheet"] = _df(balance)
        out["cash_flow"] = _df(cashflow)
    except Exception as e:
        out["error"] = f"financial sheets fetch failed: {type(e).__name__}: {e}"
    # Key ratios
    try:
        out["key_metrics"] = _df(ak.stock_financial_abstract_ths(symbol=code))
    except Exception:
        pass
    return out


def cmd_forecast(args):
    ak = _ak()
    fn = ak.stock_yjyg_em  # 业绩预告
    try:
        df = fn(date=args.date) if args.date else fn()
    except TypeError:
        df = fn()
    return {"date": args.date, "rows": _df(df), "source": "akshare"}


def cmd_flash(args):
    ak = _ak()
    fn = ak.stock_yjkb_em  # 业绩快报
    try:
        df = fn(date=args.date) if args.date else fn()
    except TypeError:
        df = fn()
    return {"date": args.date, "rows": _df(df), "source": "akshare"}


def cmd_report_calendar(args):
    ak = _ak()
    fn = ak.stock_yysj_em  # 财报披露计划
    try:
        df = fn(date=args.date) if args.date else fn()
    except TypeError:
        df = fn()
    return {"date": args.date, "rows": _df(df), "source": "akshare"}


# ---- Events ----

def cmd_lhb(args):
    ak = _ak()
    if args.date:
        df = ak.stock_lhb_detail_em(start_date=args.date, end_date=args.date)
    else:
        df = ak.stock_lhb_detail_em()
    return {"date": args.date, "rows": _df(df), "source": "akshare"}


def cmd_lhb_stock(args):
    ak = _ak()
    # stock_lhb_stock_detail_date_em returns the dates on which this stock
    # appeared on 龙虎榜. To get the per-event detail, the caller passes a
    # specific date via the lhb-detail subcommand (not exposed yet — drill
    # via ak.stock_lhb_stock_detail_em(symbol, date, flag) if needed).
    df = ak.stock_lhb_stock_detail_date_em(symbol=args.code)
    return {"code": args.code, "appearances": _df(df), "source": "akshare"}


def cmd_block_trade(args):
    ak = _ak()
    if args.date:
        df = ak.stock_dzjy_mrmx(start_date=args.date, end_date=args.date)
    else:
        df = ak.stock_dzjy_mrmx()
    return {"date": args.date, "rows": _df(df), "source": "akshare"}


def cmd_unlock(args):
    ak = _ak()
    fn = ak.stock_restricted_release_summary_em
    df = fn(date=args.month) if args.month else fn()
    return {"month": args.month, "rows": _df(df), "source": "akshare"}


def cmd_shareholder_count(args):
    ak = _ak()
    df = ak.stock_zh_a_gdhs_detail_em(symbol=args.code)
    return {"code": args.code, "rows": _df(df), "source": "akshare"}


def cmd_insider_trade(args):
    ak = _ak()
    # 高管增减持 — stock_ggcg_em returns 全部 history (~150k rows). Slice to
    # the requested date or, when --date omitted, the last 30 days to keep
    # the response usable. Use --date YYYY-MM-DD to pin one day.
    df = ak.stock_ggcg_em(symbol="全部")
    if df is not None and not df.empty and "公告日" in df.columns:
        if args.date:
            df = df[df["公告日"].astype(str) == args.date]
        else:
            import datetime as _dt
            cutoff = (_dt.date.today() - _dt.timedelta(days=30)).isoformat()
            df = df[df["公告日"].astype(str) >= cutoff]
    return {"date": args.date, "rows": _df(df), "source": "akshare"}


def cmd_buyback(args):
    ak = _ak()
    df = ak.stock_repurchase_em()
    return {"rows": _df(df), "source": "akshare"}


def cmd_dividend(args):
    ak = _ak()
    if args.code:
        df = ak.stock_fhps_detail_em(symbol=args.code)
        return {"code": args.code, "rows": _df(df), "source": "akshare"}
    df = ak.stock_fhps_em()
    return {"rows": _df(df), "source": "akshare"}


# ---- Primary market ----

def cmd_ipo_calendar(args):
    """Upcoming + recent IPOs (申购 calendar). One dataset filtered by date side."""
    ak = _ak()
    df = ak.stock_xgsglb_em(symbol="全部股票")
    import datetime as _dt
    today = _dt.date.today().isoformat()
    # Future or today's 申购日期 only → "upcoming"
    upcoming = df[df["申购日期"].astype(str) >= today] if "申购日期" in df.columns else df
    return {"rows": _df(upcoming), "source": "akshare"}


def cmd_ipo_winning(args):
    """Past IPOs with 中签率 already published (results). Filterable by --year."""
    ak = _ak()
    df = ak.stock_xgsglb_em(symbol="全部股票")
    if "中签率" in df.columns:
        df = df[df["中签率"].notna()]
    if args.year and "申购日期" in df.columns:
        df = df[df["申购日期"].astype(str).str.startswith(str(args.year))]
    return {"year": args.year, "rows": _df(df), "source": "akshare"}


# ---- ETF / CB ----

def cmd_etf_list(args):
    ak = _ak()
    df = ak.fund_etf_category_sina(symbol="ETF基金")
    return {"rows": _df(df), "source": "akshare"}


def cmd_etf_quote(args):
    ak = _ak()
    try:
        df = ak.fund_etf_spot_em()
        match = df[df["代码"] == args.code]
        return {"code": args.code, "row": _df(match)[0] if not match.empty else None, "source": "akshare"}
    except Exception as e:
        return {"code": args.code, "error": f"{type(e).__name__}: {e}"}


def cmd_cb_list(args):
    ak = _ak()
    df = ak.bond_cb_jsl()
    return {"rows": _df(df), "source": "akshare"}


def cmd_cb_quote(args):
    ak = _ak()
    df = ak.bond_cb_jsl()
    # JSL column is 代码 (the 6-digit bond code, e.g. 113008).
    match = df[df["代码"] == args.code]
    return {"code": args.code, "row": _df(match)[0] if not match.empty else None, "source": "akshare"}


# ---- CLI ----

def main() -> None:
    p = argparse.ArgumentParser(prog="research.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name: str, help_: str, func, *fields):
        sp = sub.add_parser(name, help=help_)
        for fn in fields:
            fn(sp)
        sp.set_defaults(func=func)

    # Fundamentals
    add("fundamentals", "income/balance/cashflow for a CN A-share code",
        cmd_fundamentals,
        lambda sp: sp.add_argument("code"),
        lambda sp: sp.add_argument("--quarterly", action="store_true"))
    add("forecast", "业绩预告 (earnings pre-announcement) for a quarter",
        cmd_forecast,
        lambda sp: sp.add_argument("--date", help="YYYYMMDD (period end)"))
    add("flash", "业绩快报 (earnings flash) for a quarter",
        cmd_flash,
        lambda sp: sp.add_argument("--date"))
    add("report-calendar", "财报披露计划",
        cmd_report_calendar,
        lambda sp: sp.add_argument("--date"))

    # Events
    add("lhb", "龙虎榜 daily list",
        cmd_lhb,
        lambda sp: sp.add_argument("--date", help="YYYYMMDD"))
    add("lhb-stock", "龙虎榜 history for one stock",
        cmd_lhb_stock,
        lambda sp: sp.add_argument("code"))
    add("block-trade", "大宗交易 daily list",
        cmd_block_trade,
        lambda sp: sp.add_argument("--date"))
    add("unlock", "限售解禁 summary for a month",
        cmd_unlock,
        lambda sp: sp.add_argument("--month", help="YYYYMM"))
    add("shareholder-count", "股东户数 history for a stock",
        cmd_shareholder_count,
        lambda sp: sp.add_argument("code"))
    add("insider-trade", "高管增减持 recent",
        cmd_insider_trade,
        lambda sp: sp.add_argument("--date"))
    add("buyback", "回购实施进展", cmd_buyback)
    add("dividend", "分红送转",
        cmd_dividend,
        lambda sp: sp.add_argument("--code", help="single-stock detail; omit for market-wide list"))

    # Primary
    add("ipo-calendar", "新股申购日历", cmd_ipo_calendar)
    add("ipo-winning", "中签率历史",
        cmd_ipo_winning,
        lambda sp: sp.add_argument("--year", help="YYYY"))

    # ETF / CB
    add("etf-list", "ETF universe", cmd_etf_list)
    add("etf-quote", "single-ETF quote + premium",
        cmd_etf_quote,
        lambda sp: sp.add_argument("code"))
    add("cb-list", "可转债 list with premium", cmd_cb_list)
    add("cb-quote", "single 可转债 detail",
        cmd_cb_quote,
        lambda sp: sp.add_argument("code"))

    args = p.parse_args()
    try:
        out = args.func(args)
    except SystemExit:
        raise
    except Exception as e:
        die(f"{type(e).__name__}: {e}")
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
