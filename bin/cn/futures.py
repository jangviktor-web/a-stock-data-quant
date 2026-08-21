#!/usr/bin/env python3
"""futures: front-month quotes for CN onshore commodity futures
(SHFE, DCE, CZCE, INE, GFEX).

Keyless. Provider:
  - futsseapi.eastmoney.com/static/{sc}_{cont}_qt   (Eastmoney futures qt)

For global futures (NYMEX/COMEX/CBOT/CME/CFE), use global-markets/scripts/futures.py.

Output: JSON to stdout. Errors: JSON {"error": "..."} with exit code 1.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any, NoReturn

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
TIMEOUT = 12
EM_STATIC = "http://futsseapi.eastmoney.com/static/{sc}_{dm}_qt"

# CN main-continuous code conventions:
#   SHFE/DCE/INE/GFEX: lowercase root + "m"  (e.g. cum, rbm, im, scm, lcm)
#   CZCE:              uppercase root + "M"  (e.g. SRM, FGM, SAM)
CATALOG: dict[str, dict[str, Any]] = {
    # SHFE
    "cu":  {"name": "SHFE Copper",            "exchange": "SHFE", "sc": 113, "cont": "cum"},
    "al":  {"name": "SHFE Aluminum",          "exchange": "SHFE", "sc": 113, "cont": "alm"},
    "au":  {"name": "SHFE Gold",              "exchange": "SHFE", "sc": 113, "cont": "aum"},
    "ag":  {"name": "SHFE Silver",            "exchange": "SHFE", "sc": 113, "cont": "agm"},
    "rb":  {"name": "SHFE Rebar",             "exchange": "SHFE", "sc": 113, "cont": "rbm"},
    "hc":  {"name": "SHFE Hot-rolled Coil",   "exchange": "SHFE", "sc": 113, "cont": "hcm"},
    # DCE
    "i":   {"name": "DCE Iron Ore",           "exchange": "DCE",  "sc": 114, "cont": "im"},
    "m":   {"name": "DCE Soybean Meal",       "exchange": "DCE",  "sc": 114, "cont": "mm"},
    "p":   {"name": "DCE Palm Oil",           "exchange": "DCE",  "sc": 114, "cont": "pm"},
    "c":   {"name": "DCE Corn",               "exchange": "DCE",  "sc": 114, "cont": "cm"},
    # CZCE
    "SR":  {"name": "CZCE Sugar",             "exchange": "CZCE", "sc": 115, "cont": "SRM"},
    "CF":  {"name": "CZCE Cotton",            "exchange": "CZCE", "sc": 115, "cont": "CFM"},
    "TA":  {"name": "CZCE PTA",               "exchange": "CZCE", "sc": 115, "cont": "TAM"},
    "MA":  {"name": "CZCE Methanol",          "exchange": "CZCE", "sc": 115, "cont": "MAM"},
    "FG":  {"name": "CZCE Glass",             "exchange": "CZCE", "sc": 115, "cont": "FGM"},
    "SA":  {"name": "CZCE Soda Ash",          "exchange": "CZCE", "sc": 115, "cont": "SAM"},
    # INE
    "sc":  {"name": "INE Crude",              "exchange": "INE",  "sc": 142, "cont": "scm"},
    # GFEX
    "lc":  {"name": "GFEX Lithium Carbonate", "exchange": "GFEX", "sc": 225, "cont": "lcm"},
}


def die(msg: str, code: int = 1) -> NoReturn:
    print(json.dumps({"error": msg}, ensure_ascii=False))
    sys.exit(code)


def _get_json(url: str) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def em_quote_one(sc: int, cont: str) -> dict[str, Any] | None:
    url = EM_STATIC.format(sc=sc, dm=cont)
    try:
        j = _get_json(url)
    except (urllib.error.URLError, OSError):
        return None
    qt = j.get("qt") if isinstance(j, dict) else None
    if not qt or qt.get("p") in (None, 0, "-"):
        return None
    return {
        "name": qt.get("name"),
        "code": qt.get("dm"),
        "price": qt.get("p"),
        "open": qt.get("o"),
        "high": qt.get("h"),
        "low": qt.get("l"),
        "prev_close": qt.get("zjsj"),
        "change": qt.get("zde"),
        "pct": qt.get("zdf"),
        "volume": qt.get("vol"),
        "open_interest": qt.get("ccl"),
        "source": "eastmoney",
    }


def cmd_quote(args):
    aliases = [a.strip() for a in args.aliases.split(",") if a.strip()]
    out = []
    for a in aliases:
        entry = CATALOG.get(a)
        if not entry:
            out.append({"alias": a, "error": "unknown contract alias"})
            continue
        row = em_quote_one(entry["sc"], entry["cont"])
        if row is None:
            row = {"alias": a, "error": "eastmoney unavailable"}
        row.setdefault("alias", a)
        row.setdefault("desc", entry["name"])
        out.append(row)
    return out


def cmd_list(args):
    return [
        {
            "alias": alias,
            "name": e["name"],
            "exchange": e["exchange"],
            "eastmoney_code": e["cont"],
        }
        for alias, e in CATALOG.items()
    ]


def main() -> None:
    p = argparse.ArgumentParser(prog="futures.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    pq = sub.add_parser("quote", help="front-month quote for one or more contract aliases")
    pq.add_argument("aliases", help="comma-separated aliases (e.g. cu,rb,SR,lc). See `list`.")
    pq.set_defaults(func=cmd_quote)
    pl = sub.add_parser("list", help="list supported CN onshore contract aliases")
    pl.set_defaults(func=cmd_list)
    args = p.parse_args()
    try:
        out = args.func(args)
    except urllib.error.HTTPError as e:
        die(f"http {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        die(f"network: {e.reason}")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
