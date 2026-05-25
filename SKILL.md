---
name: a-stock-data-quant
version: "3.2.0"
description: "A-share stock quantitative analysis toolkit with 20+ technical indicators, 7 backtesting strategies, candlestick pattern recognition, multi-source data fallback, real-time quotes, AI financial analysis, and 7x24 news. Supports Claude Code, Cursor, Codex, Gemini, and 5+ other AI agents."
keywords: ["stock", "quant", "a-share", "backtest", "technical-analysis", "finance", "akshare", "trading", "investment", "china-stock", "MACD", "RSI", "KDJ", "real-time-quotes", "AI-analysis"]
author: "jangviktor"
license: "MIT"
repository: "https://github.com/jangviktor-web/a-stock-data-quant"
category: "data"
allowedTools:
  - Bash
  - Read
  - Glob
  - Grep
---

# a-stock-data-quant — A股量化分析工具箱

> 技术指标 · 形态识别 · 策略回测 · 实时行情 · 新闻资讯 · AI金融分析（东方财富妙想）

**⚠️ 免责声明**：本工具仅供学习研究，不构成投资建议。技术分析基于历史数据，不预测未来。

**🔄 多数据源**: 主源 akshare 失效时自动降级到备用源（百度/mootdx/datacenter/同花顺），确保数据可用性。

---

## TL;DR

```bash
python3 bin/quant.py analyze sh600519                    # 综合分析
python3 bin/quant.py compare sh600519,sz000858           # 多股对比
python3 bin/quant.py backtest sh510500 --strategy ensemble --html  # 回测+图表
python3 bin/quant.py realtime sh600519,sz000858          # 实时行情
python3 bin/quant.py news                                # 新闻快讯
python3 bin/quant.py em-diagnose sh600519                # AI诊断
python3 bin/quant.py search 白银                          # 搜索股票
```

---

## 安装

### 方式一：SkillHub (推荐，支持9+ AI Agent)

```bash
# Claude Code
npx @skill-hub/cli install a-stock-data-quant --agent claude

# Cursor
npx @skill-hub/cli install a-stock-data-quant --agent cursor

# 其他 Agent (codex/gemini/copilot/windsurf/cline/roo/opencode)
npx @skill-hub/cli install a-stock-data-quant --agent <agent>
```

### 方式二：ClawHub

```bash
clawhub package install a-stock-data-quant
```

### 方式三：GitHub 直接克隆

```bash
cd ~/.claude/skills   # Claude Code
git clone https://github.com/jangviktor-web/a-stock-data-quant.git
```

### 依赖安装

```bash
pip install akshare numpy pandas requests mootdx
# Windows: 用 python 代替 python3
```

---

## 决策树

```
用户问了什么？
│
├─ "分析某只股票" ──────────→ analyze
├─ "哪只股票更强" ──────────→ compare
├─ "回测某个策略" ──────────→ backtest
├─ "今天市场有什么信号" ────→ scan
├─ "RSI/MACD/均线多少" ────→ indicators
├─ "有没有W底/形态" ──────→ pattern
├─ "主力资金怎么样" ──────→ fund
├─ "现在价格多少" ─────────→ realtime
├─ "搜一下XX股票" ─────────→ search
├─ "帮我诊断一下" ─────────→ diagnose
├─ "AI分析/AI选股" ────────→ em-diagnose / em-pick
├─ "AI问答/AI资讯" ────────→ em-ask / em-news
├─ "AI基金分析" ───────────→ em-fund
├─ "宏观数据(CPI/GDP)" ───→ macro
├─ "市场热点" ─────────────→ hotspot
├─ "市场情绪/涨停/跌停" ──→ market
├─ "个股深度/股东/解禁" ──→ info
├─ "缓存管理" ─────────────→ cache
├─ "新闻/快讯/资讯" ────────→ news
└─ "有哪些功能" ───────────→ list
```

---

## 检查点

### 🔒 A：执行前
- 确认代码（"茅台"→ sh600519）、参数（周期、策略、资金量）
- 用户说"不用了"/"只看看" → 展示命令+示例，不执行

### 🔒 B：结果解读
- 一句话总结 + 关键数值引用 + 后续建议

