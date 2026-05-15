---
name: quant-china
description: "A股量化分析工具箱。触发词：量化、选股、回测、技术分析、股票对比、市场扫描、均线、MACD、RSI、KDJ、布林带、资金流向、形态识别、实时行情、搜索股票、东方财富、AI诊断、AI选股、AI问答。用途：分析单只股票技术面、对比多只股票、回测交易策略、扫描市场热点、查看资金流向、实时报价、AI金融分析。入口：python3 bin/quant.py <命令> <股票代码>。支持 --html 输出交互式图表。em-* 命令调用东方财富妙想AI。realtime/search 命令基于腾讯/东方财富实时接口。"
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

# 输出HTML图表（交互式K线+信号+交易明细）
python3 bin/quant.py analyze sh600519 --html
python3 bin/quant.py backtest sh510500 --strategy ensemble --html

# 数据缓存管理
python3 bin/quant.py cache stats
python3 bin/quant.py cache clear
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

## 检查点（Checkpoints）

在以下节点暂停，确认后再继续：

### 🔒 检查点A：执行前确认
执行 analyze/compare/backtest/scan 前：
- 确认股票代码是否正确（用户说"茅台"→ sh600519）
- 确认参数（周期、策略、资金量）
- **不想执行时**：展示完整命令 + 预期输出示例 + 解读方式，让用户自行决定
- 用户说"不用了"/"只看看"/"告诉我怎么操作" → 进入"展示模式"，不调用命令

### 🔒 检查点B：结果解读
输出结果后，主动提供：
- 一句话总结（"技术面偏多/偏空/震荡"）
- 关键信号解读（引用具体数值，说明"这意味着什么"）
- 后续建议（是否需要深入其他维度）

### 🔒 检查点C：投资建议前
在给出任何"买入/卖出/持有"倾向的结论前：
- 明确声明"技术分析仅供参考，不构成投资建议"
- 建议结合基本面、消息面综合判断

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

**输出示例**：
```
📡 市场扫描  策略: macd  周期: 1d
扫描时间: 2026-05-13 15:00

代码         名称      现价    涨跌%   信号     RSI    成交量(万)
--------------------------------------------------------------
sh600519    贵州茅台  1344.09  -0.77   金叉     32.0    477
sz000858    五粮液     89.15   -1.56   无信号   16.0    312
sh601212    白酒ETF     7.77   -1.40   金叉     44.0    198
...
共扫描 200 只股票, 发现 15 个金叉信号
```

**解读**：扫描结果按信号排序，金叉=潜在买入机会。结合RSI过滤超买（>70不追），成交量太低的（<100万）流动性差，谨慎参与。

---

### 5. indicators — 技术指标

```bash
python3 bin/quant.py indicators sh600519 --indicators ma5,ma10,ma20,macd,rsi
python3 bin/quant.py indicators sh600519 --indicators boll,kdj,cci,wr,atr,bias,obv
```

**输出示例**：
```
📈 技术指标: sh600519  周期: 1d

指标        当前值      信号
----------------------------
MA5       1360.80     ↓ 下行
MA10      1377.32     ↓ 下行
MA20      1405.54     ↓ 下行
MACD      DIF=-21.67  DEA=-14.70  死叉看空
RSI14     32.00       中性
```

**解读**：指标单独查看，适合需要特定指标的场景。多指标交叉验证更可靠（如MACD金叉+RSI中性=较安全的买入信号）。

---

### 6. pattern — 形态识别

```bash
python3 bin/quant.py pattern sh600519                            # 识别所有形态
python3 bin/quant.py pattern sh600519 --pattern w-bottom,cup-handle  # 指定形态
```

**输出示例**：
```
🔍 形态识别: sh600519

形态          数量    最近位置    深度     状态
------------------------------------------------
w-bottom      4       位置[456]  11.3%    ✅ 已确认
v-reversal    2       位置[480]  5.6%     ✅ 已确认
cup-handle    1       位置[?]    8.6%     ⏳ 形成中
triple-bottom 1       位置[?]    11.3%    ⏳ 形成中
dip-buy       0       -          -        ❌ 未检测到
```

**解读**：
- W底/V型反转/杯柄 = 底部形态，关注突破颈线的买点
- "已确认"比"形成中"更可靠
- 深度越大，后续反弹空间通常越大

---

### 7. fund — 资金面分析

```bash
python3 bin/quant.py fund sh600519
```

**输出示例**：
```
💰 资金面: sh600519

主力资金: 净流入 +1.23亿
大单: 净流入 +0.89亿
中单: 净流入 +0.34亿
小单: 净流出 -0.12亿

近5日主力资金: +0.5, -0.3, +1.1, +0.8, +1.2 (亿)
```

