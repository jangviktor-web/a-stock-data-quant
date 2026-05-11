# quant-china 🇨🇳

A股量化分析工具箱 — 技术指标、形态识别、策略回测、多股对比、市场扫描

## 功能

- 📊 **综合分析** — 一次出完整报告：行情+指标+形态+策略信号+回测
- 🧪 **策略回测** — 7种策略：均线交叉、MACD、RSI、布林带、KDJ、买入持有、**多策略共振(ensemble)**
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

## 子命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `analyze` | 综合分析（数据+指标+形态+策略+回测） | `analyze sh000001` |
| `compare` | 多股对比 | `compare sh600519,sz000858` |
| `backtest` | 单策略回测 | `backtest sh510500 -s ensemble` |
| `scan` | 市场扫描 | `scan --strategy macd` |
| `data` | 获取行情数据 | `data sh000001 -n 30` |
| `indicators` | 技术指标计算 | `indicators sh000001 -i ma5,macd,rsi` |
| `pattern` | 形态识别 | `pattern sh000001` |
| `fund` | 资金面分析 | `fund sh600519` |
| `list` | 列出可用资源 | `list` |

## 策略说明

### 单一策略
- **ma_cross** — MA5/MA20 金叉死叉
- **macd** — DIF/DEA 交叉
- **rsi** — RSI超买(>70)卖出，超卖(<30)买入
- **boll** — 触及布林上轨卖出，下轨买入
- **kdj** — K/D金叉死叉

### 🆕 多策略共振 (ensemble)
5个策略投票，≥N个同时看多才出买入信号。过滤假信号，减少交易次数。

```bash
# 默认3个策略同意才出信号
python3 bin/quant.py backtest sh510500 --strategy ensemble

# 多股对比时附带ensemble回测
python3 bin/quant.py compare sh601212,sh603993,sz300811 --ensemble 3
```

## K线周期

| 周期 | 参数 | 说明 |
|------|------|------|
| 日线 | `1d` | 默认 |
| 周线 | `1w` | |
| 月线 | `1M` | |
| 1分钟 | `1m` | |
| 5分钟 | `5m` | |
| 15分钟 | `15m` | |
| 30分钟 | `30m` | |
| 60分钟 | `60m` | |

## 股票代码格式

- 沪市：`sh` + 代码，如 `sh600519`（贵州茅台）、`sh000001`（上证指数）
- 深市：`sz` + 代码，如 `sz000858`（五粮液）、`sz399006`（创业板指）

## 输出示例

```
📊 综合分析: sh510500
  最新价: 8.91  涨跌: +1.63%

📈 技术指标
  MA5  :    8.71  ↑ 偏离 +2.34%
  MACD:  DIF=0.186  DEA=0.124  → 金叉看多
  RSI14: 72.38  → 超买 ⚠️

🧪 策略回测
  buy_hold      +63.53%  +28.13%   19.87%   1.1486
  ma_cross      +85.04%  +36.37%   12.07%   1.7939  🏆
  ensemble      +74.72%  +32.48%   17.86%   1.3200
```

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
└── LICENSE               # MIT License
```

## 技术指标库

内置 MyTT 技术指标库，支持：

MA, EMA, SMA, MACD, KDJ, RSI, BOLL, CCI, WR, ATR, BIAS, OBV, DMI, TRIX, VR, EMV, BBI, MFI, ASI, PSY

## 致谢

- [Ashare](https://github.com/mpquant/Ashare) — 行情数据接口
- [akshare](https://github.com/akfamily/akshare) — A股数据接口
- [MyTT](https://github.com/mpquant/MyTT) — 技术指标库
- [ScottZt/jin-ce-zhi-suan](https://github.com/ScottZt/jin-ce-zhi-suan) — 策略灵感

## License

MIT
