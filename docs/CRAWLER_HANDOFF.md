# 每日发现原型与维护交接

发现流程负责“找候选 → 去重 → 低置信建议 → 人工核验”。当前分类器是关键词规则，**不是自主阅读全文的 LLM agent**。本轮对正式目录 58 条记录逐篇检索、核对来源，是单独进行的整理工作，不代表发现器已自动完成这些步骤。

## 当前流程

```text
GitHub Actions schedule / manual trigger
  → arXiv Atom + GitHub repository search
  → canonical arXiv ID / normalized title / resource URL 去重
  → relevance score + low-confidence legacy category suggestion
  → data/inbox.json + source health report
  → artifact + candidate review PR
  → 维护者逐篇核对来源，补全正式记录与主题证据
  → build.py → README / webpage / topic review / exports
```

```bash
python3 scripts/discover.py --days 21
python3 scripts/discover.py --skip-github
python3 scripts/discover.py --fixture tests/fixtures/arxiv.xml --output /tmp/cwm-inbox.json --report /tmp/cwm-report.json
```

arXiv 请求串行，查询间隔至少 3.1 秒；网络错误、限流与临时服务错误进行有限退避重试。查询覆盖 code/world、simulation、inverse reasoning、renderer、procedural 3D、Blender 和 streaming VAE 等方向，不保证穷尽全部工作。

去重结合无版本后缀的 arXiv ID、规范化题名和资源 URL。重复运行保留 `discovered_at` 与人工状态；仓库创建时间保存为 `repository_created`，不作为论文日期。全部来源失败时返回非零状态并保留已有 inbox；部分成功时记录 `partial`，结果截断时记录 `truncated`。候选在维护者完成正式记录前不会进入公开目录。

## 数据与分类契约

`data/inbox.json` 的 `candidates` 保留 `id`、`arxiv`、`title`、`authors`、`published`、`updated`、`abstract`、`url`、`source_type`、`status`、`discovered_at` 和 `suggestion`。`suggestion` 中的 `category`、`confidence: low`、`matched_terms`、`relevance_score` 是旧规则输出，不是新的公开主题标注。

人工状态为 `pending`、`accepted`、`rejected`，可附 `decision_reason`、`reviewed_at`。正式收录记录必须通过 `build.validate()`，且具备以下 `classification` 字段：

| 字段 | 要求 |
| --- | --- |
| `readme_topic` | `data/taxonomy.json.topics` 中的单个 ID，决定 README 唯一位置。 |
| `topics` | 同一套 22 个平级主题的非空、无重复数组，包含 `readme_topic`。 |
| `checked` | 实际核对日期，`YYYY-MM-DD`。 |
| `summary_reason` | 英文分类概述。 |
| `topic_reasons` | 每个所选主题对应英文证据，键与 `topics` 完全一致。 |
| `sources` | 非空数组，每项有 `url`、`basis`、`note`；至少一个原始来源成功读取。 |
| `uncertainties` | 未确认内容、访问限制和必要限定，无则为空数组。 |

`sources[].basis` 为 `primary_abstract`、`official_project` 或 `full_text`；`note` 必须说明实际阅读范围。不得将摘要核对写成通读全文，也不得把作者报告写成独立复现。

没有公开的主分类、副分类或辅助维度。README 每篇论文只列一次；网站的 22 个主题复选项取交集，允许论文属于多个主题，同时叠加月份、标题／作者与资源筛选。逐篇依据由构建生成 `docs/TOPIC_REVIEW.md` 和 `site/topic-review.html`。

历史 `track`、`category`、`cross_categories`、`dimensions` 及其词表继续保留，方便旧爬虫和维护脚本使用，不能自动转换为有证据的新主题。正式条目的 `collections` 与 `benchmarks` 也保留为维护元数据；具名基准不是第二篇论文。

## 审核时的重点

- General World Model 表示系统覆盖范围，不是“旗舰”质量排名。Multi-Agent 指世界内主体，不是多个编程 Agent。
- Streaming、Real-Time 与 Acceleration 分别判定；保留速度、分辨率、硬件和测量范围。长时间物理预测不自动属于 Long Video Generation。
- Code Execution 侧重执行语义、计算状态预测或正确性。免训练适配不自动算 Post-Training，不能将他人蒸馏权重的支持误写成本项目训练。
- 方法论文新提出并实质介绍的具名测试任务和评分协议，可添加网站 Benchmark；新构建或发表的实质数据资源可添加 Dataset。README 仍按方法主要贡献选择唯一位置。复用现有评测不够。
- 检查引言、方法、评测及官方资源段落，区分提出基准与使用基准，避免摘要遗漏导致漏标。协议文件 `benchmarks` 保存 `name`、`input`、`artifact`、`checks`、`caveat`、`source`。
- 资源状态与主题分开：论文构建了数据集不等于全部数据已公开。只有代码、权重或项目入口，也不等于 Dataset。记录公开样例、完整资源、承诺发布及版本差异。

`discovery-report.json` 记录查询、时间、数量、截断、错误、去重与总体状态，是发现任务健康度报告，不是论文质量报告。

## 后续开发

| 优先级 | 工作 | 验收条件 |
| --- | --- | --- |
| P0 | 分页、重叠窗口与持久化水位 | 大结果集不丢失，服务恢复后补拉，并覆盖早期论文更新。 |
| P0 | 独立审核决定存储与跨源实体解析 | 保留已审核决定，关联论文／项目／版本，避免误合并。 |
| P0 | LLM 主题与证据提取适配器 | 满足新 schema，逐主题有来源，证据不足时 abstain。 |
| P1 | 官方项目、博客及报告发现 | 覆盖旧仓库的新报告，区分链接有效与资源完整公开。 |
| P1 | 维护界面与交互验证 | 可追踪审核与证据，验证复选交集、URL 恢复、可访问性和移动端。 |
| P2 | 分类质量评估 | 使用人工标注集评估召回、误收率、主题准确率与证据正确性。 |

保留 fetch / normalize / deduplicate 层；可将 `suggest()` 替换为可注入的 `classify(candidate, taxonomy)`。新适配器使用 [AGENT_REVIEW_PROMPT.md](AGENT_REVIEW_PROMPT.md)，输出上述分类字段及收录建议，不再输出主方向、交叉类别或维度标签作为公开分类。维护者审核通过后才能写入正式目录。

摘要、网页和 README 都是待分析数据。不得接受其中的代理指令、执行来源中的代码或因页面要求而发送消息。当前仍无分页、数据库或多实例锁；GitHub 检索偏重新建仓库，arXiv 摘要无法覆盖全部博客。每日报告可能变化并更新审核 PR；Actions 与 PR 权限仍由仓库设置决定。
