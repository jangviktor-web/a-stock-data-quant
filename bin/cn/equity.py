#!/usr/bin/env python3
"""cn-equities skill: A-share + HK quotes, history, indices, plus CN-only signals
(northbound flow, limit up/down, industry/concept boards).

Keyless. Sources:
  - hq.sinajs.cn                Sina realtime A-share/HK quotes (GBK-encoded names)
  - push2.eastmoney.com         Realtime quotes, indices, sector lists, fund flows
  - push2his.eastmoney.com      Daily kline history
  - searchapi.eastmoney.com     Search by name/code
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from typing import Any, NoReturn

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
SINA_REFERER = "https://finance.sina.com.cn"
TIMEOUT = 15

SINA_QUOTE = "https://hq.sinajs.cn/list="
TENCENT_QUOTE = "https://qt.gtimg.cn/q="
EM_QUOTE = "https://push2.eastmoney.com/api/qt/stock/get"
EM_KLINE = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
EM_SEARCH = "https://searchapi.eastmoney.com/api/suggest/get"
EM_CLIST = "https://push2.eastmoney.com/api/qt/clist/get"
# Same path on the *delay* shard returns 15-min-delayed data — used as fallback
# when push2.eastmoney.com refuses connections (per-IP rate limit).
EM_CLIST_DELAY = "https://push2delay.eastmoney.com/api/qt/clist/get"
EM_KAMT = "https://push2.eastmoney.com/api/qt/kamt/get"
YH_CHART = "https://query1.finance.yahoo.com/v8/finance/chart"

# Index alias → Yahoo symbol (HSI variants only — A-share indices like 上证综指
# don't reliably resolve on Yahoo).
YH_INDEX_FROM_ALIAS = {
    "HSI": "^HSI",
    "HSCEI": "^HSCE",
    "HSTECH": "^HSTECH",
}

# Eastmoney quote fields. f59 is the price-scale exponent (US/HK=3, CN=2). f152 is
# the *display* decimals — do NOT use as scale; it under-scales by 10x for US/HK.
EM_QUOTE_FIELDS = "f43,f44,f45,f46,f47,f48,f57,f58,f59,f60,f168,f169,f170"

# Index name → Eastmoney secid
INDEX_ALIASES = {
    "SSE": "1.000001",      # 上证综指
    "SHCOMP": "1.000001",
    "SHANGHAI": "1.000001",
    "SZSE": "0.399001",     # 深证成指
    "SHENZHEN": "0.399001",
    "CSI300": "1.000300",   # 沪深300
    "HS300": "1.000300",
    "CSI500": "1.000905",   # 中证500
    "CSI1000": "1.000852",  # 中证1000
    "CHINEXT": "0.399006",  # 创业板指
    "GEM": "0.399006",
    "STAR50": "1.000688",   # 科创50
    "STAR": "1.000688",
    "KECHUANG50": "1.000688",
    "HSI": "100.HSI",       # 恒生指数
    "HANGSENG": "100.HSI",
    "HSCEI": "100.HSCEI",   # 恒生中国企业指数 (国企指数)
    "HSTECH": "100.HSTECH", # 恒生科技指数
}


# ---------- Helpers ----------


def die(msg: str, code: int = 1) -> NoReturn:
    print(json.dumps({"error": msg}), file=sys.stdout)
    sys.exit(code)


def http_text(url: str, *, referer: str | None = None, encoding: str = "utf-8") -> str:
    headers = {
        "User-Agent": UA,
        "Accept": "*/*",
        # Eastmoney's WAF/CDN sometimes drops keep-alived urllib sockets mid-response.
        # Forcing Connection: close costs one TCP handshake per call but is reliable.
        "Connection": "close",
    }
    if referer:
        headers["Referer"] = referer
    req = urllib.request.Request(url, headers=headers)
    # No retry: a 4xx/5xx or RemoteDisconnected usually means rate-limited or
    # WAF-blocked; hammering makes it worse. Fallback chains in callers handle it.
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read()
    return raw.decode(encoding, errors="replace")


def http_json(url: str) -> Any:
    return json.loads(http_text(url))


def resolve_range(args: argparse.Namespace) -> tuple[date, date]:
    today = date.today()
    if getattr(args, "days", None):
        return today - timedelta(days=args.days), today
    if not args.from_date or not args.to_date:
        die("must pass --from YYYY-MM-DD --to YYYY-MM-DD or --days N")
    return (
        datetime.strptime(args.from_date, "%Y-%m-%d").date(),
        datetime.strptime(args.to_date, "%Y-%m-%d").date(),
    )


# ---------- Market detection ----------


def detect_market(code: str) -> str:
    """Return one of: 'sh', 'sz', 'bj', 'hk'."""
    c = code.strip().upper().lstrip("0").zfill(0) or code
    if code.isdigit():
        if len(code) == 6:
            if code[0] == "6":
                return "sh"
            if code.startswith(("688",)):
                return "sh"  # STAR Market, but Sina still uses 'sh'
            if code[0] in ("0", "3"):
                return "sz"
            if code[0] in ("4", "8"):
                return "bj"
        if len(code) == 5:
            return "hk"
        if len(code) < 5:
            return "hk"
    die(f"can't detect market for code '{code}'")


def sina_symbol(code: str) -> str:
    mkt = detect_market(code)
    if mkt == "hk":
        return f"hk{code.zfill(5)}"
    return f"{mkt}{code}"


def eastmoney_secid(code: str) -> str:
    mkt = detect_market(code)
    if mkt == "sh":
        return f"1.{code}"
    if mkt == "sz":
        return f"0.{code}"
    if mkt == "bj":
        # Beijing exchange uses 0. with the code; Eastmoney has discrete handling
        return f"0.{code}"
    if mkt == "hk":
        return f"116.{code.zfill(5)}"
    die(f"no eastmoney secid for market '{mkt}'")


# ---------- Sina quote (A-share + HK, batched) ----------

_SINA_RE = re.compile(r'var hq_str_([^=]+)="([^"]*)";?')


def _parse_sina_a_share(symbol: str, fields: list[str]) -> dict[str, Any] | None:
    # Sina A-share schema (32+ fields):
    # 0=name, 1=open, 2=prev_close, 3=last, 4=high, 5=low, 6=bid1, 7=ask1,
    # 8=volume, 9=amount, then bid/ask 5-level pairs, 30=date, 31=time, 32=status?
    if len(fields) < 32 or not fields[0]:
        return None
    try:
        return {
            "symbol": symbol[2:],  # strip 'sh'/'sz' prefix
            "name": fields[0],
            "market": symbol[:2],
            "open": float(fields[1]),
            "prev_close": float(fields[2]),
            "price": float(fields[3]),
            "high": float(fields[4]),
            "low": float(fields[5]),
            "volume": int(fields[8]) if fields[8] else None,
            "amount": float(fields[9]) if fields[9] else None,
            "change": round(float(fields[3]) - float(fields[2]), 3),
            "pct": round((float(fields[3]) - float(fields[2])) / float(fields[2]) * 100, 2)
            if float(fields[2]) > 0 else None,
            "ts": f"{fields[30]} {fields[31]}" if len(fields) > 31 else None,
            "source": "sina",
        }
    except (ValueError, IndexError):
        return None


def _parse_sina_hk(symbol: str, fields: list[str]) -> dict[str, Any] | None:
    # Sina HK schema (~18 fields):
    # 0=english_name, 1=chinese_name, 2=open, 3=prev_close, 4=high, 5=low,
    # 6=last, 7=change, 8=pct, 9=bid, 10=ask, 11=amount, 12=volume, 13=?, 14=?,
    # 15=year_high, 16=year_low, 17=date, 18=time
    if len(fields) < 17 or not fields[1]:
        return None
    try:
        return {
            "symbol": symbol[2:],
            "name": fields[1],
            "name_en": fields[0],
            "market": "hk",
            "open": float(fields[2]),
            "prev_close": float(fields[3]),
            "high": float(fields[4]),
            "low": float(fields[5]),
            "price": float(fields[6]),
            "change": float(fields[7]) if fields[7] else None,
            "pct": float(fields[8]) if fields[8] else None,
            "amount": float(fields[11]) if fields[11] else None,
            "volume": int(fields[12]) if fields[12] else None,
            "ts": f"{fields[17]} {fields[18]}" if len(fields) > 18 else None,
            "source": "sina",
        }
    except (ValueError, IndexError):
        return None


def sina_quote_batch(codes: list[str]) -> list[dict[str, Any]]:
    symbols = [sina_symbol(c) for c in codes]
    url = SINA_QUOTE + ",".join(symbols)
    text = http_text(url, referer=SINA_REFERER, encoding="gbk")
    by_symbol: dict[str, list[str]] = {}
    for match in _SINA_RE.finditer(text):
        sym, payload = match.group(1), match.group(2)
        by_symbol[sym] = payload.split(",")
    out: list[dict[str, Any]] = []
    for sym in symbols:
        fields = by_symbol.get(sym)
        if fields is None or not fields[0]:
            out.append({"symbol": sym, "error": "no data"})
            continue
        parsed = (
            _parse_sina_hk(sym, fields) if sym.startswith("hk")
            else _parse_sina_a_share(sym, fields)
        )
        out.append(parsed or {"symbol": sym, "error": "parse failed"})
    return out


# ---------- Tencent quote (A-share + HK, batched) ----------

_TENCENT_RE = re.compile(r'v_([^=]+)="([^"]*)";?')


def _parse_tencent_a_share(symbol: str, fields: list[str]) -> dict[str, Any] | None:
    # Tencent A-share schema (~50 fields, '~'-separated):
    # 0=mkt, 1=name, 2=code, 3=last, 4=open, 5=prev_close, 6=volume(手),
    # 30=ts YYYYMMDDhhmmss, 31=change, 32=pct, 33=high, 34=low
    if len(fields) < 35 or not fields[1]:
        return None
    try:
        last = float(fields[3])
        prev = float(fields[5])
        ts_raw = fields[30] if len(fields) > 30 else ""
        ts = (
            f"{ts_raw[0:4]}-{ts_raw[4:6]}-{ts_raw[6:8]} "
            f"{ts_raw[8:10]}:{ts_raw[10:12]}:{ts_raw[12:14]}"
            if len(ts_raw) >= 14 else ts_raw
        )
        return {
            "symbol": symbol[2:],
            "name": fields[1],
            "market": symbol[:2],
            "open": float(fields[4]),
            "prev_close": prev,
            "price": last,
            "high": float(fields[33]),
            "low": float(fields[34]),
            "volume": int(float(fields[6])) * 100 if fields[6] else None,  # 手 → shares
            "change": float(fields[31]) if fields[31] else round(last - prev, 3),
            "pct": float(fields[32]) if fields[32] else None,
            "ts": ts,
            "source": "tencent",
        }
    except (ValueError, IndexError):
        return None


def _parse_tencent_hk(symbol: str, fields: list[str]) -> dict[str, Any] | None:
    # Tencent HK schema:
    # 0=mkt, 1=name, 2=code, 3=last, 4=prev_close, 5=open, 6=volume(shares),
    # 30=ts YYYY/MM/DD HH:MM:SS, 31=change, 32=pct, 33=high, 34=low
    if len(fields) < 35 or not fields[1]:
        return None
    try:
        last = float(fields[3])
        prev = float(fields[4])
        return {
            "symbol": symbol[2:],
            "name": fields[1],
            "market": "hk",
            "open": float(fields[5]),
            "prev_close": prev,
            "high": float(fields[33]),
            "low": float(fields[34]),
            "price": last,
            "volume": int(float(fields[6])) if fields[6] else None,
            "change": float(fields[31]) if fields[31] else round(last - prev, 3),
            "pct": float(fields[32]) if fields[32] else None,
            "ts": fields[30] if len(fields) > 30 else None,
            "source": "tencent",
        }
    except (ValueError, IndexError):
        return None


def tencent_quote_batch(codes: list[str]) -> list[dict[str, Any]]:
    symbols = [sina_symbol(c) for c in codes]  # same prefix scheme as Sina
    url = TENCENT_QUOTE + ",".join(symbols)
    text = http_text(url, encoding="gbk")
    by_symbol: dict[str, list[str]] = {}
    for match in _TENCENT_RE.finditer(text):
        sym, payload = match.group(1), match.group(2)
        by_symbol[sym] = payload.split("~")
    out: list[dict[str, Any]] = []
    for sym in symbols:
        fields = by_symbol.get(sym)
        if fields is None or len(fields) < 3 or not fields[1]:
            out.append({"symbol": sym, "error": "no data"})
            continue
        parsed = (
            _parse_tencent_hk(sym, fields) if sym.startswith("hk")
            else _parse_tencent_a_share(sym, fields)
        )
        out.append(parsed or {"symbol": sym, "error": "parse failed"})
    return out


# ---------- Eastmoney quote ----------


def _em_decimal(data: dict[str, Any]) -> int:
    return int(data.get("f59") or 2)


# ---------- Yahoo Finance (HK + HK-index fallback only) ----------
#
# Yahoo doesn't reliably cover mainland A-shares. Used here only for HK
# (`116.{code}` → `{code-stripped}.HK`) and HK indices (^HSI/^HSCE/^HSTECH)
# when Eastmoney is blackholed.


def _yh_hk_symbol(code: str) -> str:
    """A bare HK code (with or without leading zero) → Yahoo symbol."""
    c = str(code).lstrip("0") or "0"
    if len(c) < 4:
        c = c.zfill(4)
    return f"{c}.HK"


def yh_chart_raw(yh_symbol: str, *, interval: str = "1d", range_: str = "5d") -> dict[str, Any] | None:
    qs = urllib.parse.urlencode({"interval": interval, "range": range_})
    url = f"{YH_CHART}/{urllib.parse.quote(yh_symbol, safe='')}?{qs}"
    try:
        j = http_json(url)
    except Exception:
        return None
    chart = (j or {}).get("chart") or {}
    if chart.get("error"):
        return None
    return (chart.get("result") or [None])[0]


def yh_hk_quote(code: str) -> dict[str, Any] | None:
    r = yh_chart_raw(_yh_hk_symbol(code))
    if not r:
        return None
    meta = r.get("meta") or {}
    last = meta.get("regularMarketPrice")
    prev = meta.get("chartPreviousClose") or meta.get("previousClose")
    change = round(last - prev, 4) if (last is not None and prev) else None
    pct = round((last - prev) / prev * 100, 4) if (last is not None and prev) else None
    ts = meta.get("regularMarketTime")
    return {
        "symbol": str(code).zfill(5),
        "name": meta.get("longName") or meta.get("shortName"),
        "market": "hk",
        "price": last,
        "open": None,
        "high": meta.get("regularMarketDayHigh"),
        "low": meta.get("regularMarketDayLow"),
        "prev_close": prev,
        "change": change,
        "pct": pct,
        "volume": meta.get("regularMarketVolume"),
        "amount": None,
        "ts": datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else None,
        "source": "yahoo",
    }


def yh_index_quote(alias_key: str) -> dict[str, Any] | None:
    yh_sym = YH_INDEX_FROM_ALIAS.get(alias_key.upper())
    if not yh_sym:
        return None
    r = yh_chart_raw(yh_sym)
    if not r:
        return None
    meta = r.get("meta") or {}
    last = meta.get("regularMarketPrice")
    prev = meta.get("chartPreviousClose") or meta.get("previousClose")
    change = round(last - prev, 4) if (last is not None and prev) else None
    pct = round((last - prev) / prev * 100, 4) if (last is not None and prev) else None
    return {
        "symbol": yh_sym,
        "name": meta.get("longName") or meta.get("shortName"),
        "price": last,
        "high": meta.get("regularMarketDayHigh"),
        "low": meta.get("regularMarketDayLow"),
        "prev_close": prev,
        "change": change,
        "pct": pct,
        "source": "yahoo",
    }


def em_quote_one(secid: str) -> dict[str, Any]:
    url = f"{EM_QUOTE}?secid={secid}&fields={EM_QUOTE_FIELDS}"
    j = http_json(url)
    d = j.get("data")
    if not d:
        return {"symbol": secid, "error": "no data", "rc": j.get("rc")}
    dec = _em_decimal(d)
    scale = 10**dec

    def num(k: str, factor: int = scale) -> float | None:
        v = d.get(k)
        if v is None or v == "-":
            return None
        try:
            return round(float(v) / factor, dec)
        except (TypeError, ValueError):
            return None

    return {
        "symbol": d.get("f57"),
        "name": d.get("f58"),
        "secid": secid,
        "price": num("f43"),
        "open": num("f46"),
        "high": num("f44"),
        "low": num("f45"),
        "prev_close": num("f60"),
        "change": num("f169"),
        "pct": num("f170", 100),
        "volume": d.get("f47"),
        "amount": d.get("f48"),
        "source": "eastmoney",
    }


def em_quote_batch(codes: list[str]) -> list[dict[str, Any]]:
    return [em_quote_one(eastmoney_secid(c)) for c in codes]


# ---------- History (kline) — Eastmoney primary, Sina/Tencent fallbacks ----------


def em_history(secid: str, from_d: date, to_d: date, adjust: str = "qfq") -> list[dict[str, Any]]:
    fqt = {"none": 0, "qfq": 1, "hfq": 2}.get(adjust, 1)
    lmt = max((to_d - from_d).days + 5, 5)
    url = (
        f"{EM_KLINE}?secid={secid}&klt=101&fqt={fqt}"
        f"&end={to_d.strftime('%Y%m%d')}&lmt={lmt}"
        "&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58"
    )
    j = http_json(url)
    d = (j or {}).get("data") or {}
    klines = d.get("klines") or []
    rows: list[dict[str, Any]] = []
    for line in klines:
        parts = line.split(",")
        if len(parts) < 6:
            continue
        d_str = parts[0]
        if d_str < from_d.strftime("%Y-%m-%d") or d_str > to_d.strftime("%Y-%m-%d"):
            continue
        rows.append({
            "date": d_str,
            "open": float(parts[1]),
            "close": float(parts[2]),
            "high": float(parts[3]),
            "low": float(parts[4]),
            "volume": int(float(parts[5])),
            "amount": float(parts[6]) if len(parts) > 6 else None,
            "source": "eastmoney",
        })
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows


def sina_history(code: str, from_d: date, to_d: date) -> list[dict[str, Any]]:
    # Sina daily kline. A-share only (HK endpoint returns null).
    # Always full-adjusted-forward; no adjust knob. No amount field.
    mkt = detect_market(code)
    if mkt == "hk":
        return []
    sym = f"{mkt}{code}"
    lmt = max((to_d - from_d).days + 5, 5)
    url = (
        "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
        f"CN_MarketData.getKLineData?symbol={sym}&scale=240&ma=no&datalen={lmt}"
    )
    j = http_json(url)
    if not isinstance(j, list):
        return []
    rows: list[dict[str, Any]] = []
    for r in j:
        d_str = r.get("day", "")
        if d_str < from_d.strftime("%Y-%m-%d") or d_str > to_d.strftime("%Y-%m-%d"):
            continue
        rows.append({
            "date": d_str,
            "open": float(r["open"]),
            "close": float(r["close"]),
            "high": float(r["high"]),
            "low": float(r["low"]),
            "volume": int(float(r["volume"])),
            "amount": None,
            "source": "sina",
        })
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows


def tencent_history(code: str, from_d: date, to_d: date, adjust: str = "qfq") -> list[dict[str, Any]]:
    # Tencent kline. Handles A-share and HK. adjust: qfq|hfq|none.
    # A-share: sh/sz/bj prefix → fqkline endpoint. HK: hk + 5-digit → hkfqkline.
    mkt = detect_market(code)
    if mkt == "hk":
        sym = f"hk{code.zfill(5)}"
        path = "hkfqkline"
    else:
        sym = f"{mkt}{code}"
        path = "fqkline"
    adj = adjust if adjust in ("qfq", "hfq") else ""
    lmt = max((to_d - from_d).days + 5, 5)
    url = f"https://web.ifzq.gtimg.cn/appstock/app/{path}/get?param={sym},day,,,{lmt},{adj}"
    j = http_json(url)
    if (j or {}).get("code") != 0:
        return []
    data = (j.get("data") or {}).get(sym) or {}
    key = f"{adj}day" if adj else "day"
    arr = data.get(key) or data.get("day") or []
    rows: list[dict[str, Any]] = []
    for r in arr:
        if len(r) < 6:
            continue
        d_str = r[0]
        if d_str < from_d.strftime("%Y-%m-%d") or d_str > to_d.strftime("%Y-%m-%d"):
            continue
        # Tencent volume unit = 手 (lots, 100 shares for A; shares for HK is raw).
        rows.append({
            "date": d_str,
            "open": float(r[1]),
            "close": float(r[2]),
            "high": float(r[3]),
            "low": float(r[4]),
            "volume": int(float(r[5])),
            "amount": None,
            "source": "tencent",
        })
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows


def fetch_history(code: str, from_d: date, to_d: date, adjust: str = "qfq") -> list[dict[str, Any]]:
    """Eastmoney → Sina (A only) → Tencent. First non-empty wins."""
    errors: list[str] = []
    for name, fn in (
        ("eastmoney", lambda: em_history(eastmoney_secid(code), from_d, to_d, adjust)),
        ("sina",      lambda: sina_history(code, from_d, to_d)),
        ("tencent",   lambda: tencent_history(code, from_d, to_d, adjust)),
    ):
        try:
            rows = fn()
            if rows:
                return rows
        except Exception as e:
            errors.append(f"{name}: {type(e).__name__}: {e}")
    if errors:
        die("all history sources failed: " + " | ".join(errors))
    return []


# ---------- Index ----------


# Sina/Tencent index symbols for fallback. Maps Eastmoney secid → (sina, tencent).
# Sina s_ format returns [name, price, change, pct, vol, amount].
# Sina int_ format (HK indices) returns [name, price, change, pct].
# Tencent q= format is a long ~~-delimited string; index 3 is price, 31 is change, 32 is pct.
_INDEX_FALLBACK = {
    "1.000001":   ("s_sh000001", "sh000001"),
    "0.399001":   ("s_sz399001", "sz399001"),
    "1.000300":   ("s_sh000300", "sh000300"),
    "1.000905":   ("s_sh000905", "sh000905"),
    "1.000852":   ("s_sh000852", "sh000852"),
    "0.399006":   ("s_sz399006", "sz399006"),
    "1.000688":   ("s_sh000688", "sh000688"),
    "100.HSI":    ("int_hangseng", "hkHSI"),
    "100.HSCEI":  (None,           "hkHSCEI"),
    "100.HSTECH": (None,           "hkHSTECH"),
}


def sina_index_quote(sina_sym: str) -> dict[str, Any] | None:
    url = f"https://hq.sinajs.cn/list={sina_sym}"
    txt = http_text(url, referer="https://finance.sina.com.cn/", encoding="gbk")
    m = _SINA_RE.search(txt)
    if not m:
        return None
    raw = m.group(2)
    if not raw:
        return None
    fields = raw.split(",")
    # int_ (HK): name,price,change,pct ; s_ (CN): name,price,change,pct,vol,amount
    if sina_sym.startswith("int_") and len(fields) >= 4:
        return {
            "name": fields[0],
            "price": float(fields[1]),
            "change": float(fields[2]),
            "pct": float(fields[3]),
            "source": "sina",
        }
    if sina_sym.startswith("s_") and len(fields) >= 6:
        return {
            "name": fields[0],
            "price": float(fields[1]),
            "change": float(fields[2]),
            "pct": float(fields[3]),
            "volume": int(float(fields[4])) if fields[4] else None,
            "amount": float(fields[5]) * 10000 if fields[5] else None,  # 万元 → 元
            "source": "sina",
        }
    return None


def tencent_index_quote(tx_sym: str) -> dict[str, Any] | None:
    url = f"https://qt.gtimg.cn/q={tx_sym}"
    txt = http_text(url, referer="https://gu.qq.com/", encoding="gbk")
    # v_sh000300="1~沪深300~000300~4908.17~..."
    m = re.search(r'v_[^=]+="([^"]+)"', txt)
    if not m:
        return None
    parts = m.group(1).split("~")
    if len(parts) < 33:
        return None
    try:
        return {
            "name": parts[1],
            "price": float(parts[3]),
            "prev_close": float(parts[4]) if parts[4] else None,
            "open": float(parts[5]) if parts[5] else None,
            "change": float(parts[31]) if parts[31] else None,
            "pct": float(parts[32]) if parts[32] else None,
            "source": "tencent",
        }
    except (ValueError, IndexError):
        return None


def fetch_index(secid: str) -> dict[str, Any]:
    errors: list[str] = []
    try:
        row = em_quote_one(secid)
        if row.get("price") is not None:
            return row
        errors.append(f"eastmoney: {row.get('error', 'no price')}")
    except Exception as e:
        errors.append(f"eastmoney: {type(e).__name__}: {e}")
    fb = _INDEX_FALLBACK.get(secid)
    if fb:
        sina_sym, tx_sym = fb
        if sina_sym:
            try:
                row = sina_index_quote(sina_sym)
                if row:
                    row["secid"] = secid
                    return row
            except Exception as e:
                errors.append(f"sina: {type(e).__name__}: {e}")
        if tx_sym:
            try:
                row = tencent_index_quote(tx_sym)
                if row:
                    row["secid"] = secid
                    return row
            except Exception as e:
                errors.append(f"tencent: {type(e).__name__}: {e}")
    return {"secid": secid, "error": " | ".join(errors) or "no data"}


def resolve_index(name: str) -> str:
    key = name.upper().replace(" ", "").replace("_", "").replace("-", "")
    if key in INDEX_ALIASES:
        return INDEX_ALIASES[key]
    if "." in name and name.split(".")[0].isdigit():
        return name
    die(f"unknown index '{name}'. Supported: {', '.join(sorted(set(INDEX_ALIASES.keys())))}")


# ---------- Search ----------


def em_search(query: str, limit: int = 10) -> list[dict[str, Any]]:
    qs = urllib.parse.urlencode({"input": query, "type": 14, "count": limit})
    j = http_json(f"{EM_SEARCH}?{qs}")
    data = ((j or {}).get("QuotationCodeTable") or {}).get("Data") or []
    return [
        {
            "symbol": row.get("Code"),
            "name": row.get("Name"),
            "secid": row.get("QuoteID"),
            "exchange": row.get("JYS"),
            "type": row.get("SecurityTypeName"),
        }
        for row in data
    ]


# ---------- Northbound / Southbound ----------


def northbound() -> dict[str, Any]:
    url = f"{EM_KAMT}?fields1=f1,f2,f3,f4&fields2=f51,f52,f54"
    j = http_json(url)
    d = (j or {}).get("data") or {}

    def ch(name: str) -> dict[str, Any]:
        raw = d.get(name) or {}
        # upstream amounts are in 万元 (10,000 yuan units) — rescale to yuan
        return {
            "net_in_cny": (raw.get("dayNetAmtIn") or 0) * 10000,
            "daily_limit_cny": (raw.get("dayAmtThreshold") or 0) * 10000,
            "status": "open" if raw.get("status") == 1 else "closed",
        }

    return {
        "northbound": {  # HK → mainland
            "hk_to_sh": ch("hk2sh"),
            "hk_to_sz": ch("hk2sz"),
        },
        "southbound": {  # mainland → HK
            "sh_to_hk": ch("sh2hk"),
            "sz_to_hk": ch("sz2hk"),
        },
    }


# ---------- Sector ranking / limit-up/down ----------


# clist fs filter strings (Eastmoney market-board codes)
FS_ALL_A_SHARE = "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2"
FS_INDUSTRY = "m:90+t:2+f:!50"
FS_CONCEPT = "m:90+t:3+f:!50"


def clist(fs: str, fields: str, *, order_field: str = "f3", desc: bool = True, limit: int = 20) -> list[dict[str, Any]]:
    qs = urllib.parse.urlencode({
        "pn": 1, "pz": limit, "po": 1 if desc else 0, "np": 1,
        "fltt": 2, "invt": 2, "fid": order_field, "fs": fs, "fields": fields,
    }, safe="+:!,")
    # Primary realtime → 15-min-delay fallback. Both return the same shape.
    for base in (EM_CLIST, EM_CLIST_DELAY):
        try:
            j = http_json(f"{base}?{qs}")
            rows = ((j or {}).get("data") or {}).get("diff") or []
            if rows:
                return rows
        except (urllib.error.URLError, OSError):
            continue
    return []


def limit_movers(direction: str, limit: int = 20) -> list[dict[str, Any]]:
    """direction: 'up' (highest gainers near +10%) or 'down' (lowest)."""
    desc = direction == "up"
    fields = "f2,f3,f6,f12,f14"  # last, pct, amount, code, name
    rows = clist(FS_ALL_A_SHARE, fields, order_field="f3", desc=desc, limit=limit)
    return [
        {
            "symbol": r.get("f12"),
            "name": r.get("f14"),
            "price": r.get("f2"),
            "pct": r.get("f3"),
            "amount": r.get("f6"),
        }
        for r in rows
    ]


def sector_ranking(kind: str, limit: int = 20) -> list[dict[str, Any]]:
    """kind: 'industry' or 'concept'."""
    fs = FS_INDUSTRY if kind == "industry" else FS_CONCEPT
    fields = "f3,f12,f14"  # pct, code, name
    rows = clist(fs, fields, order_field="f3", desc=True, limit=limit)
    return [
        {"code": r.get("f12"), "name": r.get("f14"), "pct": r.get("f3")}
        for r in rows
    ]


# ---------- Dispatch ----------


def _is_bad_row(row: dict[str, Any]) -> bool:
    return "error" in row or row.get("price") is None


def _merge_quotes(primary: list[dict[str, Any]], fallback: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per-row: keep primary if good, else swap in fallback if good."""
    out: list[dict[str, Any]] = []
    fb_by_sym = {r.get("symbol"): r for r in fallback if r.get("symbol")}
    for p in primary:
        if not _is_bad_row(p):
            out.append(p)
            continue
        sym = p.get("symbol")
        fb = fb_by_sym.get(sym) if sym else None
        out.append(fb if fb and not _is_bad_row(fb) else p)
    return out


