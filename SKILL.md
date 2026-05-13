---
name: quant-china
description: "A股量化分析工具箱。触发词：量化、选股、回测、技术分析、股票对比、市场扫描、均线、MACD、RSI、KDJ、布林带、资金流向、形态识别。用途：分析单只股票技术面、对比多只股票、回测交易策略、扫描市场热点、查看资金流向。入口：python3 bin/quant.py <命令> <股票代码>"
---

# quant-china — A股量化分析工具箱

> 基于 akshare + MyTT 的命令行量化工具，支持技术指标、形态识别、策略回测、多股对比、市场扫描。

**⚠️ 免责声明**：本工具仅供学习研究，不构成投资建议。技术分析基于历史数据，不预测未来。

---

## TL;DR

```bash
# 分析一只股票
python3 bin/quant.py analyze sh600519

# 对比多只股票
python3 bin/quant.py compare sh600519,sz000858,sh601212

# 回测策略
python3 bin/quant.py backtest sh510500 --strategy ensemble
```

---

## 安装

```bash
pip install akshare numpy pandas requests
# 失败时尝试：pip3 install 或 pip install --user
```

---

## 我该怎么用？（决策树）

```
用户问了什么？
│
├─ "分析某只股票" ──────────→ analyze 命令
├─ "哪只股票更强" ──────────→ compare 命令
├─ "回测某个策略" ──────────→ backtest 命令
├─ "今天市场有什么信号" ────→ scan 命令
├─ "RSI/MACD/均线多少" ────→ indicators 命令
├─ "有没有W底/形态" ──────→ pattern 命令
├─ "主力资金怎么样" ──────→ fund 命令
└─ "有哪些功能" ──────────→ list 命令
```

---

## 股票代码速查

| 市场 | 格式 | 示例 |
|------|------|------|
| 沪市 | `sh` + 6位 | `sh600519`(茅台)、`sh000001`(上证指数)、`sh510500`(中证500ETF) |
| 深市 | `sz` + 6位 | `sz000858`(五粮液)、`sz399006`(创业板指) |

> 用户说"茅台"→ 用 `sh600519`；说"中证500"→ 用 `sh510500`

---

## 命令详解

### 1. analyze — 综合分析（推荐入口）

一次出完整报告：行情 + 指标 + 形态 + 策略信号 + 回测。

```bash
python3 bin/quant.py analyze sh600519                        # 默认日线
python3 bin/quant.py analyze sh600519 --period 1w --count 500  # 周线500根
python3 bin/quant.py analyze sh510500 --capital 200000 --stop-loss 0.05  # 带资金和止损
```

**输出示例**：
```
📊 综合分析: sh510500
最新价: 8.91 涨跌: +1.63%

📈 技术指标
 MA5 : 8.71 ↑ 偏离 +2.34%
 MACD: DIF=0.186 DEA=0.124 → 金叉看多
 RSI14: 72.38 → 超买 ⚠️

🧪 策略回测
 buy_hold +63.53%  最大回撤 19.87%  夏普 1.15
 ma_cross +85.04%  最大回撤 12.07%  夏普 1.79 🏆
 ensemble +74.72%  最大回撤 17.86%  夏普 1.32
```

**怎么解读**：

| 看到 | 意味着 | 建议 |
|------|--------|------|
| MA5 ↑ 偏离>2% | 短期涨太快 | 注意回调风险 |
| MACD 金叉 | 中期动能向上 | 偏多 |
| RSI >70 | 超买 | 不宜追高 |
| ensemble 跑赢 buy_hold | 策略有超额收益 | 可参考信号 |
| 最大回撤 >15% | 波动大 | 需设止损 |

---

### 2. compare — 多股对比

```bash
python3 bin/quant.py compare sh600519,sz000858,sh601212          # 三股对比
python3 bin/quant.py compare sh601212,sh603993,sz300811 --ensemble 3  # 带ensemble回测
python3 bin/quant.py compare sh000001,sz399001,sz399006 --period 1w   # 周线对比
```

**输出**：各股技术指标并排 + 综合评分排名。评分最高 = 技术面最强。

---

### 3. backtest — 策略回测

