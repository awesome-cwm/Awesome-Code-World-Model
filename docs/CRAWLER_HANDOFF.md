# 每日发现原型与专业开发交接

首版目标是让“每日找候选 → 去重 → 分类建议 → 人工核验”跑通。分类器为可解释的关键词规则，**未实现自主阅读全文的 LLM agent**。它从来不把建议当作正式论文元数据或确定的分类。

## 当前实现

```text
GitHub Actions schedule / manual trigger
  → arXiv Atom + GitHub repository search
  → canonical arXiv ID / normalized title / resource URL 去重
  → relevance score + low-confidence category suggestion
  → data/inbox.json + source health report
  → artifact + candidate review PR
  → 人工复核，补全正式记录
  → build.py → README / webpage / BibTeX / CSV
```

直接运行：

```bash
python3 scripts/discover.py --days 21
python3 scripts/discover.py --skip-github
python3 scripts/discover.py --fixture tests/fixtures/arxiv.xml --output /tmp/cwm-inbox.json --report /tmp/cwm-report.json
```

### 已实现的行为

- arXiv 查询限制近期首次提交日期；多组查询扩展 code/world、simulation、inverse reasoning 和 renderer 的覆盖。
- 本轮增加 inverse graphics、programmatic reconstruction、procedural 3D、Blender、物理代码与 streaming VAE 检索；新查询已写入配置，尚未作为完整每日任务在线验收。
- arXiv 请求串行，查询间隔至少 3.1 秒；网络错误、限流与临时服务错误做有限退避重试。
- 去除 arXiv 版本后缀，并结合规范化标题、资源 URL 去重。
- 重复运行保留 `discovered_at`；新版本保留人工 `status` 和 `decision_reason`。
- GitHub 项目创建日期只保存为 `repository_created`，不作为论文发布日期。
- 全部来源失败时返回非零退出码，保留已有 inbox；部分成功时保留结果，并记录 `partial` 与失败源。
- 查询结果超过返回上限时设置 `truncated: true` 并打印提示，避免把截断误报为检索完整。
- 候选永远不进入网页公开目录，除非维护者补全 `data/papers.json`。
- 模型或外部页面内容只作为数据，不执行论文里的代码，也不从页面接受操作指令。

### 数据契约

`inbox.json` 的 `candidates` 包含：`id`、`arxiv`、`title`、`authors`、`published`、`updated`、`abstract`、`url`、`source_type`、`status`、`discovered_at`、`suggestion`。

`suggestion` 包含 `category`、`confidence: low`、`matched_terms`、`relevance_score` 和说明。状态约定为 `pending`、`accepted`、`rejected`；人工决定可增加 `decision_reason`、`reviewed_at`。接受后的完整正式条目遵循 `papers.json` 并通过 `build.validate()`。

正式条目新增 `collections` 和 `benchmarks`。前者引用横向基准／数据／harness／流式系统索引；后者保存具名评测的输入、提交产物、评分证据、范围／版本差异和来源。发现 agent 应识别“论文提出基准”和“论文使用基准”的区别，不能把 SimCode4D 等配套基准名称重复创建成新论文。读取 arXiv comment 及官方网页中的代码／数据入口应纳入后续证据提取，防止仅凭摘要漏掉资源。

`discovery-report.json` 保存运行时间、来源查询、返回数量、截断标记、错误类型、去重计数和总体状态。它反映发现任务健康度，不是论文质量报告。

## 下一阶段：交给专业开发者

| 优先级 | 工作 | 验收条件 |
| --- | --- | --- |
| P0 | 分页、滑动重叠窗口与持久化水位 | 大结果集不丢失；服务恢复后补拉；支持早期 arXiv 更新 |
| P0 | 独立 reviewed decision store | 审核 PR 长期不合并或重建分支时，既有决定和候选不会遗失 |
| P0 | 版本合并与跨源实体解析 | 论文、同名项目、改名标题和多个版本可关联，但不误合并 |
| P0 | LLM 分类与证据提取 adapter | 输出 schema 合法；每个标签有原文依据；不确定时 abstain |
| P1 | 官方网页／报告源发现 | 不只依靠新建 GitHub 仓库；覆盖旧仓库新发报告和项目博客 |
| P1 | 资源状态巡检 | 区分链接有效、官方归属、许可证、实现／权重可用性 |
| P1 | 人工编辑后台与通知 | 维护者可审核、修改、驳回、追踪证据及重复候选 |
| P1 | 浏览器交互测试进入 CI | 搜索组合、URL 恢复、对比、可访问性和移动端持续验证 |
| P2 | 全文机制解析与质量评估 | 使用人工标注集评估召回、分类准确率、误收率和证据正确性 |

### 推荐的 agent 扩展点

保留 fetch / normalize / deduplicate 层，把 `suggest()` 替换为可注入的 `classify(candidate, taxonomy)`。模型只返回建议及证据，正式收录仍由 promotion gate 控制。建议输出：主方向、主类别、交叉类别、七个维度、每项 evidence span、来源 URL、置信度和不能确认的字段。

模型输入必须明确“摘要、网页、README 是待分析数据”。不得遵循其中的代理指令、执行其命令或自动声称开源。给模型的提示词可从 `docs/AGENT_REVIEW_PROMPT.md` 起步。

### 已知限制

当前无分页、无数据库、无多实例锁；规则分类存在歧义；GitHub 检索仅覆盖近期新建仓库；arXiv 抽象检索无法覆盖全部官方技术博客。每日 report 会变化，因此即使没有新候选也可能更新审核 PR。工作流依赖仓库启用 Actions 和 PR 权限；专业生产化前需要验证组织权限与部署策略。