**解读**：
- 主力净流入=机构在买，偏多信号
- 大单+中单同时流入=较健康的资金推动
- 小单流出+主力流入=散户卖、机构买，通常是好信号
- 连续3日以上主力流入=资金面趋势确认

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

### 输出示例与行动映射

#### 常见输出→行动
| 看到什么 | 意味着什么 | 建议行动 |
|---------|-----------|---------|
| MACD金叉 + RSI<70 + 多头排列 | 技术面偏多 | 可关注，逢低布局 |
| MACD死叉 + RSI>70 + 空头排列 | 技术面偏空 | 注意风险，减仓观望 |
| MA5偏离>3% | 短期涨太快 | 不宜追高，等回调 |
| ensemble夏普>1.5且跑赢基准 | 策略有效 | 可参考信号操作 |
| 最大回撤>20% | 波动大 | 需严格止损，控制仓位 |
| compare评分差>20分 | 强弱分明 | 关注评分最高的 |

#### compare 输出示例
```
┌─────────┬────────┬────────┬──────────┐
│ 指标     │ 茅台   │ 五粮液  │ 泸州老窖  │
├─────────┼────────┼────────┼──────────┤
│ 趋势     │ 多头   │ 震荡   │ 多头      │
│ MACD     │ 金叉   │ 死叉   │ 金叉      │
│ RSI      │ 65     │ 45     │ 58       │
│ 综合评分  │ 82     │ 58     │ 75       │
└─────────┴────────┴────────┴──────────┘
```
→ 综合评分最高 = 技术面最强。茅台82分 > 泸州老窖75分 > 五粮液58分。

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
→ 🔒 检查点A：确认代码 sh600519，确认是否需要指定参数
→ python3 bin/quant.py analyze sh600519
→ 🔒 检查点B：一句话总结 + 关键信号解读 + 引用数值
→ 建议：是否需要对比其他股票或回测策略
→ 🔒 检查点C：如涉及买卖建议，声明免责
```

### 场景B：选股对比
```
用户："茅台五粮液泸州老窖哪个强"
→ 🔒 检查点A：确认三只股票代码
→ python3 bin/quant.py compare sh600519,sz000858,sh601212
→ 🔒 检查点B：排名 + 各指标对比表 + 一句话结论
→ 建议：对最强的做详细分析
```

### 场景C：策略验证
```
用户："ensemble策略回测中证500"
→ 🔒 检查点A：确认代码 sh510500，确认策略 ensemble
→ python3 bin/quant.py backtest sh510500 --strategy ensemble
→ 🔒 检查点B：收益率/回撤/夏普 vs buy_hold + 策略是否有效的结论
→ 🔒 检查点C：声明回测结果不代表未来表现
→ 建议：是否调整参数或换策略
```

---

## 复合场景处理

当用户需求涉及多个步骤时，按顺序串联：

```
用户："茅台和五粮液哪个强，顺便看看MACD策略回测"
→ 🔒 检查点A：确认代码 sh600519,sz000858 + 策略 macd
→ Step 1: python3 bin/quant.py compare sh600519,sz000858
→ Step 2: python3 bin/quant.py backtest sh600519 --strategy macd
→ Step 3: python3 bin/quant.py backtest sz000858 --strategy macd
→ 🔒 检查点B：综合compare结果+两只股票的回测表现，给出结论
```

```
用户："扫描今天MACD金叉的股票，然后对最强的做详细分析"
→ Step 1: python3 bin/quant.py scan --strategy macd
→ Step 2: 从扫描结果中选评分最高的
→ Step 3: python3 bin/quant.py analyze {最强股票代码}
→ 🔒 检查点B：结合扫描信号+详细分析，给出操作建议
```

## 异常处理（补充）

| 场景 | 处理 |
|------|------|
| akshare API 限流 | 降低请求频率，批量分析时加 2-3秒间隔；如遇 429 错误，等待 30秒重试 |
| 股票停牌 | 提示"该股票已停牌，数据可能不完整"，建议查看复牌后的走势 |
| 非交易时段 | 数据为上一交易日收盘数据，提示"当前为非交易时段，数据截至上一交易日" |
| 数据异常（价格为0/NaN） | 过滤异常数据点，提示"部分数据异常，分析结果可能受影响" |
| 股票退市/不存在 | 提示"未找到该股票数据"，检查代码是否正确 |
| 周线/月线数据不足 | 自动降级到日线，提示"周线数据不足，已切换为日线分析" |

## 数据流向图

```
用户输入（股票代码/问题）
    ↓
意图路由（决策树）
    ↓
