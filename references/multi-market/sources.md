# Sources catalogue

Raw endpoint reference for the CN-market wrappers. Verified 2026-05-27
from a CN-routed network. All keyless. AKShare-wrapped endpoints are
called via AKShare (lazy-imported in `research.py`, `options.py`,
`macro.py`); the underlying endpoints are listed for reference only.

## hq.sinajs.cn — realtime A-share + HK (batched)

The default data source behind every Chinese broker app. **Batched in a single
HTTP call** for any number of symbols — major advantage over Eastmoney's
one-secid-per-call quote API.

### Endpoint

```
https://hq.sinajs.cn/list=sh600519,sz000001,hk00700
```

- Requires `Referer: https://finance.sina.com.cn` header — without it, returns
  empty response or 403.
- Returns **GBK-encoded** JavaScript: `var hq_str_sh600519="贵州茅台,1268.02,...";`
  Wrapper decodes as GBK.
- One `var hq_str_<symbol> = "..."` line per requested symbol. Missing symbols
  produce an empty payload (`var hq_str_xxx="";`).

### Symbol prefix

- `sh` + 6-digit → Shanghai A-share (incl. STAR Market `688xxx`)
- `sz` + 6-digit → Shenzhen A-share (incl. ChiNext `300xxx`)
- `hk` + 5-digit → Hong Kong
- `bj` + 6-digit → Beijing (北交所)

### A-share CSV field order (positions 0-31)

| Pos | Field |
|---|---|
| 0 | name |
| 1 | open |
| 2 | prev_close |
| 3 | last |
| 4 | high |
| 5 | low |
| 6 | bid1 |
| 7 | ask1 |
| 8 | volume (shares) |
| 9 | amount (yuan) |
| 10-29 | bid/ask 5-level (price/qty pairs) |
| 30 | date `YYYY-MM-DD` |
| 31 | time `HH:MM:SS` |

### HK CSV field order

| Pos | Field |
|---|---|
| 0 | english_name |
| 1 | chinese_name |
| 2 | open |
| 3 | prev_close |
| 4 | high |
| 5 | low |
| 6 | last |
| 7 | change abs |
| 8 | change pct |
| 9 | bid |
| 10 | ask |
| 11 | amount (HKD) |
| 12 | volume (shares) |
| 15 | 52w high |
| 16 | 52w low |
| 17 | date `YYYY/MM/DD` |
| 18 | time `HH:MM` |

## push2.eastmoney.com — quotes, indices, sectors, fund flows

Reverse-engineered from `quote.eastmoney.com`. Keyless. CN- and US-reachable.

### Stock/index quote (single)

```
https://push2.eastmoney.com/api/qt/stock/get?secid=<S>&fields=f43,...
```

**`secid` format:** `<market>.<code>`

| Prefix | Market |
|---|---|
| `0.` | Shenzhen (000xxx, 002xxx, 003xxx, 300xxx) |
| `1.` | Shanghai (600xxx, 688xxx) + Shanghai indices (000001, 000300, 000688) |
| `116.` | HK |
| `100.` | International indices (HSI, HSCEI, HSTECH, SPX, etc.) |
| `105./106./107.` | US Nasdaq / NYSE / AMEX (covered by global-equities) |

### Quote fields

| Code | Meaning | Notes |
|---|---|---|
| `f43` | Last | int, divide by `10^f59` |
| `f44` | High | scaled |
| `f45` | Low | scaled |
| `f46` | Open | scaled |
| `f47` | Volume | raw |
| `f48` | Amount | raw, currency depends on market |
| `f57` | Code | string |
| `f58` | Name | string, Chinese for CN/HK |
| `f59` | Price decimals (scale exponent) | CN/indices=2, HK=3. **Use this, not f152.** |
| `f60` | Prev close | scaled |
| `f152` | Display decimals (UI) | **Do not use as scale** — under-scales HK by 10x. |
| `f169` | Change abs | scaled |
| `f170` | Change pct (bps) | divide by 100 |

### Verified index secids

