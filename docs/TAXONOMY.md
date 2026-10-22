# World Models Taxonomy V2

分类结构遵循维护者提供的 V2 设计：**六个主分类、22 个细方向、八个辅助标签维度**。每篇论文只能归入一个主分类；辅助标签可以有一个或多个，横跨不同维度。

## 主分类 / Research Areas

| 主分类 | 细方向 |
| --- | --- |
| World Construction | Generation · Reconstruction · Programmatic Generation |
| World Dynamics & Simulation | State Prediction · Physical Simulation · Long-Horizon Rollout · Multi-Agent Dynamics |
| World Interaction & Control | Navigation · Action Control · World Editing · Rule Control · Multi-Agent Interaction |
| World Reasoning & Learning | Planning · Counterfactual Reasoning · Agent Learning |
| Modeling & Systems | Model Architecture · Training & Alignment · Inference & Serving |
| Resources & Analysis | Dataset · Benchmark · Evaluation · Survey |

主分类按论文最主要的研究贡献决定。构建仿真环境可以归入 World Construction；研究状态演化或求解过程可以归入 World Dynamics & Simulation。提出方法时配套提供 benchmark，并不自动将论文的主分类改成 Resources & Analysis。

细方向是主分类下的进一步说明，最多选择一个，并且必须属于所选主分类。如果图中的细方向不能准确表达论文的目标，可以留为 `null`，而不是强行指定不受证据支持的方向。例如，可执行物理推理的研究不必被直接认定为反事实推理。

## 辅助标签 / Tag Dimensions

维度名称与维护者的设计保持一致。具体取值从已有分类、机制维度与整理过的论文说明中迁移，统一词表在 `data/taxonomy.json`。

| 维度 | 当前标签 |
| --- | --- |
| Research Challenges | Inverse Reconstruction · Physical Consistency · Temporal Consistency · Compositional Generalization · Physical Reasoning · Functional Correctness · Counterfactual Testing |
| Memory & State | Explicit State · Persistent State · Off-screen State · Object Identity · Visual Memory |
| Control & Interaction | Action-conditioned · Closed-loop Interaction · Program Editing · Rule Editing · Camera Control · World Expansion |
| Representation & Output | Scene Programs · Transition Programs · Physics Programs · Visual Proxies · Software Execution Traces · Physical Language · Scene Constraints · Neural Geometry · Video Latents · Code & Simulation Corpora |
| Methods & Training | Program Synthesis · Program Search · Execution Feedback · Visual Feedback · Physics Feedback · Trajectory Fitting · Task Feedback · Model Training · Multi-agent Methods · Distillation · Training-free |
| Runtime & Efficiency | Streaming Output · Runtime Measurement · GPU Computing · Cache Reuse |
| World Setting & Domain | General Worlds · Physical Phenomena · Robotics · Games · Video Generation · Software Environments |
| Evaluation Focus | Executability · Visual & Geometric Fidelity · Physical Fidelity · Functional / Task Success · Latency & Throughput · Reasoning & Prediction |

单个维度可以不选标签，但每篇论文的八个维度合计至少一个。标签描述研究焦点、实现机制或评测目标，不表示性能已经被本项目独立认证。尤其是 Physical Consistency 不等于物理正确性认证，Streaming Output 不等于实时交互，Multi-agent Methods 不等于世界中存在多个自主实体。

## 数据约束

每条正式记录包含 `classification`：

```json
{
  "area": "world-construction",
  "direction": "reconstruction",
  "tags": {
    "research_challenges": ["inverse-reconstruction"],
    "memory_state": [],
    "control_interaction": [],
    "representation_output": ["scene-program"],
    "methods_training": [],
    "runtime_efficiency": [],
    "world_setting_domain": [],
    "evaluation_focus": []
  },
  "basis": "primary-source review with documented evidence"
}
```

`area` 必须是单个字符串，不能是数组。`direction` 必须是所选主分类下的单个方向或 `null`。`tags` 必须包含八个维度数组，值不能重复，也不能使用其他维度的标签。构建校验会拒绝多主分类、方向与主类不匹配、未知标签、错误维度以及辅助标签全空的记录。

首轮 V2 迁移覆盖现有 58 条正式记录，依据是已维护的元数据、作者摘要与编辑说明，`basis` 记为 `existing_curated_metadata`。这次迁移不表示重新逐篇全文审核。原来的 `track`、`category`、`cross_categories` 和七个 `dimensions` 保留作为历史研究元数据；网站与 README 的主分类只使用 V2 的 `classification.area`。

## 网站检索

- 主分类使用同一组单选按钮。All 是浏览全部主类的入口，不是论文的主分类。
- 细方向为单选下拉框；选择细方向会同步其所属主分类。
- 辅助标签按八个维度折叠展示，支持多选，所有已选辅助标签取 AND 交集。收起面板后仍显示已选标签。
- 月份、标题／作者关键词、资源徽标与上述条件共同筛选。右侧月份数量按其他条件更新，手机上月份栏可横向滚动。
- 点击卡片上的主分类、细方向或辅助标签也可以筛选。卡片只显示一个主分类，更多辅助标签可展开查看。

链接示例：`?area=world-construction&direction=reconstruction&tags=physical-consistency&month=2026-10`。状态保存到地址栏，刷新和浏览器前进后退可以恢复；无效类别、方向和标签被忽略。原来十个大标签的 `topics` 参数已由 V2 的 `area`、`direction` 和 `tags` 取代。

## 维护与扩展

优先使用现有主类、细方向和辅助词表，修订记录时保留具体来源依据。若要增加辅助标签，先在对应维度定义，再使用到论文记录。主分类维持单一，跨方向联系通过辅助标签表达。README 的六个主分类章节各自只列所属论文；最近更新与阅读路径作为导航引用，不改变主分类归属。

原始来源核验和边界说明见 [Research notes](RESEARCH.md)，各 benchmark 的输入、产物、证据和限制见 [Benchmark Atlas](BENCHMARKS.md)。