### 🔒 C：投资建议前
- 声明"技术分析仅供参考，不构成投资建议"

---

## 股票代码

| 市场 | 格式 | 示例 |
|------|------|------|
| 沪市 | `sh` + 6位 | `sh600519`(茅台)、`sh000001`(上证指数)、`sh510500`(中证500ETF) |
| 深市 | `sz` + 6位 | `sz000858`(五粮液)、`sz399006`(创业板指) |

> 不知道代码？→ `python3 bin/quant.py search 茅台`

---

## 核心命令

### analyze — 综合分析（推荐入口）

行情 + 指标 + 形态 + 策略信号 + 回测，一次出完整报告。

```bash
python3 bin/quant.py analyze sh600519                        # 默认日线
python3 bin/quant.py analyze sh600519 --period 1w --count 500  # 周线500根
python3 bin/quant.py analyze sh600519 --html                  # 生成HTML图表
```

**解读速查**：

| 看到 | 意味着 | 建议 |
|------|--------|------|
| MA5偏离>2% | 短期涨太快 | 注意回调 |
| MACD金叉 | 中期动能向上 | 偏多 |
| RSI>70 | 超买 | 不宜追高 |
| ensemble跑赢buy_hold | 策略有超额收益 | 可参考信号 |
| 最大回撤>15% | 波动大 | 需设止损 |

### compare — 多股对比

```bash
python3 bin/quant.py compare sh600519,sz000858,sh601212      # 自动显示实时行情
python3 bin/quant.py compare sh000001,sz399001,sz399006 --period 1w
```

输出：各股指标并排 + 综合评分排名 + 实时价格。评分最高 = 技术面最强。

### backtest — 策略回测

```bash
python3 bin/quant.py backtest sh510500 --strategy ensemble    # 多策略共振
python3 bin/quant.py backtest sh600519 --strategy macd --html # 含HTML图表
python3 bin/quant.py backtest sh600519 --strategy rsi --capital 200000 --stop-loss 0.05
```

| 策略 | 逻辑 | 适用场景 |
|------|------|---------|
| `buy_hold` | 买入持有（基准） | 对比基准 |
| `ma_cross` | MA5/MA20金叉死叉 | 趋势行情 |
| `macd` | DIF/DEA交叉 | 中期趋势 |
| `rsi` | RSI超买超卖 | 震荡行情 |
| `boll` | 布林带轨道反弹 | 区间震荡 |
| `kdj` | KDJ金叉死叉 | 短线交易 |
| `ensemble` | **多策略共振（推荐）** | 过滤假信号 |

**关键指标**：总收益率 vs 基准、最大回撤<15%较健康、夏普>1较好>2优秀、胜率>50%正期望。

### scan — 市场扫描

```bash
python3 bin/quant.py scan --strategy macd
python3 bin/quant.py scan --strategy ma_cross --min-volume 1000000
```

输出按信号排序，金叉=潜在买入机会。结合RSI过滤超买（>70不追），成交量<100万流动性差。

### indicators — 技术指标

```bash
python3 bin/quant.py indicators sh600519 --indicators ma5,ma10,ma20,macd,rsi
python3 bin/quant.py indicators sh600519 --indicators boll,kdj,cci,wr,atr,bias,obv
```

多指标交叉验证更可靠（如MACD金叉+RSI中性=较安全的买入信号）。

### pattern — 形态识别

```bash
python3 bin/quant.py pattern sh600519                            # 全部形态
python3 bin/quant.py pattern sh600519 --pattern w-bottom,cup-handle  # 指定形态
```

| 形态 | 信号 |
|------|------|
| W底(`w-bottom`) | 底部反转 |
| V型反转(`v-reversal`) | 底部反转 |
| 杯柄(`cup-handle`) | 突破买入 |
| 三重底(`triple-bottom`) | 底部确认 |
| 回踩买入(`dip-buy`) | 顺势买入 |

"已确认"比"形成中"更可靠。深度越大，后续反弹空间通常越大。

### fund — 资金面分析

```bash
python3 bin/quant.py fund sh600519
```

主力净流入=机构在买（偏多）。连续3日以上主力流入=资金面趋势确认。

