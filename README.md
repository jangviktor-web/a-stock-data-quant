# quant-china

A股量化分析工具箱 — 技术指标、形态识别、策略回测、多股对比、市场扫描

> 🏷️ 版本: `2026.5.13` | 基于 [akshare](https://github.com/akfamily/akshare) + [MyTT](https://github.com/mpquant/MyTT) 构建

## 功能

| 功能 | 命令 | 说明 |
|------|------|------|
| 📊 综合分析 | `analyze` | 一次出完整报告：行情+指标+形态+策略信号+回测 |
| 🧪 策略回测 | `backtest` | 7种策略：均线交叉、MACD、RSI、布林带、KDJ、买入持有、多策略共振 |
| 🔍 形态识别 | `pattern` | W底、V型反转、杯柄、三重底、回踩买入 |
| 📈 多股对比 | `compare` | 并排对比多只股票的技术面和策略信号 |
| 📡 市场扫描 | `scan` | 全市场板块扫描，按策略信号排序 |
| 💰 资金面分析 | `fund` | 主力资金流向、大中小单分析 |
| 📉 技术指标 | `indicators` | MA/MACD/RSI/KDJ/BOLL/CCI/ATR/OBV 等 20+ 指标 |

## 快速开始

```bash
# 安装依赖
pip install akshare numpy pandas requests

# 综合分析（推荐入口）
python3 bin/quant.py analyze sh000001

# 多股对比
python3 bin/quant.py compare sh600519,sz000858,sh601212

# 策略回测
python3 bin/quant.py backtest sh510500 --strategy ensemble

# 市场扫描
python3 bin/quant.py scan --strategy ma_cross

# 列出所有可用指标/策略/形态
python3 bin/quant.py list
```

## 命令详解

### analyze — 综合分析

一次出完整报告：行情概览 + 技术指标 + 形态识别 + 策略信号 + 策略回测

```bash
python3 bin/quant.py analyze sh000001
python3 bin/quant.py analyze sh600519 --period 1w --count 500
python3 bin/quant.py analyze sh510500 --capital 200000 --stop-loss 0.05
```

### compare — 多股对比

并排对比多只股票的技术面、信号和回测结果

```bash
python3 bin/quant.py compare sh600519,sz000858,sh601212
python3 bin/quant.py compare sh601212,sh603993,sz300811 --ensemble 3
python3 bin/quant.py compare sh000001,sz399001,sz399006 --period 1w
```

### backtest — 策略回测

```bash
python3 bin/quant.py backtest sh510500 --strategy ma_cross
python3 bin/quant.py backtest sh510500 --strategy ensemble
python3 bin/quant.py backtest sh600519 --strategy rsi --capital 200000 --stop-loss 0.05
```

### scan — 市场扫描

```bash
python3 bin/quant.py scan --strategy macd
python3 bin/quant.py scan --strategy ma_cross --min-volume 1000000
```

### indicators — 技术指标

```bash
python3 bin/quant.py indicators sh000001 --indicators ma5,ma10,ma20,macd,rsi
python3 bin/quant.py indicators sh600519 --indicators boll,kdj,atr20
```

### pattern — 形态识别

```bash
python3 bin/quant.py pattern sh000001
python3 bin/quant.py pattern sh600519 --pattern w-bottom,cup-handle
```

### fund — 资金面分析

```bash
python3 bin/quant.py fund sh600519
```

### data — 行情数据

```bash
python3 bin/quant.py data sh000001 --count 30
python3 bin/quant.py data sh600519 --period 15m --count 50
```

## 可用策略

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| `buy_hold` | 买入持有 | 基准对比 |
| `ma_cross` | MA5/MA20 金叉死叉 | 趋势行情 |
| `macd` | DIF/DEA 交叉 | 中期趋势 |
| `rsi` | RSI超买超卖 | 震荡行情 |
| `boll` | 布林带轨道反弹 | 区间震荡 |
| `kdj` | KDJ金叉死叉 | 短线交易 |
| `ensemble` | **多策略共振（推荐）** | 过滤假信号 |

## 参数速查

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--period` | K线周期 | `1d` |
| `--count` | 数据条数 | `120` |
| `--strategy` | 策略名 | `buy_hold` |
| `--capital` | 初始资金 | `100000` |
| `--stop-loss` | 止损比例(如0.05=5%) | 无 |
| `--ensemble N` | 共振阈值 | `3` |
| `--json` | 输出JSON格式 | — |

## 股票代码格式

- 沪市：`sh` + 代码，如 `sh600519`（贵州茅台）、`sh000001`（上证指数）、`sh510500`（中证500ETF）
- 深市：`sz` + 代码，如 `sz000858`（五粮液）、`sz399006`（创业板指）

## K线周期

`1d`(日线) | `1w`(周线) | `1M`(月线) | `1m`(1分钟) | `5m`(5分钟) | `15m`(15分钟) | `30m`(30分钟) | `60m`(60分钟)

## 形态识别

| 形态 | 参数 | 说明 |
|------|------|------|
| W底 | `w-bottom` | 双底形态，底部反转信号 |
| V型反转 | `v-reversal` | 急跌后快速反弹 |
| 杯柄 | `cup-handle` | 杯底+柄部，突破买入 |
| 三重底 | `triple-bottom` | 三次探底不破 |
| 回踩买入 | `dip-buy` | 上升趋势中的回调买点 |

## 内置技术指标

MA, EMA, SMA, MACD, KDJ, RSI, BOLL, CCI, WR, ATR, BIAS, OBV, DMI, TRIX, VR, EMV, BBI, MFI, ASI, PSY

## 项目结构

```
quant-china/
├── bin/
│   ├── quant.py          # CLI 主入口
│   └── stock_full.py     # 综合分析脚本
├── lib/
│   ├── akshare_data.py   # akshare 数据层
│   ├── ashare.py         # 行情数据获取
│   ├── backtest.py       # 回测引擎
│   ├── mytt.py           # 技术指标库（MyTT）
│   ├── patterns.py       # 形态识别
│   └── strategies.py     # 策略模块
├── SKILL.md              # OpenClaw skill 文档
├── README.md             # 本文件
├── requirements.txt      # Python 依赖
└── LICENSE               # MIT
```

## 致谢

- [Ashare](https://github.com/mpquant/Ashare) — 行情数据接口
- [akshare](https://github.com/akfamily/akshare) — A股数据

## License

MIT