| Index | Secid |
|---|---|
| 上证综指 | `1.000001` |
| 深证成指 | `0.399001` |
| 沪深300 | `1.000300` |
| 中证500 | `1.000905` |
| 中证1000 | `1.000852` |
| 创业板指 | `0.399006` |
| 科创50 | `1.000688` |
| 恒生指数 | `100.HSI` |
| 恒生中国企业指数 (国企指数) | `100.HSCEI` |
| 恒生科技指数 | `100.HSTECH` |

### K-line history

```
https://push2his.eastmoney.com/api/qt/stock/kline/get
  ?secid=<S>
  &klt=101                # 101=daily, 102=weekly, 103=monthly, 1/5/15/30/60=intraday
  &fqt=1                  # 0=none, 1=qfq forward-adj, 2=hfq backward-adj
  &end=20500101           # rolling: pass a far-future date
  &lmt=120                # number of bars (newest counting back)
  &fields1=f1,f2,f3,f4,f5,f6
  &fields2=f51,f52,f53,f54,f55,f56,f57,f58
```

Response: `data.klines` = list of CSV strings:

```
date,open,close,high,low,volume,amount,amplitude_pct
```

Note: `close` is the **second** field, not third — easy to misorder.

### List/screener (`clist/get`) — sectors + limit movers

```
https://push2.eastmoney.com/api/qt/clist/get
  ?pn=1&pz=20&po=1&np=1&fltt=2&invt=2
  &fid=f3                 # sort field (f3=pct change)
  &fs=<filter>            # market-board filter (see below)
  &fields=f2,f3,f6,f12,f14
```

`fs` market-board filters used by this skill:

| `fs` | Meaning |
|---|---|
| `m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2` | All A-share boards (沪深京 main + 创业板 + 科创板) — used for limit-up/down |
| `m:90+t:2+f:!50` | 行业板块 (industry sectors, exclude small) |
| `m:90+t:3+f:!50` | 题材板块 (concept theme boards) |

`fields` codes (in `clist`-style responses, indexed by `f<N>`):

| Code | Meaning |
|---|---|
| `f2` | Last price |
| `f3` | Change pct |
| `f6` | Amount (成交额) |
| `f8` | Turnover rate |
| `f12` | Code |
| `f14` | Name |

`fid` values worth knowing: `f3` (gain%), `f6` (amount), `f8` (turnover%), `f10`
(volume ratio).

### 北向/南向资金 (Stock Connect)

```
https://push2.eastmoney.com/api/qt/kamt/get?fields1=f1,f2,f3,f4&fields2=f51,f52,f54
```

Response shape:

```json
{"data": {
  "hk2sh": {"status": 1, "dayNetAmtIn": 0.0, "dayAmtThreshold": 5200000.0},
  "sh2hk": {"status": 1, "dayNetAmtIn": 4200000.0, "dayAmtThreshold": 4200000.0},
  "hk2sz": {...}, "sz2hk": {...}
}}
```

- `hk2sh`/`hk2sz` = 北向 (HK → mainland buying mainland A-shares).
- `sh2hk`/`sz2hk` = 南向 (mainland → HK buying HK stocks).
- Amounts are in **万元** (10,000 yuan units). Wrapper rescales to whole yuan.
- `dayAmtThreshold` is the daily quota cap; when `dayNetAmtIn` ≥ threshold, the
  channel saturates for that day.

### Realtime northbound minute series

```
https://push2.eastmoney.com/api/qt/kamt.rtmin/get?fields1=f1,f2,f3,f4&fields2=f51,f54
```

Returns minute-by-minute net inflow `s2n` (累计净流入) as CSV strings. Not wired
in v1 — add when someone wants the live stream.

## searchapi.eastmoney.com — search

```
https://searchapi.eastmoney.com/api/suggest/get?input=<Q>&type=14&count=10
```

Supports Chinese name, English name, partial code, pinyin. `type=14` returns
stock/index/ETF; other values filter by asset class. Response is keyed
`QuotationCodeTable.Data[]` with `Code`/`Name`/`QuoteID`/`JYS`/`SecurityTypeName`.