```bash
python3 bin/quant.py backtest sh510500 --strategy ma_cross
python3 bin/quant.py backtest sh510500 --strategy ensemble         # 多策略共振
python3 bin/quant.py backtest sh600519 --strategy rsi --capital 200000 --stop-loss 0.05
```

**可用策略**：

| 策略 | 逻辑 | 适用场景 |
|------|------|---------|
| `buy_hold` | 买入持有（基准） | 对比基准 |
| `ma_cross` | MA5/MA20 金叉死叉 | 趋势行情 |
| `macd` | DIF/DEA 交叉 | 中期趋势 |
| `rsi` | RSI 超买超卖 | 震荡行情 |
| `boll` | 布林带轨道反弹 | 区间震荡 |
| `kdj` | KDJ 金叉死叉 | 短线交易 |
| `ensemble` | **多策略共振（推荐）** | 过滤假信号 |

**关键指标解读**：
- 总收益率 vs 基准 → 策略是否跑赢买入持有
- 最大回撤 <15% → 较健康
- 夏普比率 >1 → 较好，>2 → 优秀
- 胜率 >50% → 正期望

---

### 4. scan — 市场扫描

```bash
python3 bin/quant.py scan --strategy macd                    # MACD金叉扫描
python3 bin/quant.py scan --strategy ma_cross --min-volume 1000000  # 均线交叉+成交量筛选
```

---

### 5. indicators — 技术指标

```bash
python3 bin/quant.py indicators sh600519 --indicators ma5,ma10,ma20,macd,rsi
python3 bin/quant.py indicators sh600519 --indicators boll,kdj,cci,wr,atr,bias,obv
```

**可选指标**：MA, EMA, MACD, RSI, BOLL, KDJ, CCI, WR, ATR, BIAS, OBV

---

### 6. pattern — 形态识别

```bash
python3 bin/quant.py pattern sh600519                            # 识别所有形态
python3 bin/quant.py pattern sh600519 --pattern w-bottom,cup-handle  # 指定形态
```

**可识别形态**：W底(`w-bottom`)、V型反转(`v-reversal`)、杯柄(`cup-handle`)、三重底(`triple-bottom`)、回踩买入(`dip-buy`)、Zigzag转折点

---

### 7. fund — 资金面分析

```bash
python3 bin/quant.py fund sh600519
```

输出：主力资金净流入/流出、大单/中单/小单资金流向。

---

### 8. data — 原始行情数据

```bash
python3 bin/quant.py data sh600519 --count 30               # 最近30天日线
python3 bin/quant.py data sh600519 --period 15m --count 50   # 15分钟线
```

---

### 9. list — 查看可用资源

```bash
python3 bin/quant.py list
```

---

## K线周期

`1d`(日线) | `1w`(周线) | `1M`(月线) | `1m` | `5m` | `15m` | `30m` | `60m`

---

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

---

## 输出格式

data、indicators、pattern、backtest 命令支持 `--json` 参数输出 JSON。

---

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
├── requirements.txt      # Python 依赖
└── LICENSE               # MIT
```

---

## 异常处理

| 场景 | 处理 |
|------|------|
| 依赖未安装 | `pip install akshare numpy pandas requests` |
| 代码格式错 | 提示 `sh`/`sz` + 6位数字 |
| 数据不可用 | 换股票或稍后重试 |
| 网络超时 | 检查连接后重试 |
| 扫描为空 | 放宽筛选条件 |
| 回测太短 | 建议至少100个交易日 |

---

## 工作流模板

### 场景A：分析一只股票
```
用户："茅台技术面怎么样"
→ python3 bin/quant.py analyze sh600519
→ 解读：趋势方向 + MACD/RSI信号 + 回测结果
→ 建议：是否需要对比其他股票或回测策略
```

### 场景B：选股对比
```
用户："茅台五粮液泸州老窖哪个强"
→ python3 bin/quant.py compare sh600519,sz000858,sh601212
→ 解读：综合评分排名 + 各指标对比
→ 建议：对最强的做详细分析
```

### 场景C：策略验证
```
用户："ensemble策略回测中证500"
→ python3 bin/quant.py backtest sh510500 --strategy ensemble
→ 解读：收益率/回撤/夏普 vs buy_hold
→ 建议：是否调整参数或换策略
```

---

## License

MIT
