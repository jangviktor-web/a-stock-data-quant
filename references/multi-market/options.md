# options.py — advanced reference

CN ETF options + CFFEX index options via AKShare.

## Underlyings

### ETF options (上交所 + 深交所)

| Code | Name | Exchange |
|---|---|---|
| `510050` | 50ETF | SSE |
| `510300` | 沪深300ETF | SSE |
| `510500` | 中证500ETF | SSE |
| `588000` | 科创50ETF | SSE |
| `588080` | 科创板50ETF | SSE |
| `159919` | 沪深300ETF (深) | SZSE |
| `159915` | 创业板ETF | SZSE |
| `159922` | 中证500ETF (深) | SZSE |
| `159901` | 深100ETF | SZSE |

### CFFEX index options

| Code | Underlying |
|---|---|
| `IO` | 沪深300 指数 |
| `MO` | 中证1000 指数 |
| `HO` | 上证50 指数 |

Run `underlyings` for a parseable list (no akshare needed for this
subcommand).

## Subcommand semantics

### `expiries CODE`
Returns the listed expiry months. ETF format: `YYYYMM` (e.g. `202607`).
CFFEX format: `YYMM` (e.g. `2607`).

### `chain CODE --expiry M`
Full chain for one month. ETF: `--expiry YYYYMM`. CFFEX: `--expiry YYMM`.

Each row carries strike, call/put symbol, last price, bid/ask, IV, OI, vol.

### `pcr CODE`
Aggregate put/call ratio + IV summary across the chain. AKShare returns a
multi-period table; useful for sentiment monitoring.

## Trading hours

CN options share the underlying equity-market hours:
- ETF options: 09:30–11:30, 13:00–15:00
- CFFEX index options: 09:30–11:30, 13:00–15:00 (no night session)

Outside hours, last-traded values are stale (no live tick); IV / OI freeze
at close.

## AKShare function mapping

| Subcommand | AKShare function | Source |
|---|---|---|
| `expiries` ETF | `option_sse_list_sina` / `option_szse_list_sina` | SSE / SZSE via Sina mirror |
| `expiries` CFFEX | `option_cffex_hs300_list_sina` etc. | CFFEX via Sina |
| `chain` ETF | `option_finance_board` | SSE金融期权 / SZSE |
| `chain` CFFEX | `option_cffex_hs300_spot_sina` etc. | CFFEX |
| `pcr` | `option_value_analysis_em` | Eastmoney |

If AKShare renames or removes a function, patch the dispatch dict in
`scripts/options.py`.

## Greeks

Not returned. AKShare exposes IV; for Greeks, compute Black–Scholes locally
using:
- spot = `bin/cn/equity.py quote CODE` last price
- strike, time-to-expiry from the chain row
- IV from the chain row
- risk-free = `macro-rates-fx/scripts/rates.py series 1Y` latest
- dividend yield: 0 for ETF options on broad-index ETFs (close enough)

## Gotchas

- ETF option chain endpoint changes form occasionally on SSE side. If
  `chain` returns empty rows with no error, upgrade AKShare.
- CFFEX symbols use the standard letter-month codes (`IO2509-C-3900`).
  Wrapper sends just the month query string; AKShare assembles the rest.