## qt.gtimg.cn — Tencent realtime quotes (batched)

Tencent's mobile-app quote backend. Batched like Sina; same prefix scheme.
Wired as third-tier fallback in `quote` (after Sina for A-share / Eastmoney for HK).

### Endpoint

```
https://qt.gtimg.cn/q=sh600519,sz000001,hk00700
```

- No `Referer` requirement.
- Returns **GBK-encoded** JavaScript: `v_sh600519="1~贵州茅台~600519~1303.00~...";`
- One `v_<symbol> = "..."` line per requested symbol.

### Symbol prefix

Same as Sina (`sh` / `sz` / `hk` / `bj` + code).

### A-share CSV field order (`~`-separated)

| Pos | Field |
|---|---|
| 0 | market code (1=sh/sz, 100=hk) |
| 1 | name |
| 2 | code |
| 3 | last |
| 4 | open |
| 5 | prev_close |
| 6 | volume (手 = 100 shares; multiply by 100 for shares) |
| 30 | timestamp `YYYYMMDDhhmmss` |
| 31 | change abs |
| 32 | change pct |
| 33 | high |
| 34 | low |

### HK CSV field order

| Pos | Field |
|---|---|
| 0 | market code (100) |
| 1 | name |
| 2 | code |
| 3 | last |
| 4 | prev_close |
| 5 | open |
| 6 | volume (shares) |
| 31 | timestamp `YYYY/MM/DD HH:MM:SS` |
| 32 | change abs |
| 33 | change pct |
| 34 | high |
| 35 | low |

## query1.finance.yahoo.com — HK + HK-index fallback

Wired as final fallback for HK stock quotes and HK-family index quotes
(`HSI`/`HSCEI`/`HSTECH`) only. Does not cover mainland A-shares reliably.

### Endpoint

```
https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?interval=1d&range=5d
```

Keyless, single-symbol per call (no batch).

### Symbol mapping

- HK stock: `{code-without-leading-zero, 4-digit-padded}.HK` → `00700` → `0700.HK`.
- HK indices: `^HSI`, `^HSCE` (国企指数), `^HSTECH` (恒生科技).

Throttles by IP (HTTP 429). Treated as soft failure in the wrapper. See the
global-equities Yahoo section in
[`global-equities/references/sources.md`](../../global-equities/references/sources.md)
for full schema detail.

## Rate limits

None of the providers publish rate limits; the following thresholds are
empirical.

- **Eastmoney (`push2*.eastmoney.com`)** — undocumented per-IP burst ceiling.
  Symptom when tripped: HTTPS connect succeeds but the server closes the
  socket before sending a response (`RemoteDisconnected` from urllib,
  `Empty reply from server` / curl exit 52). Affects subsequent calls from
  the same IP for several minutes; reproducible from both Python and curl.
  Observed at roughly 20 calls in 5 seconds. Subcommands `index`,
  `history`, `search`, `northbound`, `limit-up/down`, `industry`,
  `concept` have no fallback — pace accordingly. `quote` survives via
  the Sina → Eastmoney → Tencent chain. Wrapper retries (`http_text`
  attempts 3× with backoff) don't help once blackholed; pacing does.
- **Sina (`hq.sinajs.cn`)** — historically IP-blocks on bursty per-symbol
  calls; safe with the wrapper's single-batched request per `quote` call.
- **Tencent (`qt.gtimg.cn`)** — batched same as Sina; no block observed.

## Evaluated alternative sources (not wired)

Verified 2026-05-27. Listed so future work doesn't re-evaluate from scratch.

### CN A-share / HK quotes