def _safe_quote(fn: Any, codes: list[str]) -> list[dict[str, Any]]:
    """Call a quote-batch fn; on network/parse error return per-code error rows
    so the auto-fallback chain can swap in another source."""
    try:
        return fn(codes)
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
        return [{"symbol": c, "error": f"transient: {e}"} for c in codes]


def cmd_quote(args: argparse.Namespace) -> Any:
    codes = [c.strip() for c in args.codes.split(",") if c.strip()]
    source = args.source
    if source == "eastmoney":
        return em_quote_batch(codes)
    if source == "sina":
        return sina_quote_batch(codes)
    if source == "tencent":
        return tencent_quote_batch(codes)
    # auto: A-share via Sina (batched), HK via Eastmoney; fall back per-source
    # chain: A-share Sina → Eastmoney → Tencent;  HK Eastmoney → Sina → Tencent
    a_codes = [c for c in codes if detect_market(c) != "hk"]
    hk_codes = [c for c in codes if detect_market(c) == "hk"]
    out: list[dict[str, Any]] = []
    if a_codes:
        rows = _safe_quote(sina_quote_batch, a_codes)
        if any(_is_bad_row(r) for r in rows):
            rows = _merge_quotes(rows, _safe_quote(em_quote_batch, a_codes))
        if any(_is_bad_row(r) for r in rows):
            rows = _merge_quotes(rows, _safe_quote(tencent_quote_batch, a_codes))
        out.extend(rows)
    if hk_codes:
        rows = _safe_quote(em_quote_batch, hk_codes)
        if any(_is_bad_row(r) for r in rows):
            rows = _merge_quotes(rows, _safe_quote(sina_quote_batch, hk_codes))
        if any(_is_bad_row(r) for r in rows):
            rows = _merge_quotes(rows, _safe_quote(tencent_quote_batch, hk_codes))
        # Last-tier: Yahoo per-symbol (no batch). Only fills rows still bad.
        if any(_is_bad_row(r) for r in rows):
            yh_rows: list[dict[str, Any]] = []
            for r in rows:
                if _is_bad_row(r):
                    code = r.get("symbol") or r.get("code") or ""
                    yh = yh_hk_quote(code)
                    yh_rows.append(yh or r)
                else:
                    yh_rows.append(r)
            rows = yh_rows
        out.extend(rows)
    return out


