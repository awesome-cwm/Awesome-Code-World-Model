# Code World Models：主题分类

目录采用 **22 个平级主题**。每篇论文可以对应多个主题，网站通过复选组合查找论文。没有主分类、副分类或辅助维度。

README 为方便阅读，只将每篇论文放在一个最能代表其主要贡献的主题下。这个位置由 `classification.readme_topic` 指定，不增加分类层级；网站使用同一记录的 `classification.topics`，允许论文出现在多个主题的结果中。

## 主题表

词表与 ID 以 [data/taxonomy.json](https://github.com/awesome-cwm/Awesome-Code-World-Model/blob/main/data/taxonomy.json) 的 `topics` 为准。

| 主题 | 中文 | 何时使用 |
| --- | --- | --- |
| General World Model | 通用世界模型 | 提出整合世界状态、演化、交互或观察生成的完整框架；表示系统范围，不是质量排名。 |
| Memory | 记忆 | 研究持久状态、历史信息、离屏实体、对象身份或记忆一致性。 |
| Interactive | 交互 | 世界能响应用户或智能体动作，并继续运行。 |
| Real-Time | 实时 | 报告实时生成、模拟或低延迟交互；保留原始硬件与计时条件。 |
| Acceleration | 加速 | 减少推理、执行或渲染时间及计算开销。 |
| Long Video Generation | 长视频生成 | 研究持续、较长时长的视频生成与时间一致性。 |
| Streaming | 流式生成 | 增量接收输入、持续输出或按因果顺序分块生成。 |
| Multi-Agent | 多主体 | 世界内多个行动主体的共享状态、行为与相互影响。 |
| Action Control | 动作控制 | 用按键、鼠标、机器人动作等输入显式控制世界行为。 |
| Physics | 物理 | 研究物理机制、运动、接触、碰撞、材料或物理一致性。 |
| World Generation | 世界生成 | 按需求创建场景、资产、游戏或仿真环境。 |
| World Reconstruction | 世界重建 | 从图片、视频、轨迹或观测恢复场景、物理或规则。 |
| World Editing | 世界编辑 | 修改对象、布局、属性、行为或世界规则。 |
| Neural Rendering | 神经渲染 | 根据代码、可执行状态、几何或代理画面生成图像或视频。 |
| Planning | 规划 | 利用世界模型搜索、推演并选择行动方案。 |
| Agent Learning | 智能体学习 | 利用生成环境、模拟经验或世界模型反馈改进智能体。 |
| Code Execution | 代码执行 | 研究程序执行语义、计算状态预测或执行正确性。 |
| Post-Training | 后训练 | 对已有模型进行微调、强化学习、蒸馏或适配。 |
| Benchmark | 基准 | 提供可复用的测试任务与评分协议。 |
| Dataset | 数据集 | 以世界程序、场景、轨迹、仿真样例或配对数据为实质资源贡献；公开范围单独记录。 |
| Evaluation | 评测分析 | 集中分析能力、证据、局限或失败原因。 |
| Survey | 综述 | 整理文献、分类体系、研究进展与方向。 |

## 标注规则

- 先阅读原始摘要、官方项目、报告或论文正文，再逐篇判断。标签必须有实质内容支持；不按题名或旧分类自动转换，也不设固定标签数量上限。
- `readme_topic` 只能是一个合法主题 ID，且必须包含在该记录的 `topics` 中。`topics` 至少一项，不重复。README 全部论文条目各出现一次，不在“近期更新”或“阅读路径”再次列出。
- General World Model 不等于“旗舰”质量认证，也不因为论文使用了世界模型就自动添加。专门的加速器或解码器不因此成为完整世界模型。
- Multi-Agent 指世界内的主体；多个编程 Agent 协作不满足这个定义。
- Streaming 不自动等于 Real-Time；Acceleration 也不保证达到实时。长时间物理外推不自动等于长视频生成。
- Code Execution 不用于所有运行了代码的工作。免训练适配不自动成为 Post-Training；支持他人蒸馏后的权重，不表示本工作执行了蒸馏。
- 方法论文新提出并实质介绍的具名基准，可以添加网站 Benchmark 主题；新构建或发表的实质数据资源也可以添加 Dataset，是否完整公开另行记录。README 仍按方法主要贡献选择唯一位置。复用旧基准、附带普通实验或只提供演示，不足以添加这些标签。
- `resource_status` 记录代码、权重、项目或数据等资源的发布情况，与 Dataset 主题分开；数据集论文构建了完整资源，也可能只公开少量示例，应分别写清。存在资源链接不等于发布了数据集；基准协议成立也不等于全部文件已开放。

## 数据格式与证据

每条正式记录的 `classification` 保存：

| 字段 | 约束 |
| --- | --- |
| `readme_topic` | 单个主题 ID，仅决定 README 中的唯一位置。 |
| `topics` | 非空、无重复的合法主题 ID 数组，用于网站复选。 |
| `checked` | 实际核对日期，格式为 `YYYY-MM-DD`。 |
| `summary_reason` | 英文概述，说明为什么这样分类。 |
| `topic_reasons` | 每个已选主题对应一条英文证据说明；键必须与 `topics` 完全一致。 |
| `sources` | 非空来源数组，每项含 `url`、`basis`、`note`。 |
| `uncertainties` | 尚未确认、访问受限或需限定理解的事项；没有则为空数组。 |

`sources[].basis` 仅使用 `primary_abstract`、`official_project` 或 `full_text`。`note` 写明实际读到的部分，例如“摘要”“官方 README 的训练与速度表”“正文第 4 节”。正文只读了部分时应注明，不写成通读全文。英文说明应转述证据，避免大段复制原文。

本轮 58 条记录均已逐条检索并核对原始来源；30 条包含相关正文段落的定向核对，共记录 90 次来源引用。来源核对不代表独立复现或通过质量认证。逐篇依据见生成的 [Topic review](https://github.com/awesome-cwm/Awesome-Code-World-Model/blob/main/docs/TOPIC_REVIEW.md)，网站对应页面为 [topic-review.html](https://awesome-cwm.github.io/Awesome-Code-World-Model/topic-review.html)。

## 网站筛选

Survey 作为词表保留，目前没有收录记录，不为填满分类而放入不符的论文。

网站展示同一套 22 个复选项，多选取交集；论文卡片可以属于多个主题，但同一结果列表只显示一次。月份、标题／作者搜索和资源徽标筛选继续叠加。

例如 `?topics=memory,real-time` 查找同时涉及记忆与实时的工作。条件保存在网址中；旧网址中的 `area`、`direction`、`tags` 参数不再参与筛选。

历史 `track`、`category`、`cross_categories`、`dimensions` 与相关词表保留给旧爬虫和维护工具使用，不构成公开分类。修改主题定义应编辑 `data/taxonomy.json`，修改论文对应关系应编辑 `data/papers.json`，然后运行构建。

本文件是分类说明的规范版本；仓库根目录的 `Code_World_Models_Taxonomy.md` 保留相同内容，便于直接查看。