| Source | Endpoint | Auth | Status |
|---|---|---|---|
| AKShare (Python lib) | wraps Eastmoney + Sina + Tencent + 同花顺 + JuChao + 网易财经 + many others | none (per-call) | Library only. Underlying endpoints addressable individually. |
| 同花顺 (10jqka) | `d.10jqka.com.cn/v6/realhead/hs_{code}/last.js` (A-share), `d.10jqka.com.cn/v6/realhead/hk_{code}/last.js` (HK) | none | CN-IP friendly. Occasional UA gating. |
| 雪球 (Xueqiu) | `stock.xueqiu.com/v5/stock/realtime/quotec.json?symbol=SH600519,SZ000001` | Cookie (`xq_a_token`) required | Public site requires session cookie. |
| 网易财经 (163) | `api.money.126.net/data/feed/0600519,money.api` | none | JSONP-style. |
| JuChao (cninfo) | `webapi.cninfo.com.cn/api/stock/p_stock2101?scode=600519` | none | Listed company data; announcements + filings, not realtime quotes. |
| 中证指数 (CSI) | `www.csindex.com.cn/csindex-home/indexInfo/index-info?indexCode=000300` | none | Official index publisher; daily values only. |

### Stock Connect / fund flow

| Source | Endpoint | Auth | Status |
|---|---|---|---|
| HKEX | `www.hkex.com.hk/eng/csm/Statistics/...` | none | Static daily CSVs/XLS, T+1. |
| Eastmoney rtmin (used minimal) | `push2.eastmoney.com/api/qt/kamt.rtmin/get` | none | Minute-by-minute net inflow; not wired in v1. |

### Macro / 龙虎榜 / fundamentals (deferred)

| Source | Endpoint | Auth | Status |
|---|---|---|---|
| Eastmoney 龙虎榜 | `datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_DAILYBILLBOARD_DETAILSNEW` | none | Works; needs per-day + per-stock filter shape. |
| Eastmoney 财务数据 | `datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_LICO_FN_CPD&...` | none | Quarterly financials. Defer to `cn-fundamentals` skill. |
| Eastmoney 公告 | `np-anotice-stock.eastmoney.com/api/security/ann?cb=...&sr=-1&page_size=...&page_index=1&ann_type=...` | none | Announcements; defer to `cn-fundamentals`. |
| 巨潮资讯 (cninfo) | `www.cninfo.com.cn/new/hisAnnouncement/query` | none | Regulatory filings; defer to `cn-fundamentals`. |
| Wind | `tushare.pro` (wraps Wind for some series) | API key + score | Not keyless. |
| Tushare | `api.tushare.pro` | API key (free with score) | — |
| AKShare local | (see above) | none | Already covered. |

### Global (covered by `global-equities`)

| Source | Endpoint | Auth | Status |
|---|---|---|---|
| Nasdaq | `api.nasdaq.com/api/quote/...` | none | Primary US-stock source in `global-equities`. |
| Frankfurter | `api.frankfurter.dev/v1/...` | none | Primary FX source in `global-equities`. |

## Backlog (v2)

| Need | Why deferred |
|---|---|
| **A+H pair lookup** | `RPT_AH_COMPARE` endpoint renamed/retired; needs re-discovery. |
| **龙虎榜 (top trader exposures)** | `RPT_DAILYBILLBOARD_DETAILSNEW` works but needs per-day + per-stock filtering shape. |
| **个股资金流向 (per-stock fund flow)** | Different endpoint family (`push2.eastmoney.com/api/qt/ulist.np/get`); not yet wired. |
| **Realtime 北向 minute stream** | `kamt.rtmin/get` — defer until needed. |
| **B-share** | Dead market; not worth coding. |
| **Intraday minute bars** | `klt=1/5/15/30/60` already supported by the same `history` shape — gated by a future `--interval` flag. |
| **公告/财报 (announcements, financials)** | Distinct API surface; could become a separate `cn-fundamentals` skill. |
| **可转债 (convertible bonds), 期货 (futures), 期权 (options)** | Eastmoney covers them via different `fs` filters; defer per demand. |

## Cross-reference

- `global-equities` — US stocks/ETFs, global indices, FX. Also serves shallow HK
  via `116.*` secids; this skill is preferred for any CN-listed name (deeper data
  + CN-only signals).
- `macro-rates-fx` (future) — owns US Treasury yields, CPI, NFP, FRED-backed.
