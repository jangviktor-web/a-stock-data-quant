# macro.py — advanced reference

CN macroeconomic indicators via AKShare. Lazy-imported.

## Coverage

| Subcommand | AKShare function | Units / frequency |
|---|---|---|
| `cpi` | `macro_china_cpi_yearly` | 同比 + 环比, monthly |
| `ppi` | `macro_china_ppi_yearly` | 同比, monthly |
| `gdp` | `macro_china_gdp_yearly` | 同比, quarterly |
| `m0m1m2` | `macro_china_money_supply` | 同比, monthly |
| `pmi-mfg` | `macro_china_pmi_yearly` | level (50 = neutral), monthly |
| `pmi-non-mfg` | `macro_china_non_man_pmi` | level, monthly |
| `pmi-caixin` | `macro_china_cx_pmi_yearly` | level, monthly |
| `social-financing` | `macro_china_shrzgm` | 亿元, monthly |
| `fiscal` | `macro_china_fx_reserves_yearly` | 亿美元 |
| `lpr` | `macro_china_lpr` | %, irregular (announcements) |
| `shibor` | `rate_interbank` | %, daily |
| `industrial` | `macro_china_industrial_production_yoy` | 同比, monthly |
| `retail` | `macro_china_consumer_goods_retail` | 当月+累计 同比/环比, monthly |
| `fixed-asset` | `macro_china_gdzctz` | 同比, monthly (累计) |
| `reserve-rate` | `macro_china_reserve_requirement_ratio` | %, irregular |
| `treasury-yield` | `bond_china_yield` | %, daily (1M, 3M, 6M, 1Y, 3Y, 5Y, 7Y, 10Y, 30Y) |

## Release timing (typical)

| Indicator | Release window |
|---|---|
| 制造业 PMI / 非制造业 PMI | last day of month, 09:00 |
| 财新 PMI | first business day of next month, 09:45 |
| CPI / PPI | ~9th–10th of next month |
| 社融 / M2 | ~10th–15th of next month |
| 工业增加值 / 零售 / 固定资产 | ~15th of next month |
| GDP | mid-month after quarter end (中旬) |
| LPR | 20th of each month (or next business day) |
| 国债收益率曲线 | T+1 daily |
| 央行储备金率 | irregular announcement |

## Gotchas

- `treasury-yield` returns one row per (date, tenor) — pivot externally
  if you want a wide format.
- AKShare's macro functions occasionally rename — e.g.
  `macro_china_pmi_yearly` covers 制造业 PMI; the `-yearly` suffix is
  legacy and the data is monthly. Don't assume function name = data
  frequency.
- All series are sourced from 国家统计局 / 央行 / 中央国债登记结算 —
  authoritative but lag of 1 release cycle is normal.
- Long histories: most series go back 10+ years. Slice in the agent if
  you only need recent data — AKShare always returns the full history.

## Cross-reference

For US/global macro (CPI/PCE/NFP/UNRATE/Fed funds/yields/recession spreads)
+ FX, use `macro-rates-fx/scripts/`. The two are deliberately disjoint —
CN macro lives here so the akshare dep is captured in one skill, US/global
macro lives in `macro-rates-fx` for the stdlib + optional FRED-key story.