def cmd_history(args: argparse.Namespace) -> Any:
    fr, to = resolve_range(args)
    return fetch_history(args.code, fr, to, args.adjust)


def cmd_index(args: argparse.Namespace) -> Any:
    names = [n.strip() for n in args.names.split(",") if n.strip()]
    out = []
    for n in names:
        secid = resolve_index(n)
        row = fetch_index(secid)
        # Yahoo fallback only for HK indices that have a Yahoo mapping (last resort)
        if (row.get("error") or row.get("price") is None) and n.upper() in YH_INDEX_FROM_ALIAS:
            yh = yh_index_quote(n)
            if yh:
                yh["secid"] = secid
                yh["fallback_reason"] = row.get("error", "no eastmoney/sina/tencent data")
                row = yh
        row.setdefault("symbol", n)
        out.append(row)
    return out


def cmd_search(args: argparse.Namespace) -> Any:
    return em_search(args.query, args.limit)


def cmd_northbound(_: argparse.Namespace) -> Any:
    return northbound()


def cmd_limit_up(args: argparse.Namespace) -> Any:
    return limit_movers("up", args.limit)


def cmd_limit_down(args: argparse.Namespace) -> Any:
    return limit_movers("down", args.limit)


def cmd_industry(args: argparse.Namespace) -> Any:
    return sector_ranking("industry", args.limit)


