---
name: a-stock-data-quant
agent_created: true
description: 股市/股票/行情/股价/涨跌/大盘/指数/个股分析——金融/投资/股票/基金/ETF/板块/指数/宏观/外汇/大宗商品/财报/估值/持仓/交易/仓位/量化/因子/回测/选股/期权/衍生品/投行建模/技术指标/行情监控/预警——内置研究框架（红线/检索策略/数据口径/50+方法论 references/scripts）、A股量化数据引擎（12层数据源·bin/quant.py）、多市场数据层（港股/期货/期权/宏观/公告事件·bin/cn/*.py）与 8 个研报写作工作流（读年报/可比公司/深度报告/业绩快评/调研纪要/行业研究/晨会纪要/研报摘要·references/research-workflows/）。金融场景总入口，命中任一上述领域即优先加载；并集成同花顺金融数据服务（hithink-finance，iFinD 级 A股/指数/板块/公募基金/特色数据权威源，接入层见 references/hithink-finance/）。
when_to_use: 只要用户提到 股票、股市、行情、股价、最新价、涨跌、涨停、跌停、大盘、指数、K线、ETF、基金、期货、期权、港股、美股、板块、资金、主力、北向、龙虎榜、财报、业绩、估值、市盈率、市净率、PE/PB、买入、卖出、仓位、定投、选股、量化、回测 等任一关键词，即自动调用本 skill。金融场景必须使用本 skill，包括但不限于：个股/标的研究、报价/财报/估值、买卖/仓位操作建议、股票代码（A股6位/港股5位/美股ticker）、分析方法论/建模/策略、投行文书；以及需要实际获取 A股/港股数据——实时行情/K线、研报(东财+巨潮)、信号(热点/北向/龙虎榜/解禁/行业)、资金面(融资融券/大宗/股东户数/资金流)、新闻、F10财务三表、公告、互动易、筹码分布、板块资金流、市场温度、估值分位、ETF排行、回测、综合诊断；港股行情、CN期货主连、CN期权(ETF+CFFEX)、CN宏观(CPI/PPI/GDP/M2/PMI/社融/LPR/SHIBOR/国债收益率)、业绩预告/快报/披露计划、解禁/股东户数/增减持/回购/分红/新股/IPO日历、ETF/可转债列表与行情；以及研报写作（读年报/可比公司分析/深度报告/业绩快评/调研纪要/行业研究/晨会纪要/研报摘要）；公共信息源不可用时，可经用户确认启用同花顺金融数据服务（hithink-finance）作为备用源——A股权威行情/复权K线/财报/估值/集合竞价/指数板块/公募基金/特色数据（涨停跌停/异动/热榜/龙虎榜）/全市场 Parquet 导出（API Key 获取：fuyao.aicubes.cn，需用户同意并发送给 Agent 后方可启用）。
version: 3.6.0
license: MIT
keywords: ["stock","股市","股票","行情","股价","最新价","涨跌","涨停","跌停","大盘","指数","K线","个股","板块","龙头","资金","主力","港股","美股","基金","ETF","期货","期权","财报","业绩","估值","市盈率","市净率","PE","PB","买入","卖出","仓位","定投","理财","选股","量化","回测","股票分析","股票代码","quant","a-share","backtest","technical-analysis","finance","akshare","trading","investment","china-stock","stock-market","stock-price","market-quote","share-price","equities","MACD","RSI","KDJ","real-time-quotes","AI-analysis","valuation","dcf","options","macro","fund-flow","research","stock-decision","buy-sell-signal","should-i-buy","etf-decision","should-i-buy-etf","etf-signal","fund","hk","futures","forecast","lhb","dragon-tiger","unlock","insider-trade","buyback","dividend","ipo","annual-report","deep-dive","earnings-review","field-research","industry-study","morning-brief","research-digest","comparable","peers","北向","解禁","增减持","回购","分红","新股","业绩预告","读年报","深度报告","业绩快评","调研纪要","行业研究","晨会纪要","研报摘要","可比公司","同花顺","hithink","hithink-finance","iFinD","集合竞价","公募基金","异动","热榜","龙虎榜","fuyao","复权因子","全市场导出"]
allowed-tools: [Bash, Read, Glob, Grep, Write, Edit, WebFetch, WebSearch]
---

# a-stock-data-quant — 金融研究框架 + A股量化数据引擎 + 港股/期货/期权/宏观数据层 + 研报工作流（整合版）

> 本 skill 为「研究框架 + A股量化数据引擎 + 多市场数据层 + 研报写作工作流」的一体化整合版。

## 路由总览
- **研究框架 / 红线 / 检索策略 / 数据口径 / 时间口径 / 场景方法论 references / 投行 scripts** → 见下方「整合框架」章节。
- **A股实际取数 / 量化指标 / 回测 / 综合诊断** → 见文末「A股量化数据引擎（a-stock-data-quant）」章节；完整内嵌实现见 `references/a-stock-full.md`，或运行 `bin/quant.py`。
- **港股 / 期货 / 期权 / 宏观 / A股公告事件（业绩预告/解禁/股东/增减持/回购/分红/新股/IPO）** → 见「能力路由矩阵」章节，运行 `bin/cn/*.py`。
- **研报写作工作流（读年报/可比公司/深度报告/业绩快评/调研纪要/行业研究/晨会纪要/研报摘要）** → 见「研报工作流」章节，工作流细节在 `references/research-workflows/<slug>/`。

> 以下「整合框架」章节为本 skill 的红线 / 检索策略 / 数据口径 / 时间口径 / 场景方法论 references 索引 / 投行 scripts 约定；文末补充 A股量化数据引擎。

## 能力路由矩阵（数据域 → 首选实现 → 备用）

| 数据域 | 首选 | 备用 / 说明 |
|---|---|---|
| A股实时行情 / K线 | `bin/quant.py realtime\|analyze`（腾讯多源降级） | `bin/cn/equity.py quote\|history`（新浪批量，支持港股） |
| **港股** 行情 / K线 | `bin/cn/equity.py quote 00700\|history`（东财116.*） | —（wb 引擎为 A股向，港股走 cn） |
| **期货**（18 主连） | `bin/cn/futures.py quote cu,au\|list` | — |
| **期权**（ETF+CFFEX 指数期权） | `bin/cn/options.py underlyings\|chain\|pcr` | — |
| **宏观**（CPI/PPI/GDP/M2/PMI/社融/LPR/SHIBOR/国债收益率） | `bin/cn/macro.py cpi\|lpr\|treasury-yield …` | akshare 深度序列 |
| 北向资金 | `bin/cn/equity.py northbound`（东财 kamt） | ⚠️ wb `sources_hexin` 响应结构已变、视为 deprecated |
| 涨跌停 / 行业 / 题材板块 | `bin/quant.py hot-stocks\|hot-boards` | `bin/cn/equity.py limit-up\|limit-down\|industry\|concept` |
| 龙虎榜 / 大宗交易 | `bin/quant.py capital-flow`（东财 datacenter） | `bin/cn/research.py lhb\|block-trade` |
| **业绩预告 / 快报 / 披露计划** | `bin/cn/research.py forecast\|flash\|report-calendar` | — |
| **解禁 / 股东户数 / 增减持 / 回购 / 分红 / 新股 / IPO** | `bin/cn/research.py unlock\|shareholder-count\|insider-trade\|buyback\|dividend\|ipo-calendar` | — |
| A股三表（IS/BS/CF） | `bin/quant.py fundamentals` | `bin/cn/research.py fundamentals` |
| ETF / 可转债 列表与行情 | `bin/cn/research.py etf-list\|etf-quote\|cb-list\|cb-quote`（无 key） | 有 GF key 时 `bin/quant.py etf-rank` |
| 研报写作（读年报/深度/快评/纪要/行业/晨会/摘要/可比） | `references/research-workflows/` 工作流 | 配合 `bin/quant.py` / `bin/cn/*.py` 取数 |
| **集合竞价** 快照 / 短期基准 | 引擎层不支持 | hithink（**备用·需用户确认启用**）竞价端点 `references/hithink-finance/` |
| **公募基金**（资料 / 经理 / 净值 / 持仓 / 财务 / ETF·LOF 行情） | `bin/cn/research.py etf-*`（仅 ETF 列表 / 行情） | hithink（28 端点最全·**备用·用户确认后启用**） |
| **特色数据**（涨停 / 跌停 / 炸板 / 连板 / 异动 / 热榜 / 龙虎榜） | `bin/quant.py capital-flow`（仅龙虎榜 partial） | hithink（11 端点·**备用·用户确认后启用**） |
| **A股权威复权 K线 / 分红送股因子** | `bin/quant.py analyze`（腾讯 / 新浪，复权口径有限） | hithink（`adjustment-factors`·**备用·用户确认后启用**） |
| **全市场历史行情导出 / 本地建库** | `bin/quant.py` 逐只拉（数千次请求，不推荐） | hithink Market Dumps（Parquet·**备用·用户确认后启用**） |

> **去重原则**：同一数据域只走一条链路（首选）；A股核心以引擎层（实测修复+多源降级）为准；多市场数据层补港股/期货/期权/宏观/公告事件等增量域。**不要两条链路都跑。**

## 研报工作流（引用 `references/research-workflows/`）

以下 8 个研报写作工作流是**纯方法论模板**，用户触发后：先按工作流取数（`bin/quant.py` / `bin/cn/*.py`），再按其章节产出成品报告；`{{占位符}}` 与连接器增强见根级 `CONNECTORS.md`。

| 触发 | 工作流目录 | 产出 |
|---|---|---|
| 读年报 / 年报分析 | `references/research-workflows/annual-report-reader/` | 结构化投资备忘录（财务+风险扫描+分红） |
| 可比公司 / 估值对比 | `.../comparable-analysis/` | 估值倍数矩阵 + 估值区间/隐含股价 |
| 深度报告 / 首次覆盖 | `.../deep-dive-report/` | 券商体例深度研报 |
| 业绩快评 / 业绩点评 | `.../earnings-review/` | 业绩点评（超/低预期判断） |
| 调研纪要 / 纪要整理 | `.../field-research-notes/` | 标准化调研纪要 |
| 行业研究 / 行业报告 | `.../industry-research/` | 行业全景报告 |
| 晨会纪要 / 晨会材料 | `.../morning-briefing/` | 晨会汇报材料 |
| 研报摘要 / 研报对比 | `.../research-digest/` | 研报要点 + 观点分歧矩阵 |

## 触发顺序硬约束
- 必须**先**加载本 skill 的红线与路由规范，任何涉及金融市场数据的请求，**都要**调用数据接口 / 检索工具获取数据；**禁止跳过本 skill 直接裸答或者凭记忆回答。**

## 红线（金融场景一票否决）

- **禁止编造数据**：不虚构数据/事件/公司名/财务数字；数据源缺失时直接说明"当前数据源未覆盖 / 需进一步核实"，不要编一组数据再加"待核实"标签；引用不确定的研报/论文时标"该引用需核实原文"
- **禁止核心概念混淆**：客户 vs 竞争对手、整机厂 vs 零部件厂、净利润 vs 归母净利润、同比 vs 环比、财年 vs 自然年；不确定时用"据我理解"前缀并请用户确认
- **禁止数据自相矛盾**：同一回答内数据与结论必须一致；多组数据先交叉校验；数据源冲突时优先采信高层级来源（交易所、公司公告、年报）并显式标注分歧
- **强制免责声明**：所有包含具体投资建议、操作价位、买卖判断、仓位调整建议的输出，必须在回复末尾附加以下免责声明模板（固定文案，禁止模型自行改写、缩减或省略）：

  > **免责声明**：以上内容基于公开数据和量化分析，仅供参考，不构成投资建议。市场有风险，投资需谨慎。任何投资决策应结合个人风险承受能力、资金状况和投资目标独立判断，必要时咨询持牌专业机构。过往表现不预示未来收益。

## 检索策略
- 金融数据检索统一经 **agentic_search 工具** —— 它**具备自主分析与多步规划能力**，会自行判断查哪些维度、分几步查，返回结论。
- **委派 query 必须是"一句话检索意图"，保留用户原始意图，禁止拆成多维度清单 / 字段列表 / 表格格式要求**。工具 自身具备多步规划与自主检索能力，会自行拆维度、判断查哪些字段、查多深——你拆得越细、要求越"全"，它解锁的检索面越大、越发散、越慢。委派时**只交代两件事**：① 标的 / 主题 / 范围（带代码），② 大方向查什么；其余（查哪些字段、列几列、怎么排序、要不要表格、分几个维度）一律**不写**，也**不要要求工具 写分析 / 结论报告 / 大段表格**——它只需返回结论。字段筛选、表格化、排序、深度分析都是拿回数据后**主 agent 自己的活**（见第 4/7 条），不是委派 query 的内容。
- **不要要求"全面/详细/深入"检索**：委派里禁止出现"请尽可能全面地检索""详细检索""返回结构化分析数据""覆盖以下 N 个方面"这类堆砌词。检索广度与深浅由工具 按问题体量自己定，主 agent 说得越"全""细"它越发散、越慢，反而不利。就给它一句朴素的检索意图即可。
    - 反例（过度拆解，禁止）：用户问"列出场内基金里红利低波和红利自由现金流 ETF"，却委派"请查询 A 股场内 ETF 中红利低波、红利自由现金流两主题的所有相关 ETF，列出基金代码、简称、跟踪指数、管理人、最新规模、近一周/近一月/年初至今涨跌幅、管理费率+托管费率、成立日期，用表格分主题输出……"
    - 正例（一句话）："列出场内（A 股）红利低波、红利自由现金流两个主题的相关 ETF"
    - 反例：用户问"国内有哪些上市公司跟 SpaceX 相关"，却委派"请全面检索 A 股与 SpaceX 有业务关联的公司，覆盖直接供应商 / 产业链相关 / 对标概念 / 最新动态四个维度，列出名称、代码、关联逻辑、近期表现，区分实际业务与概念炒作……"
    - 正例："检索 A 股里与 SpaceX 相关的上市公司"
    - 反例（宽泛研究被拆维度 + 堆"全面"词，禁止）：用户问"银河电子怎么样"，却委派"全面分析 A 股银河电子（002519），需覆盖：1 主营业务 2 财务数据 3 估值 4 股价走势与资金流向 5 研报评级 6 近期公告 7 板块概念，请尽可能全面地检索并返回结构化分析数据"
    - 正例："研究 A 股银河电子（002519）的整体情况"
- 宽泛的"X 怎么样 / 值不值得看"只需一句话点明标的与代码，具体查什么、查多全由工具 自己拆；只有用户问题本身就很具体、只问单一字段时（如"茅台最新 PE"）才如实精确转述。
- 工具无法满足时，用 WebSearch 检索公开信息，明确告知用户数据来源并说明非实时性。

## 数据底线

- **前提显式**：问操作类问题（买/卖/加仓/减仓/换股）时，先列前提（市场环境 + 用户风险偏好 + 资金量/期限），再给"条件 → 操作 → 风险提示"。前提缺失时主动追问而非直接给操作建议
- **检索优先于记忆**：提及具体股票/基金/指数/宏观指标时，先调 agentic_search；如通达信 MCP 可用，按MCP场景说明调用拉数据，禁止纯凭记忆作答；记忆中的数字只能作为合理性 sanity check，不能作为答案
- **禁止硬编码数据**：所有行情、财务、宏观和技术指标必须通过工具动态获取并标注来源和时点，禁止在回答中直接引用训练数据中的历史数值或凭记忆输出数字
- **时效意图与目标周期解析**：用户表达“最新、当前、今天、今年、近期”等时效要求时，先结合运行时日期、市场交易状态、指标发布频率和数据发布时间确定目标周期，不得把当前年份直接等同于最新有效数据周期。用户明确指定历史日期、年份、季度、财年或回测时点时，以用户指定范围为准，不得自动改写为当前周期。

- **查询结果时效校验**：数据返回后核对其统计周期、发布时间和数据截止时间是否满足用户要求：
  1. 数据已覆盖目标周期时，按实际周期使用并标注时点；
  2. 当前周期尚未发布时，使用最近已发布周期，并明确说明数据截止时间；
  3. 返回数据明显早于目标周期时，调整时间参数或更换数据源重新查询；
  4. 仍无法取得满足要求的数据时，明确声明数据缺口和最近可用时点，不得将历史数据表述为当前数据。
- **所有关键数据必须可追溯到来源 + 时间戳**：行情 / 财务 / 宏观 / 研报数字不能裸出；每个关键数字附近都要能追溯到"来源 + 时点"（YYYY-MM-DD 或 YYYYQn），不要只在文末放一个总来源。同一数据块共享相同来源、周期和口径时，可在表头、表尾或图注统一标注，来源或周期不同时，再分别标注。来源可来自 agentic_search / 通达信 MCP / 交易所公告 / 公司年报 / 港交所披露易 / 研报 / WebSearch；WebSearch 兜底时也要标媒体名 + 日期，若生成 HTML，最好把 WebSearch 原文链接做成可点击链接。研报和媒体数据要标清"非一手来源 / 需核实原文"，不要把它们和公司公告同等处理
- **来源标注粒度与数据粒度匹配**：同一表格、图表或数据卡片中的数据共享相同来源、统计周期和口径时，可在表头、表尾或图注统一标注，无需在每个单元格重复。只有不同子项来源、时点或计算口径不同时，才需要分别标注。任何关键结论都应能追溯到对应的数据来源和时点。
- **来源质量分级**：
  - **一手来源**（交易所公告、统计局、公司年报/季报、央行/监管机构）：可直接采信，标注机构名 + 发布日期
  - **非一手来源**（财经媒体、研报引用、第三方数据平台二次引用）：必须标注"需核实原文"，不得与一手来源同等处理。研报引用还需标注研报机构 + 发布时间
- **输出来源规范**：HTML 报告应在数据卡片、图表或表格附近标注来源和数据时点；Markdown 应在关键数据首次出现处标注来源。共享来源的数据可合并标注，避免重复信息影响可读性。

## 使用指南

1. **识别意图**：先分清这是"取数据"（→ 委派 agentic_search 工具）还是"给方法论 / 分析 / 输出"（→ 读对应 reference、跑 scripts）；很多请求两者都要（先取数再分析）
2. **自主执行**：不要让用户挑数据源；数据源在哪、怎么路由由工具 内部决定，主 agent 只管把检索意图讲清楚（委派规范见上方「检索策略」——一句话意图、不指定字段/表格/维度、不要求工具 写分析报告）
3. **错误兜底**：工具 返回缺失或报错时，换个问法再调用，或用通达信 MCP（如可用）/ WebSearch 补
4. **清晰呈现**：用中文表头的可读表格展示返回结果。列举 / 排名 / 对比多个标的时，交付前过三道规整校验：
    - **每个标的必带标准格式代码**：A 股 6 位（600519）、港股 5 位（00700）、美股 ticker（AAPL），逐个标注、无一例外，不要只在第一个标的后给代码
    - **排序 / 分层必须给可量化依据**：给标的排序或分档时，写清排序所依据的具体指标（市占率 / 供应份额 / 营收占比 / 资金流入 / 增速 / 估值分位），不要用"绑定深度""市场地位""重要性"这类笼统词；确实拿不到量化指标时，说明这是定性排序，不要伪装成硬排名
    - **条件校验**：题目限定了范围（市场 A 股 / 港股 / 美股、上市状态、产品类型）时，逐个核对候选标的是否满足，剔除不符的；A 股清单里混入港股或未上市标的是硬错误
5. **按需组合**：复杂请求可多次委派工具 互补（如先让工具 选出股票池，再对池内标的逐只查详情），或在一次委派里把多步需求讲清让工具 自主完成
6. **置信度分层**：高置信度直接断言；中等用"倾向于 / 大概率"；低用"不排除 / 有可能"。不要把所有可能性平铺让用户自选
7. **除非用户指定格式，结果尽可能用 HTML 可视化呈现**：分析、对比、研报型回答尽量产出 HTML 文件（用 `Write` 落地 HTML，对话里把文件路径告诉用户）；简短 Q&A、单数字查询、Yes-No 判断仍用 Markdown。HTML 用浅底深字研报风、首屏结论先行；数据图用 ECharts、关系拓扑图用 SVG/CSS、查阅型用表格。**关键约束：手写的内联 JS / ECharts option 极易括号或引号失配，一处错整页图表全废——HTML 写完交付前必须做一次 JS 语法自检（`node --check` 或等价），报错改到通过再交付。** 复杂图优先套用现成 option 骨架填 data，不要从零手敲嵌套结构。HTML 风格、ECharts 骨架、图表分工与质量细则（图表可切换 / 多取周期消空值 / 双轴量级 / 空值不入图）见 `references/html-report-style.md`，产出 HTML 前先读它。
8. 🔴 **CHECKPOINT · 加载后必须匹配 reference**：进入本 skill 后，必须完成以下三步，**不要只读 SKILL.md 主文件就直接答**——主文件只讲红线和路由，具体方法论（步骤、阈值、避坑）都在对应 reference 里。三步未走完不得输出分析结论。

   **第一步：问题拆解为场景标签**
   把用户问题拆成一个或多个场景标签。复合问题必须拆分（如"结合大盘分析 X 该不该买"→ `market-state` + `stock-deep-research` + `valuation-pricing` + `trade-plan`），禁止用单个宽泛标签覆盖全部需求。

   **第二步：核心方法论加载**
   每个主场景必须加载对应的核心 reference；存在多个主场景时分别加载。核心 reference 加载完成后，根据问题中的具体维度追加补充 reference。Reference 加载遵循“最小充分集合”原则：每个主场景优先选择一个最相关的核心方法论；只有用户需求包含独立分析维度、且当前核心 reference 无法覆盖时，才追加补充 reference。不设置机械固定上限，但禁止为了完成清单无边界加载无关文件。判断依据是方法论是否实际用于分析，而不是读取文件数量。

   问题场景与核心必选 / 条件追加对照：

   | 问题场景 | 核心必选 | 条件追加 | 质量底线 |
   |---|---|---|---|
   | 市场展望 / 大盘 | `market-state` + `macro-transmission` | 主线研判加 `market-mainline`；板块轮动加 `sector-comparison` | 不能只做指数涨跌描述 |
   | 个股全面分析 | `stock-deep-research` + `valuation-pricing` | 按问题加 `business-model` / `quality-growth` / `peer-comparison` / `industry-chain` | "全面"不能只加载个股初探 |
   | 技术指标 / 形态 | `price-action-tools` | 仅突破、VCP、波缩、真假突破时加 `breakout-patterns` | MACD/RSI 查询不强制加载 VCP |
   | 红利 / 分红 / 回购 | `dividend-buyback` | 估值性价比加 `valuation-pricing`；现金质量加 `quality-growth` | 不能以单次股息率代替持续性验证 |
   | 政策 / 题材 / 热点 | `policy-impact` | 市场主线加 `market-mainline`；产业映射加 `industry-chain` | 必须给出政策→行业→公司传导链 |
   | 订单 / 合同负债 / 前瞻指标 | `earnings-preview` + `quality-growth` | 收入模式加 `business-model`；涉及定价兑现才加 `valuation-pricing` | 不能把所有经营前瞻指标机械路由到估值 |

   **第三步：自检（输出前必须通过）**
   - 每个主场景是否都有核心方法论 reference？
   - 数据源是否按路由表选择，且降级原因合理？
   - 用户要求的关键分析维度是否均已覆盖？
   - 方法论是否实际体现在答案中，而不是只完成文件读取？
   - 每个关键数据是否能对应到来源、时点和口径；
     不同来源/周期的子项是否分别标注？
   - 是否包含具体买卖、价位或仓位建议；
     若包含，固定免责声明是否完整位于回复末尾？
   - 若存在缺失，继续补充、重新查询或明确缩小回答范围，
     禁止假装完成全面分析。

   `html-report-style.md` **只负责输出格式，必须在方法论匹配完成后加载，不能替代任何方法论 reference。** 禁止仅加载格式类、工具类或数据源类 reference 就直接输出分析结论。
9. **优先用 scripts/ 现成工具，不要从零重写算法**：`scripts/price-action/` 含 7 个技术分析信号引擎（K 线 / 谐波 / 波浪 / 缠论 / 一目 / SMC / 基础指标），`scripts/quant/` 含 6 个量化策略引擎（配对 / 季节性 / 波动率 / 多因子 / 基本面 / 分钟级），`scripts/ib/` 含 2 个投行 utility（DCF Excel 校验 / 投行材料数字一致性）。涉及技术指标计算 / 量化策略 / DCF 审核等场景时，**先 Read 对应 script 看输入约定，再 Bash 执行**，远比 model 自己重写算法快且不出错。具体工具清单见对应 reference 末尾的"可执行工具"section
10. **多角度深度挖掘（数据返回后必跑反思）**：拿到工具数据不是答题终点而是挖掘起点。每次数据返回后过 5 维，任一维度触发新线索 → 继续检索；五维都无增量才收尾。**不为凑深度硬造，但也不要拿到一条数据就收尾**
    - ① **纵向**再追一个"为什么"：查到"净利润下滑"→ 继续拆成本 / 收入结构
    - ② **横向**看上下游 / 竞对：查到"比亚迪毛利走低"→ 顺查赛力斯 / 理想看是不是行业性
    - ③ **时间**放到 3-5 年周期看分位：查到"PE 25×"→ 调 5 年 PE 带看历史分位是高是低
    - ④ **反面**找最薄弱假设：依赖"消费复苏"→ 主动查社零 / CPI 反驳信号
    - ⑤ **行动**给条件化决策：补"若 X 跌破 Y 则 ……"，让用户拿到可操作框架
11. **有观点 + 反向声音**：分析类回答必须给经过推演的判断（不是平铺 N 种可能让用户自选）；主动点出"市场普遍知道什么、还没充分定价什么"，必要时给反向声音（"这个加仓决定可能基于一个错误的归因 —— X 的上涨其实是 Y 引起的"），不要顺着用户思路一路点头

## 时间口径（跨时区/跨市场必查）

金融数据强时效，回答时遵守以下规则：

- **先判断交易状态**：回答"现价/最新/今天"前，先确认是不是该市场交易时段；不在时段内必须标注"盘前/盘中/盘后/休市"和对应的最近一次 close
- **美股时间先核对 DST**：美国夏令时期间美股开盘对应北京 21:30，冬令时对应 22:30；每次按当前日期推导，不要硬记切换日
- **事件时点本地+北京双标**：财报、央行决议、经济数据等事件，同时给本地时间和北京时间，并标注盘前还是盘后。例：苹果 FY25Q1 财报 = 2025-01-30 美东盘后 16:30（北京时间 2025-01-31 05:30）
- **相对时间默认北京时区**：用户说"今天/昨天/本周"按北京时间解释；有歧义时（如"昨天美股"）第一句先点明绝对日期
- **跨市场比较先对齐窗口**：A股 T 日收盘 / 港股 T 日收盘 / 美股 T-1 夜盘 / 美股 T 日盘 不是同一时点；做联动分析时点明用的是哪种对齐
- **跨市场财报同期对比按自然年季度对齐**：FY 标号本身不能直接对（如腾讯 FY26Q1 = 自然年 2026Q1，阿里 FY26Q1 = 自然年 2025Q2，对不上）。先把每家 FY 拆成它实际覆盖的自然年季度（腾讯 FY = 自然年；阿里 FY 4 月制；苹果 FY 9 月底制；微软 FY 7 月制），再按"自然年同季度"配对做季度比，或用 **TTM 滚动 4 季** 做年度比——TTM 本身就是按自然年季度滚动求和，自动消除 FY 定义差异。详细步骤与币种 / 估值口径一致性见 `references/peer-comparison.md` 与 `references/valuation-pricing.md`

## 数据口径与标的核对

- **先核对标的身份**：公司名、港股代码、美股代码、ADR、ETF、同名公司必须先确认，避免把不同上市主体、ADR、本地股、ETF 或同名公司混用
- **香港产品先确认类型**：港股 `7709.HK` 这类代码可能是 ETF、杠杆产品、牛熊证或结构化产品；查 NAV 前必须先确认产品类型。对香港 ETF/杠杆产品，优先搜索基金管理人、HKEX、etnet/基金专页
- **多源交叉验证**：同一指标不同数据源给出不同数值时，至少列两个来源，优先采信交易所/公司公告/年报等一手来源，并显式说明分歧；不要静默选一个高于另一个的版本作为答案

## 场景方法论 references

`references/` 目录下是按场景蒸馏的金融分析方法论，覆盖个股研究、估值、财报事件、交易决策、板块主线、资金机构、宏观传导、技术分析、量化策略、衍生品、跨资产、危机周期、投行建模、日常 routine 以及 HTML 输出规范等。**当用户的请求落入对应场景时，先读取相应 reference 再作答。**

**使用规则**：
- 每条 reference 是"方法论 + 量化阈值 + 避坑"三段式，不是输出模板——分析时按其框架思考，但**不照抄章节标题或字数限制**
- 多场景叠加时（如"分析 A 股票该不该买"同时涉及个股研究 + 估值 + 仓位决策），并行读取多个 reference 综合判断
- 方法论类 references 只管"分析框架"，**数据获取走 agentic_search 工具 / 通达信 MCP（如可用）**

**索引（按场景类别分组）**：

**数据源调用**
- `tdx-mcp-quick-reference.md` 通达信 MCP 调用速查（10 个工具实测示例、fixedTag 路由表、避坑清单、已知限制）—— 仅在用户装了通达信 MCP 时使用

**个股研究**
- `stock-first-look.md` 个股初探（含热门股快读）
- `stock-deep-research.md` 个股深度研究（投资逻辑研究）
- `business-model.md` 业务模式拆解
- `valuation-pricing.md` 估值与定价（PE/PB/DCF/PEG/分部估值）
- `moat-quality.md` 护城河与公司质地
- `management-assessment.md` 管理层体检
- `peer-comparison.md` 同业比选
- `quality-growth.md` 质量增长匹配（高质复利 / 增长质检 / 价值股息）

**财报与事件**
- `earnings-preview.md` 财报前瞻
- `earnings-review.md` 财报后反应（业绩会提炼 / 财后漂移）
- `announcement-impact.md` 公告影响与股东信解读
- `event-catalyst.md` 事件驱动短线催化

**交易与持仓**
- `trade-plan.md` 交易计划与买卖点
- `position-sizing.md` 仓位决策与加减仓
- `portfolio-checkup.md` 持仓体检与风控
- `stop-discipline.md` 止损纪律
- `monitor-alert.md` 监控告警与停复牌

**板块主线题材**
- `sector-comparison.md` 板块比较与轮动
- `market-mainline.md` 市场主线与情绪
- `market-state.md` 市场状态与广度
- `theme-lifecycle.md` 题材周期与龙头
- `leader-game.md` 涨停龙头博弈与龙虎榜

**资金与机构**
- `fund-flow.md` 资金流与北向
- `institutional-holding.md` 机构持仓与拥挤度

**宏观/政策/产业链**
- `macro-transmission.md` 宏观行业个股传导
- `policy-impact.md` 政策解读与受益映射
- `industry-chain.md` 产业链映射与卡点

**技术分析**
- `breakout-patterns.md` 波缩突破与 VCP
- `price-action-tools.md` 技术指标与形态识别（K 线 / 谐波 / 波浪 / 缠论 / 一目 / SMC）
- `abnormal-detection.md` 放量异动与跳空归因

**风险与量化**
- `risk-stress.md` 风险压力测试（VaR / CVaR / 蒙特卡洛）
- `quant-factor-research.md` 因子研究框架
- `systematic-strategies.md` 量化策略库（配对 / 事件驱动 / 季节性 / ML / 对冲 / 波动率）
- `portfolio-optimization.md` 资产配置与组合优化

**衍生品与跨资产**
- `options-strategies.md` 期权策略（多腿组合 + Greeks）
- `fixed-income.md` 固定收益与可转债
- `forex-commodity.md` 外汇与大宗商品
- `crypto-derivatives.md` 加密衍生品（仅在用户明确要求时使用）

**主题**
- `dividend-buyback.md` 分红回购与股东回报
- `going-global.md` 出海链投资
- `crisis-event.md` 危机 / 反转 / 周期拐点

**投行建模**
- `ib-models.md` 投行估值建模（DCF / LBO / comps / 三表 / M&A / Unit Economics）
- `ib-deal-prep.md` 投行交易准备（尽调 / 投委会 / IM / pitch / NDA）

**日常 routine**
- `daily-briefing.md` 每日投研简报（盘前 / 收盘 / 晨会）

**输出规范**
- `html-report-style.md` HTML 研报输出（JS 自检 / ECharts 骨架 / 图表分工与质量细则）——产出 HTML 前先读

## 通达信 MCP（如可用）
**仅在用户环境装了通达信 MCP 时启用**——通过列出的 MCP 工具是否包含 `tdx_quotes` / `tdx_kline` / `tdx_api_data` / `tdx_indicator_select` / `tdx_screener` / `tdx_lookup_stock` / `wenda_news_query` / `wenda_notice_query` / `wenda_report_query` / `wenda_macro_query` 来判断。可用时优先在以下场景调用：

- 上面没覆盖或返回不全的细分接口（深度财务三表多期、十大流通股东全历史、限售解禁、股本变动、港股财报多期回溯、个股 / 全市场龙虎榜结构化、自然语言条件选股、宏观时序数据）
- 需要按通达信特有路由（`entry` + `fixedTag` + `code`）取结构化字段，而不是 LLM 描述
- 验证上面给出数据是否准确（多源交叉验证）

**调用前先读 references/tdx-mcp-quick-reference.md** —— 里面是 10 个工具的实测调用示例、参数含义、fixedTag 路由表、错误排查方法、已知限制。**不要凭记忆拼参数**（setcode、target、fixedTag 都有踩坑点）。
---

## A股量化数据引擎（整合 a-stock-data-quant）

当你需要**实际获取 A股数据或做量化计算**时，使用本引擎（源自 a-stock-data-quant）：

- **完整内嵌实现（自包含零依赖外部文件）**：`Read references/a-stock-full.md`，按其内嵌代码直接运行。
- **命令行主程序**：`python3 bin/quant.py <command> <args>`
  - `analyze <code>` 综合分析（如 `sh600519` / `sz000858`）
  - `compare <c1>,<c2>` 多股对比
  - `backtest <code> --strategy ensemble --html` 多策略共振回测
  - `realtime <code>` 实时行情
  - `market-temp` 市场温度计（5 维度）
  - `valuation <code>` 估值分位（PE/PB/PS）
  - `hot-stocks --mode turnover` 热门股票排行
  - `hot-boards --mode gainers` 热门板块排行
  - `board-stocks BK0892` 板块成分股
  - `capital-flow <code>` 资金流向细分
  - `fundamentals <code>` 基本面快照
  - `chip <code>` 筹码分布
- **数据源**：12 层（腾讯财经 / 东方财富 push2 / mootdx 通达信 / 百度股市通 / 东财 reportapi / 巨潮 cninfo / 东财 datacenter / 同花顺 hexin / 广发 MCP / 东方财富妙想 AI 等）。

## 同花顺 Financial API（hithink-finance）集成 —— 权威 A股 / 指数 / 基金 / 特色数据远端接入层

> 来源：`HiThink-Tech/Financial-API`（整树已并入本 skill 的 `references/hithink-finance/`，主入口总览见 `references/hithink-finance/00-overview.md` = 原 hithink-finance SKILL.md）。这是**同花顺官方金融数据服务（iFinD 级）**的 Agent 统一入口，经 4 种方式提供 A股 / 指数 / 板块 / 公募基金的权威数据。**定位：本 skill 的「备用信息源」，不是默认首选。** 默认优先走公共信息源（引擎层 `bin/quant.py` / `bin/cn/*.py`、 `agentic_search`、通达信 MCP、WebSearch）；仅当公共源不可用 / 覆盖不足、且**用户明确同意启用**时，才回退到 hithink 继续取数。

### 何时启用 hithink（备用条件 · 需用户确认）
- **公共信息源全部不可用或覆盖不足**：引擎层多源降级仍失败、 `agentic_search` 不可达、无通达信 MCP、WebSearch 也补不到时；
- 需要引擎层缺失或偏弱、且用户已同意启用的能力：**集合竞价**、**公募基金全字段**（经理 / 持仓 / 财务 / 资讯）、**特色数据**（涨停池 / 跌停池 / 炸板 / 连板梯队 / 个股异动原因 / 热榜 / 龙虎榜）、**全市场 Parquet 批量导出与本地 DuckDB 建库**、**权威复权因子流**；
- 用户主动点名「用同花顺 / iFinD / hithink 数据」并提供了 Key。
> ⚠️ **越级禁止**：公共源可用时，**不得**跳过公共源直接走 hithink；hithink 仅在「公共源失败 + 用户同意」的降级链路上启用。

### 四种接入方式（只选其一，按环境）
| 场景 | 首选 | 入口 reference |
| --- | --- | --- |
| 人类终端 / Agent 执行 / 本地 DuckDB 大结果落盘 | CLI（`hithink-finance`） | `references/hithink-finance/cli.md` |
| Chat/IDE 已连托管 MCP | MCP（4 个 HTTP 端点，55 工具） | `references/hithink-finance/mcp.md` |
| 零依赖 HTTP / 自定义脚本 / 服务端 | REST API（59 端点） | `references/hithink-finance/api.md` |
| Python / Notebook / 已有 marketdb | Python SDK | `references/hithink-finance/python-sdk.md` |

### 统一 API Key（四种方式共用）
- 获取：<https://fuyao.aicubes.cn/admin>；推荐环境变量 `HITHINK_FINANCE_API_KEY`。
- 校验顺序：运行时安全输入 → `HITHINK_FINANCE_API_KEY` → 用户级 `credentials.env` → 兼容旧 `FUYAO_TOKEN` / `API_KEY`。缺失时引导用户注册获取，**不得把 Key 写入代码 / Prompt / 日志 / 输出 / Git**。
- 接入前先探测环境（是否已配 Key / 是否连 MCP / CLI 是否在 PATH），不要让用户重复提供技术参数。

### 能力覆盖（数据域 → 端点 / 工具）
| 数据域 | 覆盖 |
| --- | --- |
| 标的消歧 / 代码表 | 元信息检索（按名称 / ticker / 中英文跨市场消歧为唯一 `thscode`） |
| A股行情 | 最新快照 / 历史日 K（前复权·后复权）/ 分红送股等复权因子流 |
| 财报 | 利润表 / 资产负债表 / 现金流量表 多期 + 指定报告期财务指标 |
| 估值 | A股 最新 PE/PB/PS/PCF 批量快照（保留 null 与负数） |
| 交易日历 | 近一年交易日序列 |
| 集合竞价 | 实时 / 终态快照 + 短期强弱基准 |
| 指数 / 板块 | 同花顺概念 / 行业 / 区域 / 特色指数目录、成分股、指数 / 板块行情（日 / 周 / 月 K） |
| 公募基金 | 资料 / 公司 / 经理 / 披露 / 财务 / 净值 / 收益 / 持有人 / 诊断 + ETF/LOF 场内快照与日线（28 端点） |
| 特色数据 | 涨停池 / 跌停池 / 炸板池 / 连板梯队 / 个股异动原因 / 飙升榜 / 热股榜 / 龙虎榜（11 端点） |
| 全市场导出 | 10 年日 K / 近 10 日 / 复权因子 Parquet 下载链接（自建库首选，勿逐只拉） |

### 能力边界（明确不覆盖 —— 超出时回退本 skill 其他层或显式说明）
- ❌ 分钟 K / tick / Level-2；❌ 港股 / 美股；❌ 期货 / 期权；❌ 宏观数据 / 新闻公告原文 / 研报 / 回测引擎；❌ 基金申赎交易或基金推荐。
- 这些域继续走本 skill 的引擎层（`bin/quant.py` / `bin/cn/*.py`）、`agentic_search`、通达信 MCP 或 WebSearch；**不得用 hithink 近似数据或模拟数据冒充**。

### 🔴 降级启用流程（用户确认门 · 公共源失败时的唯一入口）
当公共信息源（引擎层 / `agentic_search` / 通达信 MCP / WebSearch）不可用或覆盖不足、而任务又必须用 hithink 才能满足时，严格按以下 if-then 链路走，**不得静默切换**：

1. **判断**：公共源是否确实失败 / 缺失？是 → 进入第 2 步；否 → 继续走公共源，不提 hithink。
2. **询问 + 告知获取地址（🔴 必须显式问用户，不能替用户决定）**：
   > 「当前公共数据源暂不可用 / 覆盖不足。是否启用**同花顺金融数据服务（hithink-finance）**作为备用源？
   > 如需启用，请前往 <https://fuyao.aicubes.cn/admin> 注册并获取**统一 API Key**，把 Key 发给我，我来配置后继续取数。
   > 不启用也可，我会按红线说明『当前数据源未覆盖，需进一步核实』，不会编造数据。」
3. **分支**：
   - 用户**提供 Key** → 配置 `HITHINK_FINANCE_API_KEY`（环境变量 / `credentials.env`，不写入代码 / Prompt / 日志 / 输出 / Git），按上方「四种接入方式」继续取数；
   - 用户**拒绝 / 无 Key** → 按本 skill 红线输出「当前数据源未覆盖该标的 / 字段，需进一步核实」，给替代路径（WebSearch / 下次重试），**绝对禁止编造数值**。
4. **继续**：拿到 Key 后用 hithink 完成取数，同样遵守红线（禁编造）、数据底线（来源 + 时点 + 口径可追溯）、输出护栏（免责声明）。

### 路由硬规则
- hithink 是**远端 Key 服务 + 备用源**：公共源可用时默认不走它；公共源失败且**用户确认启用**后才进入上方「降级启用流程」。
- **未获用户同意，不得静默切到 hithink，不得假装 hithink 已可用，不得编造或复用旧 Key**；用户发来 Key 前，按红线给出「数据源未覆盖」结论。
- 取数后同样遵守本 skill 红线（禁编造）、数据底线（来源 + 时点 + 口径可追溯）、输出护栏（免责声明）。

### 反例黑名单（不要做什么）
- ❌ 公共源可用时越级用 hithink（破坏「公共源优先」原则）；
- ❌ 未问用户、未给获取地址就直接声称「已切换到同花顺」；
- ❌ 把 Key 写入代码 / Prompt / 日志 / 输出 / Git，或复述用户发来的 Key；
- ❌ 用户无 Key 时编造 hithink 数据或旧价冒充实时；
- ❌ 把 hithink 不覆盖的域（港股 / 美股 / 期货 / 期权 / 宏观 / 新闻 / 研报 / 回测）冒充可查。

## 🔴 数据源降级与故障处理（取数前必读）

引擎内置 12 层源，但**部分源已实测不稳定/失效**。取数时按以下 if-then 分支兜底，**禁止编造或无故跳过**：

| 触发条件（实测故障） | 一线修复 | 仍失败的兜底 |
|---|---|---|
| 实时/日K：腾讯(qt.gtimg.cn)正常、新浪(money.finance.sina)正常、东财 push2 本机可能 peer reset（仅补充） | 三者按顺序取，取到的即返回 | 三者都失败 → **明确告知用户"实时行情源当前不可用"，绝不返回训练记忆中的旧价** |
| 日K 兜底：百度股市通(finance.pae.baidu.com)已返回 `ResultCode:403` **已废弃** | **跳过百度源**，改用腾讯/新浪 | 不把百度当作兜底层（否则会 `raise` 全失败） |
| 北向资金：同花顺(data.hexin.cn)响应结构已变更、`get_north_flow` 取到空 `[]` | 改用 akshare 北向接口或东财 datacenter | **不输出空的北向结论**，注明"北向数据本次未取得" |
| 成交额单位：腾讯实时 `fields[37]` 单位与预期不符（实测偏低 1e4） | 改用 `fields[35]` 段取值 | 输出"成交额"前做量级 sanity check（单股日成交额通常千万~百亿级，明显偏离则改取东财 push2 字段） |
| 腾讯日K：`web.ifzq.gtimg.cn` 走 http 被 302 跳 https | 直接改用 `https://` 端点 | 跟随重定向仍失败则用新浪K线 |
| **全源失败**（依赖未装/网络全断） | 按上表逐级降级 | 输出"当前数据源未覆盖该标的/字段，需进一步核实"，并给替代路径（WebSearch 公开信息 / 下次重试），**绝对禁止编造数值** |

> **同花顺 Financial API（hithink-finance）是「备用信息源」**：默认优先走公共源（引擎层 / `agentic_search` / 通达信 MCP / WebSearch）。仅当**公共源全失败或覆盖不足**且**用户明确同意启用**时，才走 hithink（见上方「同花顺 Financial API（hithink-finance）集成」章节的「🔴 降级启用流程」）：先问用户是否启用、告知 Key 获取地址 <https://fuyao.aicubes.cn/admin>、用户发来 Key 后再继续取数。其为同花顺官方 iFinD 级源、含权威复权因子；**未获用户同意前不得假装可用或静默切换**。

> 依赖与运行前置：引擎依赖 `akshare/numpy/pandas/requests/pyyaml/mootdx`。**未 `pip install -r requirements.txt` 就直接 `python3 bin/quant.py` 会整层报错**——先确认依赖已装（建议 Python 3.10–3.12，避开 3.13 对 akshare 的兼容问题），缺失则提示用户安装后再跑。
> **已配好 venv**：本 skill 目录内含 `venv/`（Python 3.12 + 全套依赖，清华镜像安装），运行请用 `venv/Scripts/python.exe`（不要直接用系统 `python3`，那是 3.13 且缺依赖）。Windows 路径：`C:/Users/jangviktor/.workbuddy/skills/a-stock-data-quant/venv/Scripts/python.exe`。
> **bin/cn 数据层**：`bin/cn/*.py`（equity/futures/research/options/macro）与 wb 引擎共享同一 venv（akshare 已装，`requirements.txt` 已统一 `akshare>=1.18.64`）。调用：`venv/Scripts/python.exe bin/cn/equity.py quote 600519,00700`；其 stdlib 命令（价量/期货/北向）无 akshare 也可跑，研报/期权/宏观命令缺 akshare 时会显式报安装提示（不崩）。

## 个股买卖决策工作流（多指标综合 → 操作建议）

当用户**直接问某只个股"该买 / 该卖 / 能不能进 / 要不要跑"**时，必须走「取数 → 多指标诊断 → 给建议 + 理由」完整链路，**禁止凭感觉或记忆直接给买卖结论**（违反红线：禁编造数据）。

1. 🔴 **取数（数据必须动态获取，不得凭记忆）**：先跑引擎取真实数据——
   - `python3 bin/quant.py analyze <code>`（实时 / 估值 / 资金流 / 筹码 / 技术信号一次出），或按 `references/a-stock-full.md` 取；
   - 技术面补 `references/price-action-tools.md`、估值面补 `references/valuation-pricing.md`、资金面补 `references/fund-flow.md`、基本面补 `references/stock-deep-research.md`。
2. **四维诊断（每维给「偏多 / 中性 / 偏空」+ 关键证据，禁止空泛）**：
   - **技术面**：趋势（均线上下）+ MACD / RSI / KDJ 位置 + 量价 / 形态（突破 or 背离）
   - **估值面**：PE / PB / PS 历史分位（低位 = 安全边际）+ 同业对比
   - **资金面**：主力净流入 / 北向（若可取）/ 换手率 / 筹码集中度
   - **基本面**：营收净利趋势 / ROE / 护城河 + 近期催化或风险
3. **综合信号**：四维加权 → 落到明确一档 **买入 / 增持 / 持有 / 减仓 / 卖出**；附**置信度（高 / 中 / 低）**与「核心矛盾点」（最制约结论的一项）。
4. **操作框架（条件化，非点位承诺）**：给「触发条件 → 动作 → 风控」——
   - 例：`若回踩 XX 均线不破且量能回升 → 分批建仓；止损位设在 XX；单股仓位 ≤ X%`
   - **禁止给无条件「现在就买 / 卖」指令**。
5. 🔴 **CHECKPOINT · 输出前护栏**：结论前先列**前提**（当前市场环境 + 用户风险偏好 + 资金量 / 期限），前提缺失主动追问；回复末尾**必附固定免责声明**（见上方「红线」模板），禁止改写 / 省略。

> 输出结构建议：「结论卡（结论 + 置信度 + 矛盾点）+ 四维诊断表 + 操作框架 + 免责声明」。简短用 Markdown，完整用 HTML 研报风。技术信号基于历史数据、不预测未来，建议仅作决策输入而非指令。

## ETF 买卖决策工作流（多指标综合 → 操作建议）

当用户**直接问某只 ETF / 指数基金 / 场内基金"该买 / 该卖 / 能不能定投 / 要不要跑"**时，走与个股相同的「取数 → 多指标诊断 → 给建议 + 理由」完整链路；**诊断维度按 ETF 特性特化**（ETF 是篮子、无个股式财报），同样禁止凭记忆直接给买卖结论。

1. 🔴 **取数（数据必须动态获取，不得凭记忆）**：引擎对 ETF 代码（如 `510300` 沪深300ETF、`518880` 黄金 ETF）自动识别为 `etf` 品类——
   - `python3 bin/quant.py analyze <etf_code>`（实时 / 估值 / 资金流 / 技术信号一次出）；
   - 技术面补 `references/price-action-tools.md`、估值面补 `references/valuation-pricing.md`、资金面补 `references/fund-flow.md`；
   - 跟踪指数估值分位可补 `bin/quant.py index-val <指数代码>`（PE/PB 百分位 + 关联 ETF，需广发 key；无 key 改 akshare/东财）；
   - ETF 份额变化：`bin/quant.py capital-flow <code>` 或 akshare `fund_etf_category_sina` / `fund_etf_hist_em`（份额净流入是 ETF 资金面最直观指标）。
2. **四维诊断（ETF 特化，每维给「偏多 / 中性 / 偏空」+ 关键证据，禁止空泛）**：
   - **技术面（同个股）**：趋势（均线上下）+ MACD / RSI / KDJ 位置 + 量价 / 形态。ETF 价格即跟踪指数走势，技术信号直接可用。
   - **估值面（按 ETF 类型分支，这是与个股最大差异点）**：
     - 股票型 ETF（宽基 / 行业 / 主题 / 策略）→ 看**跟踪指数** PE/PB 历史分位（低位 = 安全边际）+ 同业对比
     - 债券型 ETF → 利率方向 + 久期 + 到期收益率；利率下行周期通常利好债基
     - 商品型 ETF（黄金等）→ 金价 / 实际利率 / 美元指数；避险升温通常利多
     - 跨境 / QDII ETF → 海外估值分位 + **汇率** + **溢价率**（高溢价 = 回落风险，警惕追高）
   - **资金面（ETF 核心指标）**：**ETF 份额变化（资金净流入最直观）** / 融资余额 / 换手率 / 北向（对 A 股 ETF）；份额持续流入 = 资金看好，流出 = 降温。
   - **基本面（ETF 选品层，与个股完全不同）**：**跟踪误差 / 基金规模（流动性） / 折溢价率 / 管理费率 / 标的指数质量**——同名 ETF 优先选规模大、跟踪误差小、费率低、折溢价≈0 的；规模过小有清盘风险。
3. **综合信号**：四维加权 → 落到明确一档 **买入 / 增持 / 持有 / 减仓 / 卖出**；附**置信度（高 / 中 / 低）**与「核心矛盾点」（如"指数估值低位但溢价率过高"）。
4. **操作框架（条件化，非点位承诺）**：给「触发条件 → 动作 → 风控」——
   - 例：`若跟踪指数 PE 分位 < 30% 且份额持续流入 → 分批 / 定投建仓；溢价率 > 5% 则等回落再进；单 ETF 仓位 ≤ X%`
   - **禁止给无条件「现在就买 / 卖」指令**。ETF 特别提示：高溢价跨境 ETF 勿追高、商品 ETF 看实际利率拐点、债基看利率周期。
5. 🔴 **CHECKPOINT · 输出前护栏**：结论前先列**前提**（当前市场环境 + 用户风险偏好 + 资金量 / 期限 + 是否定投），前提缺失主动追问；回复末尾**必附固定免责声明**（见上方「红线」模板），禁止改写 / 省略。

> 输出结构建议：「结论卡（结论 + 置信度 + 矛盾点）+ 四维诊断表（估值面按 ETF 类型标注分支）+ 操作框架 + 免责声明」。ETF 买卖建议本质是"在指数估值 + 资金流向 + 折溢价 + 选品质量"四维上的择时，技术信号基于历史数据、不预测未来，建议仅作决策输入而非指令。

## 引擎使用反模式（dim9 黑名单，禁止）

- 禁止硬编码 / 凭记忆输出行情、财务、技术指标数字（红线已强调，引擎侧再强调一次）
- 禁止把已废弃的百度K线(finance.pae.baidu.com)当作可用兜底层
- 禁止所有源失败时静默返回空表，或用旧数据伪装成实时数据
- 禁止未确认依赖就执行 `bin/quant.py`（akshare / mootdx 缺失 = 整层 RuntimeError）
- 禁止对"北向/资金流"等已坏源假装取到数据——取空就显式声明缺口
- **依赖**：`akshare / numpy / pandas / requests / pyyaml / mootdx`（见 `requirements.txt`）。建议在 Python 3.10–3.12 环境执行 `pip install -r requirements.txt`（当前 WorkBuddy 自带 Python 3.13 对 akshare 兼容性存疑）。
- **配置**：`config.yaml` 含示例 API key（`EM_API_KEY` 东方财富妙想、`GF_SKILLS_APIKEY` 广发），可选；AI 分析功能可用环境变量 `EM_API_KEY` / `GF_SKILLS_APIKEY` 或改 config 配置。
- **免责声明**：本工具仅供学习研究，不构成投资建议；技术分析基于历史数据不预测未来。
