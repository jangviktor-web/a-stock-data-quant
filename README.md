# a-stock-data-quant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-orange?logo=anthropic)](https://claude.ai/settings/plugins/submit)
[![ClawHub](https://img.shields.io/badge/ClawHub-Published-blue?logo=datacamp)](https://clawhub.ai)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green?logo=python)](https://python.org)
[![A-Share](https://img.shields.io/badge/A股-量化分析-red)](https://github.com/jangviktor-web/a-stock-data-quant)

A股量化分析工具箱 — 技术指标 · 形态识别 · 策略回测 · 实时行情 · 多数据源备份 · AI金融分析

> 版本: `v3.2.0` | 基于 [akshare](https://github.com/akfamily/akshare) + [MyTT](https://github.com/mpquant/MyTT) 构建
>
> 数据源: akshare (主) + 百度财经 + 通达信(mootdx) + 东财数据中心 + 同花顺 + 腾讯 + 东方财富
>
> AI能力: 东方财富妙想 (免费) + 东财/财联社新闻聚合
>
> 平台: [ClawHub](https://clawhub.ai) · [Claude Code](https://claude.ai) · [CherryStudio](https://cherry-ai.com) · [GitHub](https://github.com/jangviktor-web/a-stock-data-quant)

---

## 特性亮点

### 多数据源自动降级

当主数据源 (akshare) 失效时，自动切换到备用源，确保分析不中断：

```
akshare 失败 → 百度财经 / 通达信 / 东财数据中心 / 同花顺
实时行情: 腾讯 → 东方财富 → mootdx (三级降级)
K线数据: 新浪 → 腾讯 → mootdx → 百度 (四级降级)
```

降级过程对用户透明，stderr 输出 `[降级]` 提示，不影响正常输出。

### 东方财富妙想 AI

免费使用，基于东方财富专业数据库，支持：
- **AI 诊断**: 基本面+技术面+资金面+估值综合分析
- **AI 选股**: 自然语言条件选股（"白酒板块龙头"）
- **AI 问答**: 任意金融问题
- **AI 资讯**: 实时财经新闻搜索
- **AI 基金**: 基金诊断+持仓分析

### 20+ 技术指标 + 6 种策略

MA/EMA/MACD/RSI/BOLL/KDJ/CCI/ATR/OBV/WR/BIAS/DMI 等 20+ 指标，
支持 buy_hold/ma_cross/macd/rsi/boll/kdj/ensemble 7 种回测策略。

---

## 安装方式

### 方式一：Claude Code 插件市场（推荐）

```bash
# 在 Claude Code CLI 中搜索并安装
/install-plugin a-stock-data-quant
```

或手动安装：

```bash
# 克隆仓库到 Claude Code skills 目录
cd ~/.claude/skills
git clone https://github.com/jangviktor-web/a-stock-data-quant.git
```

### 方式二：ClawHub / OpenClaw

```bash
# 通过 ClawHub CLI 安装
clawhub package install a-stock-data-quant
```

或搜索浏览：

```bash
clawhub search stock
# → a-stock-data-quant: A股量化分析工具箱
```

在线浏览：[clawhub.ai](https://clawhub.ai) 搜索 `a-stock-data-quant`

### 方式三：CherryStudio 技能

1. 打开 CherryStudio → Skills
2. 搜索 `a-stock-data-quant`
3. 点击安装

或手动克隆到 CherryStudio skills 目录：

```bash
cd "C:\Users\<用户名>\AppData\Roaming\CherryStudio\Data\Skills"
git clone https://github.com/jangviktor-web/a-stock-data-quant.git
```

### 方式四：直接克隆（独立使用）

```bash
git clone https://github.com/jangviktor-web/a-stock-data-quant.git
cd a-stock-data-quant
pip install -r requirements.txt
python bin/quant.py list
```

---

## 快速开始

```bash
# 安装依赖
pip install akshare numpy pandas requests mootdx

# 综合分析（推荐入口）
python bin/quant.py analyze sh600519

# 多股对比
python bin/quant.py compare sh600519,sz000858,sh601212

# 实时行情
python bin/quant.py realtime sh600519,sz000858

# AI 诊断
python bin/quant.py em-diagnose sh600519

# 新闻资讯
python bin/quant.py news

# 查看所有命令
python bin/quant.py list
```

> Windows 环境用 `python` 代替 `python3`，需要 `PYTHONIOENCODING=utf-8`

---

## 命令一览

### 核心分析

| 命令 | 功能 | 说明 |
|------|------|------|
| `analyze` | 综合分析 | 行情+指标+形态+策略信号+回测，一次出完整报告 |
| `compare` | 多股对比 | 并排对比多只股票技术面，内置实时行情和综合评分 |
| `backtest` | 策略回测 | 7种策略回测，支持止损/资金量/HTML图表输出 |
| `scan` | 市场扫描 | 全市场板块扫描，按策略信号排序 |
| `indicators` | 技术指标 | MA/MACD/RSI/KDJ/BOLL/CCI/ATR/OBV 等 20+ 指标 |
| `pattern` | 形态识别 | W底、V型反转、杯柄、三重底、回踩买入、Zigzag |
| `fund` | 资金面 | 主力资金流向、融资融券、大中小单分析 |
| `diagnose` | 综合诊断 | 技术面+资金面+形态多维度评分 |

### 数据查询

| 命令 | 功能 | 说明 |
|------|------|------|
| `realtime` | 实时行情 | 腾讯/东方财富/mootdx 秒级行情，三级降级 |
| `search` | 股票搜索 | 关键词搜索股票代码 |
| `data` | 原始行情 | K线数据，支持多周期 (1m~1M) |
| `market` | 市场情绪面 | 涨停池/跌停池/龙虎榜/北向资金/融资融券 |
| `info` | 个股深度 | 限售解禁/股东人数/十大股东/行业PE/大宗交易 |
| `macro` | 宏观数据 | CPI/PPI/GDP/PMI/M2/LPR/进出口 |
| `hotspot` | 市场热点 | 人气榜+概念板块+行业板块涨跌 |
| `news` | 新闻资讯 | 东财7x24快讯+财联社电报+东财搜索 |

### AI 能力 (东方财富妙想)

| 命令 | 功能 | 说明 |
|------|------|------|
| `em-diagnose` | AI 诊断 | 基本面+技术面+资金面+估值综合分析 |
| `em-pick` | AI 选股 | 自然语言条件选股 |
| `em-ask` | AI 问答 | 任意金融问题 |
| `em-news` | AI 资讯 | 实时财经新闻搜索 |
| `em-fund` | AI 基金 | 基金诊断+持仓分析 |

### 辅助工具

| 命令 | 功能 | 说明 |
|------|------|------|
| `cache` | 缓存管理 | 查看/清理数据缓存 |
| `list` | 资源列表 | 查看所有可用指标/策略/形态 |

---

## 详细使用指南

### analyze — 综合分析

一次出完整报告：行情概览 + 技术指标 + 形态识别 + 策略信号 + 策略回测。

```bash
python bin/quant.py analyze sh600519                        # 默认日线
python bin/quant.py analyze sh600519 --period 1w --count 500  # 周线500根
python bin/quant.py analyze sh510500 --capital 200000 --stop-loss 0.05
python bin/quant.py analyze sh600519 --html                  # 生成HTML图表
```

输出包含：
- **行情概览**: 最新价、涨跌幅、区间高低点、均价、成交量
- **技术指标**: MA5/10/20/60、MACD、RSI、KDJ、BOLL、ATR
- **形态识别**: W底、V型反转、杯柄、三重底、回踩买入、Zigzag 转折点
- **策略信号**: 7种策略的最新买卖信号和共振情况
- **策略回测**: 各策略收益率、年化、最大回撤、夏普比率、胜率
- **综合判断**: 多空评分和建议

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
python bin/quant.py compare sh600519,sz000858,sh601212
python bin/quant.py compare sh000001,sz399001,sz399006 --period 1w
```

输出各股指标并排对比 + 综合评分排名 + 实时价格。评分最高 = 技术面最强。

### backtest — 策略回测

```bash
python bin/quant.py backtest sh510500 --strategy ensemble    # 多策略共振（推荐）
python bin/quant.py backtest sh600519 --strategy macd --html # 含HTML图表
python bin/quant.py backtest sh600519 --strategy rsi --capital 200000 --stop-loss 0.05
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

### market — 市场情绪面

涨停池/跌停池/情绪判断/龙虎榜/板块资金流/北向资金/融资融券，一站式市场情绪全景。

```bash
python bin/quant.py market                      # 默认参数
python bin/quant.py market --limit 10 --days 5  # 显示10条，龙虎榜近5日
```

**情绪周期速查**：

| 状态 | 涨停数 | 跌停数 | 操作建议 |
|------|--------|--------|---------|
| 冰点期 | <30 | >50 | 最好的埋伏时机 |
| 修复期 | 增多 | 减少 | 小仓位试探 |
| 高潮期 | >100 | <10 | 最危险，准备撤退 |
| 退潮期 | 减少 | 增多 | 绝不追高 |

### info — 个股深度

```bash
python bin/quant.py info 600519     # 茅台深度信息
python bin/quant.py info 000858     # 五粮液深度信息
```

输出：限售解禁 / 股东人数变化 / 十大流通股东 / 行业PE估值 / 大宗交易。

**解读要点**：
- 股东人数减少 → 筹码集中，主力在吸筹（偏多）
- 股东人数增加 → 散户化趋势（偏空）
- 十大股东增减 → 机构/港资是否在加仓
- 行业PE对比 → 个股PE是否高于行业中位

### news — 新闻资讯

```bash
python bin/quant.py news                    # 快讯列表 (东财7x24+财联社)
python bin/quant.py news 茅台                # 搜索关键词
python bin/quant.py news --top 10           # 显示10条
```

聚合东财7x24快讯 + 财联社电报 + 东财搜索，按时间排序。

### realtime — 实时行情

```bash
python bin/quant.py realtime sh600519,sz000858,sh601212
python bin/quant.py realtime sh600519 --source tencent
```

三级降级：腾讯 → 东方财富 → mootdx，涨🟢跌🔴标识。

### 东方财富妙想 AI

需在 `config.yaml` 设置 `em_api_key`。注册：https://ai.eastmoney.com/mxClaw

```bash
python bin/quant.py em-diagnose sh600519                  # AI综合诊断
python bin/quant.py em-pick "白酒板块龙头"                 # AI自然语言选股
python bin/quant.py em-ask "茅台Q1业绩怎么样"              # AI问答
python bin/quant.py em-news 白酒                           # AI资讯
python bin/quant.py em-fund sh600519                      # AI基金分析
```

---

## 多数据源架构

### 降级链

| 数据类型 | 主数据源 | 备用源 |
|----------|----------|--------|
| 实时行情 | 腾讯 → 东方财富 | mootdx (通达信TCP 7709) |
| 历史K线 | 新浪 → 腾讯 | mootdx → 百度财经 |
| 资金流向 | akshare | 百度分钟级资金流 |
| 龙虎榜 | akshare | 东财数据中心 (datacenter-web) |
| 融资融券 | akshare | 东财数据中心 |
| 限售解禁 | akshare | 东财数据中心 |
| 股东人数 | akshare | 东财数据中心 |
| 大宗交易 | akshare | 东财数据中心 |
| 北向资金 | akshare | 同花顺 (hexin.cn) |
| 概念板块 | akshare | 百度财经 |
| 新闻资讯 | 东财7x24 + 财联社 | — |

### 备用数据源说明

- **mootdx**: 通达信 TCP 7709 协议，无认证无IP限制，适合做备用
- **百度财经**: `finance.pae.baidu.com`，纯HTTP，支持K线/资金流/概念板块
- **东财数据中心**: `datacenter-web.eastmoney.com`，6种报告类型
- **同花顺**: `data.hexin.cn`，北向资金数据

### 降级机制

使用 `@_with_fallback` 装饰器包装 akshare 函数：

```python
@_with_fallback(_ak_fund_flow, ('百度', _baidu_fund_flow))
def get_fund_flow(code, market=None):
    ...
```

- 主数据源成功 → 直接返回
- 主数据源失败 → 自动尝试备用源
- 全部失败 → 返回空结果，stderr 输出错误信息
- 降级提示输出到 stderr，不污染 stdout JSON 输出

---

## 配置管理

### config.yaml

```yaml
# 东方财富妙想 AI (免费)
em_api_key: "em_xxxxxxxxxxxxxxxx"

# 回测参数
capital: 100000        # 初始资金
commission: 0.001      # 手续费率
slippage: 0.001        # 滑点

# 数据缓存
cache:
  enabled: true
  ttl_hours: 4         # 缓存有效期（小时）
  directory: cache

# HTML 输出
html:
  directory: html
```

### 数据缓存

```bash
python bin/quant.py cache stats         # 查看缓存统计
python bin/quant.py cache clear         # 清理过期缓存
python bin/quant.py cache clear --older-than 7  # 清理7天前的缓存
```

---

## 可用技术指标

```
MA    简单移动平均      EMA   指数移动平均
MACD  指数平滑异同      RSI   相对强弱指标
BOLL  布林带           KDJ   随机指标
CCI   商品通道指数      WR    威廉指标
ATR   真实波动幅度      BIAS  乖离率
OBV   能量潮           DMI   动向指标
TRIX  三重指数平滑      VR    成交量比率
EMV   简易波动指标      BBI   多空指标
MFI   资金流量指标      ASI   累积摆动指标
PSY   心理线           SAR   抛物线指标
```

---

## 形态识别

| 形态 | 参数 | 信号 |
|------|------|------|
| W底 | `w-bottom` | 底部反转 |
| V型反转 | `v-reversal` | 底部反转 |
| 杯柄 | `cup-handle` | 突破买入 |
| 三重底 | `triple-bottom` | 底部确认 |
| 回踩买入 | `dip-buy` | 顺势买入 |
| Zigzag | `zigzag` | 趋势转折点 |

"已确认"比"形成中"更可靠。深度越大，后续反弹空间通常越大。

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
| `--source` | 数据源(tencent/eastmoney/mootdx) | auto |

## K线周期

| 周期 | 代码 | 说明 |
|------|------|------|
| 日线 | `1d` | 默认，适合中长线分析 |
| 周线 | `1w` | 中期趋势 |
| 月线 | `1M` | 长期趋势 |
| 1分钟 | `1m` | 超短线 |
| 5分钟 | `5m` | 短线 |
| 15分钟 | `15m` | 日内波段 |
| 30分钟 | `30m` | 日内波段 |
| 60分钟 | `60m` | 日内波段 |

## 股票代码格式

| 市场 | 格式 | 示例 |
|------|------|------|
| 沪市 | `sh` + 6位 | `sh600519`(茅台)、`sh000001`(上证指数)、`sh510500`(中证500ETF) |
| 深市 | `sz` + 6位 | `sz000858`(五粮液)、`sz399006`(创业板指) |

不知道代码？→ `python bin/quant.py search 茅台`

---

## 项目结构

```
a-stock-data-quant/
├── bin/
│   ├── quant.py              # CLI 主入口 (2000+ 行)
│   └── stock_full.py         # 综合分析脚本
├── lib/
│   ├── akshare_data.py       # akshare 数据层 + 降级链
│   ├── ashare.py             # 行情数据获取 (含mootdx/百度降级)
│   ├── backtest.py           # 回测引擎
│   ├── chart.py              # ECharts HTML 图表生成
│   ├── data_cache.py         # CSV 数据缓存
│   ├── em_api.py             # 东方财富妙想 AI 接口
│   ├── fallback.py           # 多数据源降级引擎
│   ├── mytt.py               # 技术指标库 (MyTT)
│   ├── patterns.py           # 形态识别
│   ├── realtime_data.py      # 实时行情 (腾讯/东方财富/mootdx)
│   ├── settings.py           # 配置管理
│   ├── sources_baidu.py      # 百度财经 API (K线/资金流/概念)
│   ├── sources_datacenter.py # 东财数据中心 (龙虎榜/融资/大宗/股东/解禁)
│   ├── sources_hexin.py      # 同花顺北向资金
│   ├── sources_mootdx.py     # 通达信 TCP 7709 (实时/K线)
│   ├── sources_news.py       # 新闻聚合 (东财7x24/财联社/搜索)
│   └── strategies.py         # 策略模块
├── config.yaml               # 配置文件
├── SKILL.md                  # Claude Code skill 文档
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
  ├─ news
  │   → sources_news.py (东财7x24/财联社/东财搜索) → output
  ├─ market
  │   → akshare_data.py (涨停池/跌停池/龙虎榜/北向/融资融券) → output
  ├─ info
  │   → akshare_data.py (限售解禁/股东人数/十大股东/行业PE/大宗交易) → output
  ├─ em-diagnose/em-pick/em-ask/em-news/em-fund
  │   → em_api.py (东方财富妙想AI) → output
  └─ macro/hotspot/cache/list
      → akshare_data.py / settings.py / data_cache.py → output
```

---

## 更新日志

### v3.2.0 (2026-05-19)

**多数据源备份系统 + 新闻资讯**

新增功能：
- **多数据源自动降级**: 主数据源失效时自动切换备用源，确保分析不中断
  - 实时行情: 腾讯 → 东方财富 → mootdx (三级降级)
  - K线数据: 新浪 → 腾讯 → mootdx → 百度 (四级降级)
  - 资金流向: akshare → 百度分钟级
  - 龙虎榜/融资融券/限售解禁/股东人数/大宗交易: akshare → 东财数据中心
  - 北向资金: akshare → 同花顺
  - 概念板块: akshare → 百度财经
- **新闻资讯命令** (`news`): 东财7x24快讯 + 财联社电报 + 东财搜索
- **市场情绪面命令** (`market`): 涨停池/跌停池/龙虎榜/北向资金/融资融券一站式分析
- **个股深度命令** (`info`): 限售解禁/股东人数/十大股东/行业PE/大宗交易

新增文件：
- `lib/fallback.py` — 降级引擎 `try_sources()` + `@_with_fallback` 装饰器
- `lib/sources_baidu.py` — 百度财经 K线/资金流/概念板块
- `lib/sources_mootdx.py` — 通达信 TCP 7709 实时行情+K线
- `lib/sources_datacenter.py` — 东财数据中心 6类报告
- `lib/sources_hexin.py` — 同花顺北向资金
- `lib/sources_news.py` — 东财7x24+财联社+东财搜索

改进：
- `akshare_data.py`: 12个函数加 `@_with_fallback` 降级链
- `realtime_data.py`: 加 mootdx 第三级降级
- `ashare.py`: K线加 mootdx + 百度降级
- 修复 akshare API 签名变更导致的多个函数失效
- 修复涨停池/跌停池默认日期错误
- 修复龙虎榜金额单位显示错误
- 修复股东人数/限售解禁列名不匹配

### v3.1.0 (2026-05-15)

**东方财富妙想 AI 集成 + 实时行情**

新增功能：
- **东方财富妙想 AI**: 5个AI命令 (em-diagnose/em-pick/em-ask/em-news/em-fund)
- **实时行情** (`realtime`): 腾讯/东方财富秒级行情
- **股票搜索** (`search`): 关键词搜索股票代码
- **HTML 图表**: ECharts 交互式图表，支持缩放/拖拽/数据点悬停
- **数据缓存**: CSV 缓存，支持 TTL 过期
- **配置管理**: `config.yaml` 集中配置

新增文件：
- `lib/em_api.py` — 东方财富妙想 AI 接口
- `lib/realtime_data.py` — 腾讯/东方财富实时行情
- `lib/chart.py` — ECharts HTML 图表生成
- `lib/data_cache.py` — CSV 数据缓存
- `lib/settings.py` — 配置管理

### v3.0.0 (2026-05-15)

**综合诊断 + 宏观数据**

新增功能：
- **综合诊断** (`diagnose`): 技术面+资金面+形态多维度评分
- **宏观数据** (`macro`): CPI/PPI/GDP/PMI/M2/LPR/进出口
- **市场热点** (`hotspot`): 人气榜+概念板块+行业板块

### v2.0.0 (2026-05-13)

**核心分析功能**

新增功能：
- **综合分析** (`analyze`): 行情+指标+形态+策略信号+回测
- **多股对比** (`compare`): 并排对比多只股票技术面
- **策略回测** (`backtest`): 7种策略回测
- **市场扫描** (`scan`): 全市场板块扫描
- **形态识别** (`pattern`): W底/V型反转/杯柄/三重底/回踩买入

### v1.0.0 (2026-05-12)

**初始版本**

- 基于 akshare + MyTT + Ashare 构建
- 支持 20+ 技术指标
- 支持资金流向分析

---

## 致谢

- [Ashare](https://github.com/mpquant/Ashare) — 行情数据接口
- [akshare](https://github.com/akfamily/akshare) — A股数据
- [MyTT](https://github.com/mpquant/MyTT) — 技术指标库
- [mootdx](https://github.com/mootdx/mootdx) — 通达信行情接口
- [东方财富妙想](https://ai-oss.eastmoney.com) — AI金融分析接口
- [stock-api](https://github.com/zhangxiangliang/stock-api) — 实时行情协议参考
- [a-stock-data](https://github.com/simonlin1212/a-stock-data) — 备用数据源 API 参考

## License

MIT