def cmd_concept(args: argparse.Namespace) -> Any:
    return sector_ranking("concept", args.limit)


def main(argv: list[str]) -> None:
    p = argparse.ArgumentParser(prog="cn_equity", description="CN equity markets")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_range_flags(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--from", dest="from_date", help="YYYY-MM-DD")
        sp.add_argument("--to", dest="to_date", help="YYYY-MM-DD")
        sp.add_argument("--days", type=int, help="last N calendar days")

    q = sub.add_parser("quote", help="realtime quote (A-share + HK)")
    q.add_argument("codes", help="bare code(s), comma-separated. e.g. 600519,000001,00700")
    q.add_argument("--source", choices=["sina", "eastmoney", "tencent"])
    q.set_defaults(func=cmd_quote)

    h = sub.add_parser("history", help="daily OHLCV")
    h.add_argument("code")
    h.add_argument("--adjust", choices=["none", "qfq", "hfq"], default="qfq")
    add_range_flags(h)
    h.set_defaults(func=cmd_history)

    idx = sub.add_parser("index", help="CN/HK index quote")
    idx.add_argument("names", help="SSE,SZSE,CSI300,CSI500,CHINEXT,STAR50,HSI,...")
    idx.set_defaults(func=cmd_index)

    s = sub.add_parser("search", help="search by name/code/pinyin")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=10)
    s.set_defaults(func=cmd_search)

    nb = sub.add_parser("northbound", help="Stock Connect flow summary")
    nb.set_defaults(func=cmd_northbound)

    lu = sub.add_parser("limit-up", help="today's 涨停股")
    lu.add_argument("--limit", type=int, default=20)
    lu.set_defaults(func=cmd_limit_up)

    ld = sub.add_parser("limit-down", help="today's 跌停股")
    ld.add_argument("--limit", type=int, default=20)
    ld.set_defaults(func=cmd_limit_down)

    ind = sub.add_parser("industry", help="行业板块 ranked by gain")
    ind.add_argument("--limit", type=int, default=20)
    ind.set_defaults(func=cmd_industry)

    con = sub.add_parser("concept", help="题材板块 ranked by gain")
    con.add_argument("--limit", type=int, default=20)
    con.set_defaults(func=cmd_concept)

    args = p.parse_args(argv)
    try:
        result = args.func(args)
    except (urllib.error.URLError, OSError) as e:
        die(f"network error: {e}")
    except json.JSONDecodeError as e:
        die(f"upstream returned non-JSON: {e}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
