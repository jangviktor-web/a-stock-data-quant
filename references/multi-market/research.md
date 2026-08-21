# research.py — advanced reference

AKShare-wrapped per-name research + high-signal events. Lazy-imported.

## AKShare function mapping

| Subcommand | AKShare function | Underlying source |
|---|---|---|
| `fundamentals --quarterly` | `stock_profit_sheet_by_quarterly_em` etc. | Eastmoney F10 |
| `fundamentals` | `stock_profit_sheet_by_yearly_em` etc. | Eastmoney F10 |
| `fundamentals` key metrics | `stock_financial_abstract_ths` | 同花顺 |
| `forecast` | `stock_yjyg_em` | Eastmoney 业绩预告 |
| `flash` | `stock_yjkb_em` | Eastmoney 业绩快报 |
| `report-calendar` | `stock_yysj_em` | Eastmoney 财报披露计划 |
| `lhb` | `stock_lhb_detail_em` | Eastmoney 龙虎榜 |
| `lhb-stock` | `stock_lhb_stock_detail_em` | Eastmoney |
| `block-trade` | `stock_dzjy_mrmx` | Eastmoney 大宗交易 |
| `unlock` | `stock_restricted_release_summary_em` | Eastmoney 限售解禁 |
| `shareholder-count` | `stock_zh_a_gdhs_detail_em` | Eastmoney 股东户数 |
| `insider-trade` | `stock_ggcg_em` | Eastmoney 高管增减持 |
| `buyback` | `stock_repurchase_em` | Eastmoney 回购 |
| `dividend` | `stock_fhps_em` / `stock_fhps_detail_em` | Eastmoney 分红送转 |
| `ipo-calendar` / `ipo-winning` | `stock_xgsglb_em` | Eastmoney 新股 |
| `etf-list` | `fund_etf_category_sina` | Sina |
| `etf-quote` | `fund_etf_spot_em` | Eastmoney |
| `cb-list` | `bond_cb_jsl` | 集思录 |
| `cb-quote` | `bond_cb_jsl` (filtered) | 集思录 |

If AKShare renames a function in a future release, the wrapper surfaces
`AttributeError: module 'akshare' has no attribute 'X'` — patch the
mapping above.

## Code formats

A-share fundamentals expect `{SH/SZ}{6-digit}` (Eastmoney convention):
- `SH600519` for 上海
- `SZ000001` for 深圳

The wrapper builds this from a bare 6-digit code automatically using the
same `_market_prefix` helper as `equity.py`.

Some AKShare functions want bare 6-digit (`600519`); others want prefixed.
Wrapper handles the common cases; if a new subcommand surfaces a format
mismatch, normalize in the wrapper, not the agent.

## 龙虎榜 (lhb) usage notes

- `lhb` (no date) returns recent days; AKShare paginates to ~50 rows.
- `lhb --date YYYYMMDD` queries one specific day.
- `lhb-stock CODE` returns the historical 龙虎榜 entries for a single stock
  — useful for "this stock just hit 龙虎榜 again, what was the historical pattern".

Each row carries the top-5 buying brokers + top-5 selling brokers with
amounts. 营业部 names containing `XX机构专用` indicate institutional
participation (vs. retail-broker seats).

## 大宗交易 usage notes

`block-trade` shows discount/premium to last close. Heavy premium often
signals strategic-investor accumulation; heavy discount often signals
exit / shareholder reduction.

## ETF/可转债 latency

ETF + CB lists are fetched on every call (no caching). For repeated
queries, cache externally — these files are ~500KB each.

`bond_cb_jsl` requires public CSRF from 集思录 — usually works keyless but
intermittently asks for a login cookie. Wrapper surfaces the underlying
error.

## Gotchas

- AKShare's Chinese column names appear verbatim in the JSON output
  (`代码`, `名称`, `收盘价`, `涨跌幅`, ...). Don't try to remap — agents
  read Chinese fine.
- Period parameters vary across functions: `date=YYYYMMDD`, `date=YYYYMM`,
  `symbol=YYYYMMDD`. Wrapper tries `--date YYYYMMDD` first; check
  AKShare docs for the function-specific format if a call returns 0 rows.
- AKShare wraps screen-scraped HTML in places; if Eastmoney changes its
  page structure, calls return empty DataFrames. Upgrade AKShare to fix.