# equity.py — advanced reference

A-share + HK quote/history, indices, search, and CN-only signals (北向资金,
涨跌停, 行业/题材板块).

## Code conventions

| Pattern | Market |
|---|---|
| `600xxx`, `601xxx`, `603xxx`, `605xxx`, `688xxx` | 上海主板 + 科创板 (sh) |
| `000xxx`, `002xxx`, `300xxx` | 深圳主板 + 创业板 (sz) |
| `8xxxxx`, `4xxxxx`, `92xxxx` | 北交所 (bj) |
| `9xxxx` (5-digit) | 上海B股 |
| `2xxxx` (5-digit) | 深圳B股 |
| `0xxxx` (5-digit) | 港股 (e.g. `00700` Tencent) |
| `90xxxxx` (Eastmoney secid) | 板块 (industry / concept boards) |

`equity.py quote` auto-detects A-share vs HK from the code shape.

## Batched A-share quote

Single HTTP for many symbols via Sina:
```bash
./scripts/equity.py quote 600519,000001,300750,000858,002594
```
returns 5 rows in one network call. This is why we use Sina as primary for
A-share — Eastmoney and Tencent require one call per symbol.

## HK quote fallback chain

`116.{code}` (Eastmoney) → `hk{code}` (Sina) → `hk{code}` (Tencent) →
`{code}.HK` (Yahoo, leading-zero stripped to 4-digit).

Each tier kicks in only for rows the previous tier failed on (per-row, not
per-batch).

## Index aliases

| Friendly | Eastmoney secid | Yahoo fallback |
|---|---|---|
| `SSE`, `上证` | `1.000001` | — |
| `SZSE`, `深证` | `0.399001` | — |
| `HS300`, `沪深300` | `1.000300` | — |
| `ZZ500`, `中证500` | `1.000905` | — |
| `ZZ1000`, `中证1000` | `1.000852` | — |
| `ChiNext`, `创业板指` | `0.399006` | — |
| `STAR50`, `科创50` | `1.000688` | — |
| `HSI`, `恒生指数` | `100.HSI` | `^HSI` |
| `HSCEI`, `国企指数` | `100.HSCEI` | `^HSCE` |
| `HSTECH`, `恒生科技` | `100.HSTECH` | `^HSTECH` |

## CN-only signals

### `northbound [--days N]`
Daily net flow for 沪股通 + 深股通 + 港股通 (北上 + 南下). Source:
`push2.eastmoney.com/api/qt/kamt/get`.

### `limit-up` / `limit-down`
Today's 涨停板 / 跌停板 list, ranked. Filtered from `clist/get` with
`m:0+t:6` / `m:0+t:7`.

### `industry` / `concept`
板块 ranked by gain. `industry` = SW 一级行业 (~30 sectors); `concept` =
题材 (~200+ boards). Use `industry` for sector rotation, `concept` for
event-driven theme tracking.

## Burst limit

Eastmoney: ~20 calls / 5s → multi-minute blackhole, surfaces as
`RemoteDisconnected` / `502` / empty body. Pace HK-quote batches in
particular (no upstream fallback for CN-only signal endpoints).

## History gap

`history` uses Eastmoney exclusively. No fallback. If Eastmoney is in
blackhole, history calls fail until the IP recovers.