┌─────────────────────────────────────────┐
│           quant.py CLI 主入口            │
├─────────┬─────────┬─────────┬───────────┤
│ analyze │ compare │ backtest│ scan      │
├─────────┼─────────┼─────────┼───────────┤
│         ↓         ↓         ↓           │
│    akshare_data.py  ← 数据获取层        │
│         ↓                               │
│    ashare.py  ← 行情数据处理            │
│         ↓                               │
│    mytt.py  ← 技术指标计算              │
│    patterns.py  ← 形态识别              │
│    strategies.py  ← 策略信号            │
│    backtest.py  ← 回测引擎              │
└─────────────────────────────────────────┘
    ↓
格式化输出（终端/JSON）
    ↓
结果解读 + 行动建议（检查点B）
```

## 新增功能（基于 stock-quant + Aeolus 优化）

### 股票综合诊断 (diagnose)
借鉴 Aeolus stock-diagnosis 设计，整合技术面评分 + 资金面分析 + 基本面数据 + 形态识别，输出综合诊断结论。
```bash
python3 bin/quant.py diagnose sh600519
python3 bin/quant.py diagnose sh518850
```

### 宏观数据查询 (macro)
借鉴 Aeolus MX_MacroData 设计，通过 akshare 免费接口查询中国宏观经济数据。
```bash
python3 bin/quant.py macro cpi       # CPI
python3 bin/quant.py macro pmi       # PMI
python3 bin/quant.py macro gdp       # GDP
python3 bin/quant.py macro m2        # M2货币供应
python3 bin/quant.py macro lpr       # LPR利率
python3 bin/quant.py macro unemployment  # 失业率
python3 bin/quant.py macro trade     # 进出口
python3 bin/quant.py macro industrial    # 工业增加值
```

### 市场热点扫描 (hotspot)
借鉴 Aeolus stock-market-hotspot-discovery 设计，扫描人气榜、概念板块、行业板块涨幅榜。
```bash
python3 bin/quant.py hotspot
python3 bin/quant.py hotspot --top 30
```

### HTML 图表输出
`analyze` 和 `backtest` 支持 `--html` 参数，生成交互式 HTML 图表（K线+均线+信号标注+交易明细），文件保存在 `html/` 目录。

### 数据缓存
自动缓存行情数据到 `cache/` 目录，4小时内不重复请求。使用 `cache stats` 查看缓存状态，`cache clear` 清理。

### 配置管理
通过 `config.yaml` 集中管理参数（资金、手续费、缓存等），命令行参数优先。

### 编码修复
自动设置 UTF-8 编码，解决 Windows 下 emoji 字符显示问题。

### 实时行情 (realtime)
基于 stock-api 协议，集成腾讯/东方财富实时行情接口，无需 akshare。
```bash
# 实时报价（腾讯数据源，自动降级东方财富）
python3 bin/quant.py realtime sh600519,sz000858,sh601212
python3 bin/quant.py realtime sh600519 --source tencent

# 搜索股票（按名称或代码）
python3 bin/quant.py search 茅台
python3 bin/quant.py search 宁德时代
```
compare 命令已自动集成实时价格显示。

### 东方财富妙想 AI (em-*)
集成 [东方财富妙想](https://ai.eastmoney.com/mxClaw) 免费 AI 金融数据接口，提供 AI 驱动的股票诊断、选股、问答等功能。

**配置**：在 `config.yaml` 中设置 `em_api_key`，或设置环境变量 `EM_API_KEY`。
**注册**：[https://ai.eastmoney.com/mxClaw](https://ai.eastmoney.com/mxClaw)

```bash
# AI 股票诊断（自然语言）
python3 bin/quant.py em-diagnose sh600519
python3 bin/quant.py em-diagnose sh600519 -q "贵州茅台未来一周走势分析"

# AI 自然语言选股
python3 bin/quant.py em-pick "市盈率最低的20只股票"
python3 bin/quant.py em-pick "连续上涨的创业板股票" --top 5

# AI 金融问答
python3 bin/quant.py em-ask "什么是量化宽松？对A股有什么影响？"
python3 bin/quant.py em-ask "美联储加息周期对黄金价格的影响" --deep

# AI 资讯搜索
python3 bin/quant.py em-news "人工智能政策" --top 10
python3 bin/quant.py em-news "新能源汽车" --market cn

# AI 基金诊断
python3 bin/quant.py em-fund 招商中证白酒
python3 bin/quant.py em-fund 161725 -q "这只基金适合定投吗"
```

| 命令 | 用途 | 特点 |
|------|------|------|
| `em-diagnose` | 股票综合诊断 | 自动降级到 em-ask，5维度深度分析 |
| `em-pick` | 自然语言选股 | 支持 A股/港股/美股，多种品类 |
| `em-ask` | 金融问答 | `--deep` 启用深度思考 |
| `em-news` | 资讯搜索 | 按市场筛选，AI 总结 |
| `em-fund` | 基金诊断 | 自动降级到 em-ask，6维度基金分析 |

## License

MIT