### data — 原始行情

```bash
python3 bin/quant.py data sh600519 --count 30               # 日线
python3 bin/quant.py data sh600519 --period 15m --count 50   # 15分钟线
```

---

## 新增命令

### realtime — 实时行情

腾讯/东方财富秒级数据，无需akshare。

```bash
python3 bin/quant.py realtime sh600519,sz000858,sh601212
python3 bin/quant.py realtime sh600519 --source tencent
```

```
📡 实时行情  数据源: auto
  🔴 贵州茅台(SH600519)  1332.95  -0.69%  高:1339.28 低:1327.11 昨:1342.17
  🔴 五 粮 液(SZ000858)  86.87  -2.38%  高:88.08 低:86.62 昨:88.99
```

涨🟢/跌🔴标识，含最高价/最低价/昨收。

### search — 股票搜索

```bash
python3 bin/quant.py search 白银
python3 bin/quant.py search 宁德时代
```

```
🔍 搜索: 白银
  SZBK1616     白银
  共找到 1 条结果
```

### diagnose — 综合诊断

技术面 + 资金面 + 形态，多维度评分。

```bash
python3 bin/quant.py diagnose sh600519
```

```
🏥 股票综合诊断: sh600519
  技术面得分: -3/8
  形态: w-bottom(2) v-reversal(1) cup-handle(1)
  综合诊断: 强烈看空 🔴🔴🔴 (技术-3 + 资金+0 = -3)
```

### macro — 宏观数据

```bash
python3 bin/quant.py macro cpi       # CPI
python3 bin/quant.py macro pmi       # PMI
python3 bin/quant.py macro gdp       # GDP
python3 bin/quant.py macro m2        # M2货币供应
python3 bin/quant.py macro lpr       # LPR利率
python3 bin/quant.py macro trade     # 进出口
```

```
📊 宏观数据: 居民消费价格指数 (CPI)
  2026年04月份  全国-同比增长: 1.20  全国-环比增长: 0.30
  2026年03月份  全国-同比增长: 1.00  全国-环比增长: -0.70
```

### hotspot — 市场热点

```bash
python3 bin/quant.py hotspot
python3 bin/quant.py hotspot --top 30
```

⚠️ hotspot 依赖东方财富网络接口，部分网络环境下可能不可用。

### market — 市场情绪面分析

涨停池/跌停池/情绪判断/龙虎榜/板块资金流/北向资金/融资融券，一站式市场情绪全景。

```bash
python3 bin/quant.py market                      # 默认参数
python3 bin/quant.py market --limit 10 --days 5  # 显示10条，龙虎榜近5日
python3 bin/quant.py market --period 5日          # 板块资金流用5日累计
```

```
🌊 市场情绪面分析
  🔴 涨停池: 54只（利仁科技5连板、蒙娜丽莎6连板）
  🟢 跌停池: 15只（通达股份2连跌停）
  情绪判断: 涨停54只 / 跌停15只 → 🌊 正常
  🐉 龙虎榜: 德明利 +22.1亿、长盈通 +15.0亿
  📋 融资融券: 融资余额 14,408亿
```

**情绪周期速查**：

| 状态 | 涨停数 | 跌停数 | 操作建议 |
|------|--------|--------|---------|
| ❄️ 冰点期 | <30 | >50 | 最好的埋伏时机 |
| 🌡️ 修复期 | 增多 | 减少 | 小仓位试探 |
| 🔥 高潮期 | >100 | <10 | 最危险，准备撤退 |
| 🌊 退潮期 | 减少 | 增多 | 绝不追高 |

### info — 个股深度信息

限售解禁/股东人数变化/十大流通股东/行业PE估值/大宗交易，个股多维度深度分析。

```bash
python3 bin/quant.py info 600519     # 茅台深度信息
python3 bin/quant.py info 000858     # 五粮液深度信息
```

```
📋 个股深度信息: 600519
  📅 限售解禁: 近期无解禁
  👥 股东人数: 2026Q1 243,159户 (减少12,733户 -4.98%) → 筹码集中 🟢
  🏛️ 十大流通股东: 茅台集团54.07%、港中央6.91%(+609万股)
  📊 行业PE: 制造业 加权PE 37.51 / 中位PE 52.00
  🏷️ 大宗交易: 2026-05-15 成交价1332.96 2笔
```

