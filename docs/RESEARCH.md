# 核验记录与范围

来源核验日期：**2026-10-21**。本轮精修后目录共 **58** 条，包括 **53** 篇 arXiv 工作与 **5** 项官方报告／项目，保留首版全部 44 条。主要阅读粒度是 arXiv 元数据、摘要和官方项目说明；对部分基准阅读了全文中的任务与评测章节，未声称完成全部论文全文审核或独立实验复现。

## Benchmark 与基础组件补充

新增 14 项，建立 21 个具名 Benchmark 协议的横向索引。Video2World 和 3DCodeVerse 原已收录，本轮补充其代码／数据集链接、评测入口和数据规模说明，不重复添加。

| 新条目 | 已读取的一手来源 | 分类与核验重点 |
| --- | --- | --- |
| 4DCodeBench | [arXiv](https://arxiv.org/abs/2610.03715)、[README](https://github.com/4DCodeBench/4DCodeBench) | 100 真实＋100 合成视频；外观、几何、2D／3D 动态分开评分 |
| BVB / Blender-VideoBench | [arXiv](https://arxiv.org/abs/2609.15478)、[项目与协议](https://yoloytang.me/BVB/) | 288 室内视频；Dual VQA 测时空事实，Latent Similarity 测布局／运动；不是接触物理认证 |
| BlenderWorld | [arXiv](https://arxiv.org/abs/2610.23986)、[QwenLM README](https://github.com/QwenLM/BlenderWorld) | 223 任务、2,651 二元标准；可编辑 Blender 产物与真实参考 |
| PhysCodeGym | [arXiv](https://arxiv.org/abs/2610.17288)、[README](https://github.com/ShaoShuai0605/PhysCodeGym) | 156 任务，43 项带反事实检查；原生场景物理测量可发现视频外观掩盖的问题 |
| PhySimCode | [arXiv](https://arxiv.org/abs/2610.15722)、[README](https://github.com/SourajaKundu/PhySimCode) | 视频＋引擎名输入，规律、参数、代码输出；160,614 语料与 2,430 公开评测视频分开记录 |
| ExeWorldBench | [摘要](https://arxiv.org/abs/2610.15166)、[项目仓库](https://github.com/Helen1p/ExeWorldBench) | 单机制、机制组合、意图驱动世界合成；仓库主要是项目／数据入口，未把它认定为已发布完整评测代码 |
| Code4Scene | [全文任务／评测章节](https://arxiv.org/html/2609.36777v1)、[README](https://github.com/SimWorld-AI/Code4Scene) | 原生 Unreal 场景检查；论文 190 案例／95 公开，README 160 构建任务／20 Research Track，保留版本差异 |
| GPUPhysBench | [全文方法／评测章节](https://arxiv.org/html/2609.35639v1) | 50 GPU 物理实现任务；正确性与速度分开，未找到可靠官方代码链接 |
| 3DCodeBench | [arXiv](https://arxiv.org/abs/2606.01057)、[项目](https://www.3dcodebench.com/) | 程序化建模与 3DCodeArena 人类偏好；首次提交 2026-05-31，不用编号月份替代日期 |
| BlenderGym | [全文任务／评测章节](https://arxiv.org/html/2504.01786v1)、[README](https://github.com/richard-guyunqi/BlenderGym-Open) | 起始脚本和目标图像驱动的五类编辑，研究 generator／verifier 的推理扩展 |
| SceneCraft | [Blender code 版本摘要](https://arxiv.org/abs/2403.01248) | 2024 年前序工作；代码场景图、视觉修正、脚本库与视频生成控制 |
| WorldStream | [README](https://github.com/krennic999/WorldStream)、[系统设计博客](https://krennic999.github.io/WorldStream/blog/) | 分层语义计划＋本地程序化生成＋持久状态；当前 Code coming soon，博客更新日不当作首发日 |
| H3 Streaming VAE Decoder | [SolarX-Team README](https://github.com/SolarX-Team/H3-Streaming-VAE-Decoder)、[方法博客](https://solarx-team.github.io/H3-Streaming-VAE-Decoder/) | 无未来 latent 的解码与亮度修正；另外兼容 NVIDIA 蒸馏 decoder，自身不维护世界状态 |

3DCodeVerse 官方页将约 2.03M **code–condition pairs** 与 269,597 **executable programs** 区分，并说明 3DCodeBench 评测拆分保留。本目录采用这个口径，避免把 pair 数误写成独立程序数。

WorldStream 博客明确：模型输出结构化语义计划，行为执行由本地能力模块负责；并未声称实时合成任意物理或动画代码。预取和缓存支持持续探索，所报约 2.3 秒是 warm-cache 的 plan-to-scene 估计。与它同名的信号数据集、普通游戏地图插件及 LeRobot loader 不收入本条目。

H3 解码博客只明确到 2026 年 10 月，保留日级日期未知。其解码耗时从 latent 到达后计算，不能与 StreamRender-H3 的 diffusion step 或整条按键到显示链路混用。支持 NVIDIA 学生权重也不等于该仓库训练了同一个模型。

本轮检索使用 arXiv 的标题检索、两组扩展检索（分别最多 80、150 条）、前序工作的具名检索，以及 GitHub 官方仓库和项目页交叉核对。扩展检索不是穷尽目录：排除仅输出问答、纯视频扩散、一般软件编程和其他领域同名项。重要的未采纳例子包括 SceneBench 的空间问答、同名 SceneCraft 的 NeRF 路线，以及与代码世界表示无关的 WorldStream 信号编码论文。

## 用户提供的条目

| 输入简称 | 规范条目 / 核验来源 | 处理 |
| --- | --- | --- |
| Code World Model | [Coding Agent as World Brain](https://arxiv.org/abs/2608.25927) | 持续可交互世界 |
| SolarRenderer | [SolarRenderer](https://arxiv.org/abs/2610.28630) | 结构条件神经渲染 |
| streaming code world model | [Streaming Code World Model](https://github.com/TingtingLiao/streaming-code-world-model) | 社区流式扩展；项目型条目；非实时 |
| code video model | [Code Video Model](https://code-video-model.github.io/) | 官方技术报告；未找到对应 arXiv 时不编造编号 |
| Matrix-Game-4 | [Matrix-Game 4.0](https://arxiv.org/abs/2610.27999) | 核心：游戏引擎负责状态与规则 |
| streamrenderh3 | [StreamRender-H3 官方研究博客](https://nvlabs.github.io/Sana/Sol-Engine/StreamRender-H3/) | 用户补充官方链接后核验；不冒充独立 arXiv 论文 |
| Programmable World Model | [Programmable World Model](https://arxiv.org/abs/2609.10540) | 持续状态、可编程规则 |
| agentGarten | [AgentGarten](https://arxiv.org/abs/2610.12374) | 世界用于智能体学习 |
| WorldSolver | [WorldSolver](https://arxiv.org/abs/2610.08720) | 求解器生成；交叉关联评测 |
| Video2World | [Video2World](https://arxiv.org/abs/2610.04432) | 逆向理解与功能评测 |
| Text2Sim | [Text2Sim](https://arxiv.org/abs/2609.36593) | 可执行物理模拟生成 |
| Physis-Lang | [Physis-Lang](https://arxiv.org/abs/2609.40358) | 相邻物理语言路线 |
| worldagent | [WorldAgent](https://arxiv.org/abs/2609.33208) | 验证引导物理构建 |
| code plans, diffusion renders | [CoDeR](https://arxiv.org/abs/2609.26458) | 使用正式标题，保留 CoDeR 简称 |
| veriphy | [VeriPhy](https://arxiv.org/abs/2609.03153) | 物理证据与验证；排除同名通信／验证论文 |
| code2worlds-2 | [Code2Worlds-2](https://arxiv.org/abs/2610.17651) | 与第一版分别收录 |
| code as worlds | [Code as Worlds](https://arxiv.org/abs/2608.27549) | 可执行物理推理 |
| CWM | [CWM (Meta)](https://arxiv.org/abs/2510.02387) | 软件执行世界，正式标题保留 Open-Weights |
| swe-world | [SWE-World](https://arxiv.org/abs/2602.03419) | 软件执行环境的学习代理 |
| mpmworlds | [MPMWorlds](https://arxiv.org/abs/2606.01538) | 视频逆向物理与外推 |
| VideoCoCo | [VideoCoCo](https://arxiv.org/abs/2607.27380) | 前序代码预演与视频生成 |

## 额外补充

近期新增包括 [NeoWorld-3](https://arxiv.org/abs/2610.27690)、[CEGame-Bench](https://arxiv.org/abs/2610.26098)、[Modelica 系统辨识](https://arxiv.org/abs/2610.25019)、[3DCodeVerse](https://arxiv.org/abs/2610.22341)、[Mallea](https://arxiv.org/abs/2610.21283)、[RoboSimStudio](https://arxiv.org/abs/2610.18835) 和软件世界方向的 [ANTE](https://arxiv.org/abs/2610.15368)。

研究脉络还补充 Recursive Code World Models、GameDirector、VisualPatchWorld、SimWorlds、SceneCode、SimWorld Studio、GS-Agent、Code2Worlds、General Game Playing、Debugging Code World Models、World Programs、RoboGen、Holodeck、GIF-MCTS、PhysDreamer 和 FactorSim。所有条目的原始标题、首次提交日期和作者来自其 arXiv 记录。

没有把 EmbodiedEvo 仅凭 coding agent 关键词收入核心目录：其主要代码职责是控制策略与技能积累，而非构建世界或推断世界机制。没有将所有普通 3D／视频生成、机器人 code policy 和 Matrix-Game 早期版本自动纳入核心。

## 检索来源和边界

1. 阅读参考仓库及网页，关注问题驱动分类、月份导航与检索方式。
2. 通过 arXiv API 检索 Code World Model 及用户指定标题；扩大至 executable worlds、simulation、world programs、rendering 等邻近词。
3. 对近两周的 coding-agent / executable-world 结果进行人工筛查，并结合官方 GitHub 和项目页补核不在 arXiv 的作品。
4. 对没有可靠首发日期的官方项目保留 `published: null`。GitHub 仓库创建时间可能早于公开发布，不替代论文日期。已核验不代表已核验每一个字段。
5. 将每条记录的 `verification.source`、`basis`、`checked` 与每个资源链接的 `provenance` 写入数据；摘要可在网页详情中展开。

首轮近期广义查询按提交时间返回最新 80 条，命中范围停留在 10 月 13 日左右；其更早部分由命名检索和 Code World Model 检索补充。这不是全库穷尽搜索。后续每日爬虫会报告查询结果截断，并交给维护者复核覆盖率。

网页上的最近列表使用首次提交日期，避免把 arXiv ID 月份直接当成日期。尤其 CWM 的编号为 2510.02387，而元数据首次提交是 **2025-09-30**。

## 资源和声明的证据级别

- `primary_abstract`：身份、日期、作者及摘要已检查；机制标签是摘要层面的编辑判断。
- `official_project`：核对官方项目页／README 的内容与资源指向。
- `full_text`：阅读了全文中与分类有关的具体章节；本轮用于 BlenderGym、Code4Scene、GPUPhysBench 的任务与评价分析，不表示全文逐字审核或实验复现。

徽标只显示 `✅ Open Source` 和 `❌️ Not Open Source` 两种状态，不再标注代表作或设置特殊高亮。沿用目录的资源记录口径：前者表示已找到代码、权重、数据或官方项目页，后者表示已检查来源中暂未找到这类公开资源。“Paper / Code / Project / Data / Weights”链接分别显示实际资源类型；仅有论文链接不会得到 ✅。

上一轮从 arXiv 元数据的 comment 字段及已核验官方仓库补充 23 个资源链接，覆盖 SolarRenderer、Matrix-Game 4.0、AgentGarten、Video2World、Code as Worlds、VideoCoCo 等。当时 31 条记录有公开资源，13 条暂未找到。本轮继续补充新基准和数据链接；最新状态以每条记录的 `resource_status` 为准。

## 参考

- [Awesome Interactive World Model](https://github.com/EasonTuT/Awesome-Interactive-World-Model)
- [arXiv API 用户手册](https://info.arxiv.org/help/api/user-manual.html)
- [StreamRender-H3 官方博客](https://nvlabs.github.io/Sana/Sol-Engine/StreamRender-H3/)
- [Code Video Model 官方报告](https://code-video-model.github.io/tech_report.pdf)
