# futures.py — advanced reference

CN onshore commodity futures (SHFE, DCE, CZCE, INE, GFEX). Front-month
(主连) quotes via Eastmoney `futsseapi`.

## Catalogue (18 contracts)

| Exchange | `sc` | Aliases (root + cont) |
|---|---|---|
| SHFE | 113 | `cu/cum` `al/alm` `au/aum` `ag/agm` `rb/rbm` `hc/hcm` |
| DCE | 114 | `i/im` `m/mm` `p/pm` `c/cm` |
| CZCE | 115 | `SR/SRM` `CF/CFM` `TA/TAM` `MA/MAM` `FG/FGM` `SA/SAM` |
| INE | 142 | `sc/scm` |
| GFEX | 225 | `lc/lcm` |

## Continuous-month code convention

- SHFE / DCE / INE / GFEX: lowercase root + `m` (`cum`, `rbm`, `im`, `scm`, `lcm`)
- CZCE: uppercase root + `M` (`SRM`, `FGM`, `SAM`)

The CLI alias is case-sensitive and matches the standard root (`cu`, `SR`).

## Endpoint

```
http://futsseapi.eastmoney.com/static/{sc}_{cont}_qt
```

(HTTP — HTTPS redirects.)

Response field map (Eastmoney short names):
- `p` = last price · `o` = open · `h` = high · `l` = low
- `zjsj` = previous close (昨结算) · `zde` = absolute change · `zdf` = percent change
- `vol` = cumulative volume · `ccl` = open interest (持仓量)
- `"-"` = null sentinel (often returned outside trading hours)

## Trading hours

CN futures have multi-session days:
- Day: 09:00–10:15, 10:30–11:30, 13:30–15:00
- Night: 21:00–23:00 (most contracts), 21:00–01:00 (precious metals + crude), 21:00–02:30 (rubber + soybean meal/oil)

Outside these hours, `p == "-"` and the wrapper returns
`{"error": "eastmoney unavailable"}` for the row. Distinguish from blackhole
by checking if other rows succeeded.

## Adding a contract

Edit `CATALOG` in `scripts/futures.py`:
```python
"ALIAS": {"name": "...", "exchange": "...", "sc": ..., "cont": "..."}
```

## Burst limit

Same per-IP ceiling as the equity APIs (~20 calls / 5s → multi-minute
blackhole). No upstream fallback. Pace batches.

## History gap

Same as global-markets — Eastmoney's kline endpoint returns
`{"rc":102, "data":null}` for futures secids. AKShare wraps the CFFEX and
exchange-direct kline endpoints (`ak.futures_zh_realtime`,
`ak.futures_main_sina`); if history becomes essential, port these calls
into `bin/cn/research.py` (we already accept the akshare dep
there) rather than expanding this stdlib script.