**解读要点**：
- 股东人数减少 → 筹码集中，主力在吸筹（偏多）
- 股东人数增加 → 散户化趋势（偏空）
- 十大股东增减 → 机构/港资是否在加仓
- 行业PE对比 → 个股PE是否高于行业中位

### 东方财富妙想 AI (em-*)

需在 `config.yaml` 设置 `em_api_key`。注册：https://ai.eastmoney.com/mxClaw

```bash
python3 bin/quant.py em-diagnose sh600519                  # AI综合诊断
python3 bin/quant.py em-pick "白酒板块龙头"                 # AI自然语言选股
python3 bin/quant.py em-ask "茅台Q1业绩怎么样"              # AI问答
python3 bin/quant.py em-news 白酒                           # AI资讯
python3 bin/quant.py em-fund sh600519                      # AI基金分析
```

```
🤖 东方财富妙想 AI 诊断
  查询: 分析sh600519

  一、基本面：2026Q1营收539亿(+6.54%)，净利润272亿(+1.47%)
  二、技术面：股价1332.95，下行通道，PE历史百分位17.36%
  三、资金面：主力净流出6.52亿，连续10日DDX为负
  总结：基本面稳健，估值历史低位，短期技术面偏弱
```

```
🤖 东方财富妙想 AI 选股
  条件: 白酒板块龙头  符合条件: 57 只
  |600519|贵州茅台|1332.95|-0.69%|1.67万亿|
  |000858|五 粮 液|86.87|-2.38%|3371.95亿|
  ...
```

### news — 新闻资讯

东财7x24快讯 + 财联社电报 + 东财搜索，实时掌握市场动态。

```bash
python3 bin/quant.py news                    # 快讯列表 (东财7x24+财联社)
python3 bin/quant.py news 茅台                # 搜索关键词
python3 bin/quant.py news --top 10           # 显示10条
```

```
📰 新闻资讯
  1. 【水利部针对赣鄂湘粤桂黔琼七省区启动洪水防御Ⅳ级应急响应】
     2026-05-19 13:42  [财联社]
  2. 【三星电子股价转涨，抹去早盘5.3%的跌幅】
     2026-05-19 13:41  [财联社]
```

### cache — 缓存管理

```bash
python3 bin/quant.py cache stats    # 查看缓存
python3 bin/quant.py cache clear    # 清理缓存
```

### list — 可用资源

```bash
python3 bin/quant.py list
```

---

## 行动映射

| 看到什么 | 意味着 | 建议 |
|---------|--------|------|
| MACD金叉 + RSI<70 + 多头排列 | 技术面偏多 | 可关注，逢低布局 |
| MACD死叉 + RSI>70 + 空头排列 | 技术面偏空 | 减仓观望 |
| MA5偏离>3% | 短期涨太快 | 不宜追高 |
| ensemble夏普>1.5且跑赢基准 | 策略有效 | 可参考信号 |
| 最大回撤>20% | 波动大 | 严格止损 |
| compare评分差>20分 | 强弱分明 | 关注最强 |

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
| `--html` | 生成HTML图表 | — |
| `--json` | 输出JSON格式 | — |
| `--source` | 数据源(tencent/eastmoney) | auto |

---

## 工作流模板

### 场景A：分析一只股票
```
用户："茅台技术面怎么样"
→ 🔒 A：确认 sh600519
→ python3 bin/quant.py analyze sh600519
→ 🔒 B：一句话总结 + 关键数值 + 后续建议
→ 🔒 C：如涉及买卖，声明免责
```

### 场景B：选股对比
```
用户："茅台五粮液泸州老窖哪个强"
→ 🔒 A：确认代码
→ python3 bin/quant.py compare sh600519,sz000858,sh601212
→ 🔒 B：排名 + 对比表 + 一句话结论
```

### 场景C：策略验证
```
用户："ensemble回测中证500"
→ python3 bin/quant.py backtest sh510500 --strategy ensemble
→ 🔒 B：收益率/回撤/夏普 vs buy_hold
→ 🔒 C：声明回测不代表未来
```

