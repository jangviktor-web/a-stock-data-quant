#!/usr/bin/env python3
"""options: CN ETF options (上交所 / 深交所) + CFFEX index
options (沪深 300、中证 1000、上证 50).

Provider: AKShare. Lazy-imported — install only if needed:

    uv sync --frozen   # at skill root; then invoke via `uv run scripts/options.py …`

Subcommands:
  underlyings              list option underlyings (stdlib; no akshare needed)
  expiries CODE            list listed expiry months for an underlying
  chain CODE --expiry M    full chain for one expiry month
                           ETF: YYYYMM or YYMM ; CFFEX: YYYYMM or YYMM
  pcr CODE                 put/call ratio + IV summary (上交所 / Eastmoney)

Output: JSON to stdout. Errors: JSON {"error": "..."} with exit code 1.
"""
from __future__ import annotations

import argparse
import json
import math
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
        die("akshare not installed", install="uv sync --frozen   # at skill root, then re-invoke via `uv run scripts/options.py …`", code=2)
    return ak


def _df(df) -> list[dict[str, Any]]:
    """DataFrame → list-of-dicts; NaN/NaT → None."""
    if df is None:
        return []
    try:
        if hasattr(df, "empty") and df.empty:
            return []
        import pandas as pd
        df2 = df.copy()
        for col in df2.columns:
            ser = df2[col]
            try:
                if hasattr(ser.dtype, "kind") and ser.dtype.kind == "M":
                    df2[col] = ser.dt.strftime("%Y-%m-%d").where(ser.notna(), None)
            except Exception:
                pass
        records = df2.to_dict(orient="records")
        out = []
        for rec in records:
            clean = {}
            for k, v in rec.items():
                if v is None:
                    clean[k] = None
                elif isinstance(v, float) and math.isnan(v):
                    clean[k] = None
                else:
                    try:
                        if pd.isna(v):
                            clean[k] = None
                            continue
                    except (TypeError, ValueError):
                        pass
                    clean[k] = v
            out.append(clean)
        return out
    except Exception:
        return []


# ETF underlying code → (exchange, akshare 期权 product name).
# `product` is the value to pass to ak.option_finance_board(symbol=...).
# Only underlyings actually wired in AKShare are listed. 510500 / 159* don't
# have a clean board endpoint — added as best-effort with a clear error path.
ETF_UNDERLYINGS = {
    "510050": ("上交所", "华夏上证50ETF期权"),
    "510300": ("上交所", "华泰柏瑞沪深300ETF期权"),
    "510500": ("上交所", "南方中证500ETF期权"),
    "588000": ("上交所", "华夏科创50ETF期权"),
    "588080": ("上交所", "易方达科创50ETF期权"),
    "159919": ("深交所", "嘉实沪深300ETF期权"),
    # 159915 (创业板ETF), 159922 (中证500ETF深), 159901 (深100ETF) listed on
    # SZSE but not exposed by `option_finance_board`. Surfaced for awareness
    # only; expiries/chain return a "not supported" error rather than crash.
    "159915": ("深交所", None),
    "159922": ("深交所", None),
    "159901": ("深交所", None),
}

# CFFEX index options: code → (display name, list-fn name, spot-fn name).
CFFEX_UNDERLYINGS = {
    "IO": ("沪深300指数", "option_cffex_hs300_list_sina",  "option_cffex_hs300_spot_sina"),
    "MO": ("中证1000指数", "option_cffex_zz1000_list_sina", "option_cffex_zz1000_spot_sina"),
    "HO": ("上证50指数",  "option_cffex_sz50_list_sina",   "option_cffex_sz50_spot_sina"),
}


def _yymm(expiry: str) -> str:
    """Accept YYYYMM or YYMM; return YYMM (akshare's expected form)."""
    expiry = expiry.strip()
    if len(expiry) == 6 and expiry.isdigit():
        return expiry[2:]
    if len(expiry) == 4 and expiry.isdigit():
        return expiry
    die(f"invalid expiry {expiry!r}; expected YYYYMM or YYMM")


def _sse_list_symbol(code: str) -> str | None:
    """SSE list-fn only knows '50ETF' / '300ETF' / '500ETF' / '科创50ETF'."""
    return {
        "510050": "50ETF",
        "510300": "300ETF",
        "510500": "500ETF",
        "588000": "科创50ETF",
        "588080": "科创板50ETF",
    }.get(code)


