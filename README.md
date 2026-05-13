# quant-china

A股量化分析工具箱 — 技术指标、形态识别、策略回测、多股对比、市场扫描

## 功能

- 📊 **综合分析** — 一次出完整报告：行情+指标+形态+策略信号+回测
- 🧪 **策略回测** — 7种策略：均线交叉、MACD、RSI、布林带、KDJ、买入持有、多策略共振(ensemble)
- 🔍 **形态识别** — W底、V型反转、杯柄、三重底、回踩买入
- 📈 **多股对比** — 并排对比多只股票的技术面和策略信号
- 📡 **市场扫描** — 全市场板块扫描，按策略信号排序
- 💰 **资金面分析** — 主力资金流向、融资融券数据

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

## 命令速查

| 命令 | 说明 | 示例 |
|------|------|------|
| `analyze` | 综合分析 | `python3 bin/quant.py analyze sh000001` |
| `compare` | 多股对比 | `python3 bin/quant.py compare sh600519,sz000858` |
| `backtest` | 策略回测 | `python3 bin/quant.py backtest sh510500 -s ensemble` |
| `scan` | 市场扫描 | `python3 bin/quant.py scan --strategy macd` |
| `data` | 获取行情 | `python3 bin/quant.py data sh000001 -n 30` |
| `indicators` | 技术指标 | `python3 bin/quant.py indicators sh000001 -i ma5,macd,rsi` |
| `pattern` | 形态识别 | `python3 bin/quant.py pattern sh000001` |
| `fund` | 资金面分析 | `python3 bin/quant.py fund sh600519` |
| `list` | 列出可用资源 | `python3 bin/quant.py list` |

## 可用策略

| 策略 | 说明 |
|------|------|
| `buy_hold` | 买入持有 |
| `ma_cross` | MA5/MA20 金叉死叉 |
| `macd` | DIF/DEA 交叉 |
| `rsi` | RSI超买超卖 |
| `boll` | 布林带轨道反弹 |
| `kdj` | KDJ金叉死叉 |
| `ensemble` | 多策略共振（≥N个策略同时看多才出信号） |

## 股票代码格式

- 沪市：`sh` + 代码，如 `sh600519`（贵州茅台）、`sh000001`（上证指数）
- 深市：`sz` + 代码，如 `sz000858`（五粮液）、`sz399006`（创业板指）

## K线周期

`1d`(日线), `1w`(周线), `1M`(月线), `1m`, `5m`, `15m`, `30m`, `60m`

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

## 内置技术指标

MA, EMA, SMA, MACD, KDJ, RSI, BOLL, CCI, WR, ATR, BIAS, OBV, DMI, TRIX, VR, EMV, BBI, MFI, ASI, PSY

## 致谢

- [Ashare](https://github.com/mpquant/Ashare) — 行情数据接口
- [akshare](https://github.com/akfamily/akshare) — A股数据

## License

MIT
