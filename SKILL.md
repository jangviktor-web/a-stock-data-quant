---
name: quant-china
description: A股量化分析工具箱 — 技术指标、形态识别、策略回测、多股对比、市场扫描
---

# quant-china

A股量化分析工具箱。通过命令行或 OpenClaw 调用。

## 安装

```bash
pip install akshare numpy pandas requests
```

## 快速开始

```bash
# 综合分析（推荐入口）
python3 bin/quant.py analyze sh000001

# 多股对比
python3 bin/quant.py compare sh600519,sz000858,sh601212

# 策略回测（含多策略共振）
python3 bin/quant.py backtest sh510500 --strategy ensemble

# 市场扫描
python3 bin/quant.py scan --strategy ma_cross

# 列出所有可用指标/策略/形态
python3 bin/quant.py list
```

## 子命令

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

可用策略：`buy_hold`, `ma_cross`, `macd`, `rsi`, `boll`, `kdj`, `ensemble`

### scan — 市场扫描
```bash
python3 bin/quant.py scan --strategy macd
python3 bin/quant.py scan --strategy ma_cross --min-volume 1000000
```

### data — 行情数据
```bash
python3 bin/quant.py data sh000001 --count 30
python3 bin/quant.py data sh600519 --period 15m --count 50
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

## 股票代码格式

- 沪市：`sh` + 代码（如 `sh600519`、`sh000001`）
- 深市：`sz` + 代码（如 `sz000858`、`sz399006`）

## 技术指标

MA, EMA, MACD, RSI, BOLL, KDJ, CCI, WR, ATR, BIAS, OBV

## 策略

| 策略 | 说明 |
|------|------|
| buy_hold | 买入持有 |
| ma_cross | MA5/MA20 金叉死叉 |
| macd | DIF/DEA 交叉 |
| rsi | RSI超买超卖 |
| boll | 布林带轨道反弹 |
| kdj | KDJ金叉死叉 |
| **ensemble** | **多策略共振（≥N个策略同时看多才出信号）** |

## 形态识别

W底(w-bottom)、V型反转(v-reversal)、杯柄(cup-handle)、三重底(triple-bottom)、回踩买入(dip-buy)、Zigzag转折点

## K线周期

`1d`(日线), `1w`(周线), `1M`(月线), `1m`, `5m`, `15m`, `30m`, `60m`

## 输出格式

支持 `--json` 参数输出 JSON 格式（data、indicators、pattern、backtest 命令）

## License

MIT