### 场景D：AI诊断
```
用户："帮我全面分析一下茅台"
→ python3 bin/quant.py em-diagnose sh600519  (AI基本面+技术面+资金面)
→ python3 bin/quant.py analyze sh600519      (本地技术指标验证)
→ 🔒 B：综合AI报告+本地数据，给出结论
```

### 场景E：复合需求
```
用户："茅台和五粮液哪个强，顺便看看MACD回测"
→ Step 1: compare sh600519,sz000858
→ Step 2: backtest sh600519 --strategy macd
→ Step 3: backtest sz000858 --strategy macd
→ 🔒 B：综合结论
```

---

## 异常处理

| 场景 | 处理 |
|------|------|
| 依赖未安装 | `pip install akshare numpy pandas requests` |
| 代码格式错 | 提示 `sh`/`sz` + 6位数字 |
| 数据不可用 | 换股票或稍后重试 |
| 网络超时 | 检查连接后重试 |
| akshare限流 | 批量分析加2-3秒间隔，429错误等30秒重试 |
| 股票停牌 | 提示"已停牌，数据可能不完整" |
| 非交易时段 | 数据截至上一交易日 |
| 股票退市/不存在 | 提示"未找到数据"，检查代码 |
| 数据不足 | 自动降级到日线，提示切换 |
| em-api错误 | 自动降级到 em-ask 端点 |

---

## 项目结构

```
a-stock-data-quant/
├── bin/
│   ├── quant.py              # CLI 主入口
│   └── stock_full.py         # 综合分析脚本
├── lib/
│   ├── akshare_data.py       # akshare 数据层 (含降级链)
│   ├── ashare.py             # 行情数据获取 (含mootdx/百度降级)
│   ├── backtest.py           # 回测引擎
│   ├── chart.py              # ECharts HTML 图表
│   ├── data_cache.py         # CSV 数据缓存
│   ├── em_api.py             # 东方财富妙想 AI 接口
│   ├── fallback.py           # 多数据源降级引擎
│   ├── mytt.py               # 技术指标库（MyTT）
│   ├── patterns.py           # 形态识别
│   ├── realtime_data.py      # 实时行情 (腾讯/东方财富/mootdx)
│   ├── settings.py           # 配置管理
│   ├── sources_baidu.py      # 百度财经 API (K线/资金流/概念)
│   ├── sources_datacenter.py # 东财数据中心 (龙虎榜/融资/大宗/股东/解禁)
│   ├── sources_hexin.py      # 同花顺北向资金
│   ├── sources_mootdx.py     # 通达信 TCP 7709 (实时/K线)
│   ├── sources_news.py       # 新闻聚合 (东财7x24/财联社/搜索)
│   └── strategies.py         # 策略模块
├── config.yaml               # 配置文件（em_api_key等）
├── requirements.txt          # Python 依赖
└── LICENSE                   # MIT
```

---

## 数据流

```
用户输入 → 意图路由 → quant.py CLI
  ├─ analyze/compare/backtest/scan/indicators/pattern/fund/diagnose
  │   → akshare_data.py → mytt.py (指标) → strategies.py (信号)
  │   → [降级] → sources_baidu.py / sources_datacenter.py / sources_hexin.py
  │   → backtest.py (回测) → chart.py (HTML) → output
  ├─ realtime/search
  │   → realtime_data.py (腾讯→东方财富→mootdx) → output
  ├─ news (新闻资讯)
  │   → sources_news.py (东财7x24/财联社/东财搜索) → output
  ├─ market (市场情绪面)
  │   → akshare_data.py (涨停池/跌停池/龙虎榜/北向/融资融券) → output
  ├─ info (个股深度)
  │   → akshare_data.py (限售解禁/股东人数/十大股东/行业PE/大宗交易) → output
  ├─ em-diagnose/em-pick/em-ask/em-news/em-fund
  │   → em_api.py (东方财富妙想AI) → output
  └─ macro/hotspot/cache/list
      → akshare_data.py / settings.py / data_cache.py → output
```

---

## License

MIT