def cmd_underlyings(args):
    return {
        "etf_options": [
            {"code": c, "exchange": ex, "product": prod}
            for c, (ex, prod) in ETF_UNDERLYINGS.items()
        ],
        "cffex_index_options": [
            {"code": c, "underlying": name}
            for c, (name, _, _) in CFFEX_UNDERLYINGS.items()
        ],
    }


def cmd_expiries(args):
    ak = _ak()
    code = args.code
    if code in ETF_UNDERLYINGS:
        sym = _sse_list_symbol(code)
        if not sym:
            return {"code": code, "expiries": [], "error": "SSE/SZSE list endpoint does not cover this ETF; query chain directly with --expiry"}
        try:
            months = ak.option_sse_list_sina(symbol=sym)
        except Exception as e:
            return {"code": code, "error": f"{type(e).__name__}: {e}"}
        return {"code": code, "product": sym, "expiries": list(months), "source": "akshare"}
    if code in CFFEX_UNDERLYINGS:
        name, list_fn, _ = CFFEX_UNDERLYINGS[code]
        try:
            obj = getattr(ak, list_fn)()
        except Exception as e:
            return {"code": code, "error": f"{type(e).__name__}: {e}"}
        # Returns {underlying_name: [contract_ids...]}; extract distinct YYMM
        contracts = next(iter(obj.values())) if isinstance(obj, dict) and obj else []
        # e.g. 'io2606' → '2606'
        expiries = sorted({c[-4:] for c in contracts if c[-4:].isdigit()})
        return {"code": code, "underlying": name, "expiries": expiries, "contracts": contracts, "source": "akshare"}
    return {"code": code, "error": "unknown underlying — run `underlyings`"}


def cmd_chain(args):
    ak = _ak()
    code = args.code
    if not args.expiry:
        return {"code": code, "error": "chain requires --expiry YYYYMM or YYMM"}
    expiry = _yymm(args.expiry)
    if code in ETF_UNDERLYINGS:
        _, product = ETF_UNDERLYINGS[code]
        if not product:
            return {"code": code, "error": f"ETF {code} chain not exposed by AKShare option_finance_board"}
        try:
            df = ak.option_finance_board(symbol=product, end_month=expiry)
        except Exception as e:
            return {"code": code, "expiry": expiry, "error": f"{type(e).__name__}: {e}"}
        return {"code": code, "product": product, "expiry": expiry, "rows": _df(df), "source": "akshare"}
    if code in CFFEX_UNDERLYINGS:
        name, _, spot_fn = CFFEX_UNDERLYINGS[code]
        try:
            # CFFEX spot-fn expects e.g. 'io2606' (lowercase code + YYMM)
            df = getattr(ak, spot_fn)(symbol=f"{code.lower()}{expiry}")
        except Exception as e:
            return {"code": code, "expiry": expiry, "error": f"{type(e).__name__}: {e}"}
        return {"code": code, "underlying": name, "expiry": expiry, "rows": _df(df), "source": "akshare"}
    return {"code": code, "error": "unknown underlying"}


def cmd_pcr(args):
    ak = _ak()
    code = args.code
    # Eastmoney 期权价值分析: no args; one row per *contract*. We filter by
    # 标的代码 ≈ args.code. Returns IV + theoretical value; no explicit PCR.
    try:
        df = ak.option_value_analysis_em()
    except Exception as e:
        return {"code": code, "error": f"{type(e).__name__}: {e}"}
    if df is None or df.empty:
        return {"code": code, "rows": [], "source": "akshare"}
    # Schema varies; filter on whichever column looks like a underlying code.
    for col in ("标的代码", "标的名称", "期权代码", "合约代码"):
        if col in df.columns:
            df = df[df[col].astype(str).str.contains(code, na=False)]
            break
    return {"code": code, "rows": _df(df), "source": "akshare"}


def main() -> None:
    p = argparse.ArgumentParser(prog="options.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("underlyings", help="list option underlyings").set_defaults(func=cmd_underlyings)

    pe = sub.add_parser("expiries", help="list listed expiry months for an underlying")
    pe.add_argument("code")
    pe.set_defaults(func=cmd_expiries)

    pc = sub.add_parser("chain", help="full chain for one expiry")
    pc.add_argument("code")
    pc.add_argument("--expiry", help="YYYYMM or YYMM", required=True)
    pc.set_defaults(func=cmd_chain)

    pp = sub.add_parser("pcr", help="put/call ratio + IV summary (ETF only)")
    pp.add_argument("code")
    pp.set_defaults(func=cmd_pcr)

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
