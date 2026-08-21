# CONNECTORS.md —— 连接器占位符说明

`references/research-workflows/` 下的研报工作流子技能（读年报 / 可比公司分析 / 深度报告 / 业绩快评 / 调研纪要 / 行业研究 / 晨会纪要 / 研报摘要）均为**纯方法论工作流**，不强制依赖任何连接器（connector）。

## 占位符约定

各子技能正文中出现的 `{{占位符}}` 或 Connectors 章节均为**可选增强**，含义如下：

| 连接器 | 增强能力 | 缺失时行为 |
|---|---|---|
| Notion | 将产出（投资备忘录 / 研报等）写入 Notion 知识库 | 跳过，直接在本会话输出 |
| 腾讯文档 | 将产出写为在线文档供分享协作 | 跳过，输出 Markdown |
| 邮件 | 将产出发送到指定邮箱 | 跳过，提示用户自行发送 |
| 股票数据源 | 补充实时行情 / 估值 / 资金流数据 | 用本 skill 的 `bin/quant.py` 或 `bin/cn/*.py` 获取 |

## 使用方式

1. 未连接任何连接器时，工作流照常执行，仅跳过"写入外部"步骤。
2. 如需增强，请先在 WorkBuddy 中连接对应连接器，然后在产出末尾询问用户是否写入。
3. **禁止**因未连接连接器而中断工作流或编造"已写入"。

## 本 skill 自带的数据获取通道（无需连接器）

- A股/ETF/可转债核心：`venv/Scripts/python.exe bin/quant.py <cmd>`
- 港股/期货/期权/宏观/公告事件：`venv/Scripts/python.exe bin/cn/<equity|futures|research|options|macro>.py <cmd>`
