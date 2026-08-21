#!/usr/bin/env python3
"""macro: Chinese macroeconomic indicators.

Provider: AKShare. Lazy-imported — install only if needed:

    uv sync --frozen   # at skill root; then invoke via `uv run scripts/macro.py …`

Subcommands (all return JSON time series):
  cpi                     CPI 同比/环比 (consumer price)
  ppi                     PPI 同比/环比 (producer price)
  gdp                     GDP 增速 (quarterly)
  m0m1m2                  M0/M1/M2 money supply
  pmi-mfg                 制造业 PMI
  pmi-non-mfg             非制造业 PMI
  pmi-caixin              财新 PMI
  social-financing        社融 (total social financing)
  fiscal                  财政收支 (fiscal revenue / expenditure)
  lpr                     LPR (loan prime rate) 历史
  shibor                  SHIBOR 隔夜 / 1W / 1M / 3M / 6M / 1Y
  industrial              工业增加值
  retail                  社会消费品零售
  fixed-asset             固定资产投资
  pmi-energy              央行公开市场操作 (OMO) reverse-repo balance / MLF
  reserve-rate            存款准备金率历史
  treasury-yield          国债收益率曲线 (1M, 3M, 6M, 1Y, 3Y, 5Y, 7Y, 10Y, 30Y)

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
        die("akshare not installed", install="uv sync --frozen   # at skill root, then re-invoke via `uv run scripts/macro.py …`", code=2)
    return ak


def _df(df) -> list[dict[str, Any]]:
    """DataFrame → list-of-dicts; NaN/NaT → None; date cols → 'YYYY-MM-DD'."""
    if df is None:
        return []
    try:
        if hasattr(df, "empty") and df.empty:
            return []
        import math
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


# (subcmd, akshare-fn-name) pairs that take no args and return a DataFrame.
SIMPLE = {
    "cpi": "macro_china_cpi_yearly",
    "ppi": "macro_china_ppi_yearly",
    "gdp": "macro_china_gdp_yearly",
    "m0m1m2": "macro_china_money_supply",
    "pmi-mfg": "macro_china_pmi_yearly",
    "pmi-non-mfg": "macro_china_non_man_pmi",
    "pmi-caixin": "macro_china_cx_pmi_yearly",
    "social-financing": "macro_china_shrzgm",
    "fiscal": "macro_china_fx_reserves_yearly",
    "lpr": "macro_china_lpr",
    "shibor": "rate_interbank",
    "industrial": "macro_china_industrial_production_yoy",
    "retail": "macro_china_consumer_goods_retail",
    "fixed-asset": "macro_china_gdzctz",
    "reserve-rate": "macro_china_reserve_requirement_ratio",
    "treasury-yield": "bond_china_yield",
}


def cmd_simple(args):
    ak = _ak()
    fn_name = SIMPLE[args.cmd]
    fn = getattr(ak, fn_name, None)
    if fn is None:
        return {"error": f"AKShare function {fn_name} not found in installed version", "cmd": args.cmd}
    try:
        df = fn()
    except Exception as e:
        return {"cmd": args.cmd, "error": f"{type(e).__name__}: {e}"}
    return {"cmd": args.cmd, "akshare_fn": fn_name, "rows": _df(df), "source": "akshare"}


def main() -> None:
    p = argparse.ArgumentParser(prog="macro.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in SIMPLE:
        sp = sub.add_parser(name, help=f"AKShare: {SIMPLE[name]}()")
        sp.set_defaults(func=cmd_simple, cmd=name)
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
