# 分类设计：Code World Model 与 Code as Model

这份目录以“代码在认识和构建世界中承担什么职责”为中心。分类单位是研究贡献，不是论文标题里的关键词。参考 Awesome Interactive World Model 的研究问题组织方式，进一步区分目标、机制和验证依据。

## 本轮判断与调整（2026-10-23）

**两条主线合理，九个研究问题可保留；原来的七个维度还不能称为严格正交。** 生成／理解按主要验证目标划分，比按“是否生成代码”划分更有解释力。`Worlds for agent learning` 属于用途导向的研究问题，与机制类别存在交叉，因此采用主贡献＋多标签，而不是互斥分类树。

- **研究问题、资源类型、比较维度分层。** Benchmark 与 Dataset 属于横向资源索引。`Verification & evaluation` 收窄为 `Executable verification`，只有验证方法本身构成贡献时才归入该类；普通 benchmark 不再自动交叉列入。
- **按评测目标归类。** CEGame-Bench 移到可玩世界，ExeWorldBench 移到物理模拟合成并交叉关联逆向重建；BlenderGym 的目标是图形编辑，移到场景与资产程序。具名 benchmark 协议及来源均保留。
- **交互和交付拆开。** `interaction` 描述能施加的编辑或动作，新增 `delivery` 描述流式观测或世界扩展。H3 VAE 可流式解码，但交互能力为不适用；Streaming CWM 仅确认流式交付，交互能力保留未明确。
- **保留证据边界。** 新维度从已有标签迁移，没有对其他论文重新开展全文核验；无已有流式标签的工作记为 `unknown`，不能据此推断为离线。`curated_at` 保留来源核验日期 2026-10-21。
- **澄清关联维度。** Code role 回答代码职责，Representation 回答信息载体，二者有关联但不是同一问题。Construction feedback 改名 Refinement signal，容纳原有 training 标签，同时明确训练目标不等于构建时反馈。

README 每项只在主研究清单中完整出现一次，网站保留交叉检索。评测协议移到独立 Atlas，README 用紧凑索引呈现。58 条记录全部保留。

## 1. 两条主线：按问题的方向分类

**Code World Model / 生成：** 从意图、任务或场景规格出发，构造可执行的状态、规则、物理过程或渲染条件。核心问题是“希望什么世界存在，怎样让它运行起来”。

**Code as Model / 理解：** 从图像、视频、轨迹、规则描述等证据出发，推断一个可执行解释，并通过预测、干预、规划或验证判断解释是否有用。核心问题是“什么机制能够解释观测”。

“生成代码”不自动意味着属于生成主线。Video2World、NeoWorld-3 和 Recursive Code World Models 都生成程序，但主要验证的是从视觉证据重建世界，因此归入理解。Code as Worlds 同时构造模拟器、进行物理推理并产生监督，其主分类是可执行物理推理，交叉关联逆向重建和模拟生成。

两条主线可形成闭环：生成程序 → 执行 → 观测 → 验证解释 → 修正程序。目录保留一个主分类和若干交叉类别，避免重复计算论文数。网页类别筛选包含交叉类别；主线筛选采用主贡献归属。

## 2. 细分类：每类对应一个研究瓶颈

| 主线 | 细分类 | 核心研究问题 | 代表工作 |
| --- | --- | --- | --- |
| 生成 | Scene & asset programs | 场景是否具有可编辑、可组合、可编译的结构？ | SceneCode、3DCodeVerse |
| 生成 | Physical simulation synthesis | 生成的是运动外观，还是可运行的物理机制？ | Code2Worlds、GS-Agent、SimWorlds、Text2Sim、WorldAgent、Code2Worlds-2 |
| 生成 | Persistent & playable worlds | 谁维护离屏状态、规则和动作的持续后果？ | Code World Model、Programmable World Model、CoDeR、Mallea、Matrix-Game 4.0 |
| 生成 | Code-guided video & rendering | 代码提供的结构怎样转为连续视觉观测？ | VideoCoCo、Code Video Model、SolarRenderer、Streaming CWM、StreamRender-H3 |
| 生成 | Worlds for agent learning | 世界能否作为训练环境，并随智能体能力发展？ | RoboGen、FactorSim、SimWorld Studio、AgentGarten |
| 理解 | Inverse world reconstruction | 哪个程序、参数和机制能够解释观测？ | MPMWorlds、Video2World、Recursive CWM、NeoWorld-3、RoboSimStudio |
| 理解 | Executable physical reasoning | 运行假设能否支持定量推理与预测？ | Code as Worlds、WorldSolver |
| 理解 | Rule induction & planning | 归纳出的状态转移模型是否有助于决策？ | World Programs、GIF-MCTS、General Game Playing、VisualPatchWorld |
| 理解 | Executable verification | 哪些可执行检查能接受、否定或限定一个世界假设？ | VeriPhy；交叉关联 WorldAgent、WorldSolver、PhysCodeGym、Code4Scene |

独立的 Related perspectives 保存软件执行世界模型、非可执行代码的物理表示，以及流式视频解码组件。H3 Streaming VAE Decoder 属于最后一类：它支持交互渲染，但自身没有世界状态与动作转移。

### 横向索引：Benchmark、数据与基础组件

两条主线回答研究目标，横向索引回答“这项工作提供了什么可比较、可复用的东西”。Benchmark 不是第三条生成／理解主线：Video2World 保持理解归属，BlenderWorld 保持生成归属，两者都能从基准入口找到。

| 基准组 | 主要证据 | 对应工作 |
| --- | --- | --- |
| Video reconstruction & inverse graphics | 观测中的几何、运动和时空事实是否保留 | 4DCodeBench、BVB、PhysCodeGym、Video2World |
| Procedural 3D creation & scene editing | 原生场景、空间关系、规格满足、未编辑内容保持 | BlenderGym、3DCodeBench、BlenderWorld、Code4Scene、Code4D、4DBuildBench |
| Physical mechanisms, parameters & solvers | 参数恢复、数值正确性、物理测量、反事实与外推 | PhySimCode、PhysCodeGym、WorldSolver、GPUPhysBench、MPMWorlds、ExeWorldBench |
| Executable interaction, state & intervention | 任务完成、机制组合、状态维持与编辑后的行为 | Video2World、ExeWorldBench、IGMBench、CEGame-Bench、SimCode4D、CombatStateBench、CWMB |
| Code-guided video generation | 可编程预演对视频构图和运动的控制 | CodeVideoBench |

完整的输入、产物、评分证据与边界见 [Benchmark Atlas](BENCHMARKS.md)。同一论文提出的基准以具名协议保存，如 Code2Worlds-2 → SimCode4D；不为每个别名单独增加论文计数。仅使用现成 benchmark 或报告实验指标，不足以自动认定提出了一个新 benchmark。

数据与组件再分为三组：**Executable code & simulation corpora**、**Construction & verification harnesses**、**Streaming worlds, renderers & decoders**。3DCodeVerse 主要是数据与 harness；3DCodeBench 是相关的评测工作。PhySimCode 的 160,614 条完整生成语料与公开的 2,430 条评测子集不能混为一个发布规模。

流式系统尤其需要分层：WorldStream 按需扩展程序化世界，StreamRender-H3 根据引擎条件生成像素，H3 Streaming VAE Decoder 把已生成 latent 解码为帧。前者的空间扩展在 `delivery` 维度记作 `world_streaming`，后两者的因果视频输出记作 `streaming`；不再混入 `interaction`。三者的速度指标对应不同阶段。

## 3. 八个比较维度

| 维度 | 应当回答的问题 | 典型取值 |
| --- | --- | --- |
| Code role | 代码具体负责什么？ | 场景构造、状态转移、物理求解、视觉代理、可执行假设、验证器、学习环境、被预测的执行对象 |
| World representation | 可检查的世界信息存在哪里？ | 场景程序、状态＋规则、物理程序＋参数、proxy 视频、世界转移程序、执行轨迹、语言 |
| Dynamics authority | 下一时刻状态由谁决定？ | 显式规则、数值引擎、混合机制、神经预测、无动力学模型、未明确 |
| Refinement signal | 什么信号用于修正程序或模型？ | 编译执行、视觉批评、物理检查、轨迹拟合、任务成功、训练目标；保留训练与构建时反馈的区别 |
| Interaction contract | 用户或智能体能改变什么？ | 离线回放、程序编辑、动作条件 rollout、闭环交互、不适用、未明确 |
| Delivery mode | 世界或观测怎样逐步交付？ | 因果观测流、按需世界扩展、未单独确认 |
| Evaluation target | 作者选择验证哪些能力？ | 能运行、视觉几何、物理一致、功能任务、延迟吞吐、推理预测 |
| Domain | 被模拟或解释的是哪类世界？ | 物理现象、具身机器人、游戏、视频、通用世界、计算软件环境 |

维度标签描述来源中的机制和评价目标。**Physical fidelity 标签不表示物理正确性已经得到认证。** 默认记录摘要或官方项目页可支持的信息，不把没有观察到的能力写成已具备。训练目标与构建时运行反馈也分开记录。

## 4. 目录应当揭示的几个问题

### 4.1 世界的状态和图像的记忆不是同一个问题

程序可以保证一个对象的生命值或位置持续存在，但不能单独保证神经渲染器再次看到该对象时保持相同外观。反过来，视频外观稳定也不能证明离屏状态、规则和因果后果正确。Mallea 的对象纹理记忆，以及 Programmable World Model 的非视觉状态，是理解两种持久性的重要对照。

### 4.2 可执行程序还可以分为“组织状态”与“解释机制”

运动脚本可以生成很好的时空控制信号，但其轨迹不一定来自接触、守恒或正确求解器。Code2Worlds → Code2Worlds-2 展现从视觉运动到碰撞、惯性、关节和模拟器闭环的变化。WorldSolver 进一步把求解器本身作为待生成对象。

### 4.3 神经渲染器不等于完整世界模型

SolarRenderer 的职责是把结构条件变成观测。应当追问与其连接的状态、物理和规则来自哪里。VideoCoCo、Code Video Model 主要提供离线预演与渲染路线；Programmable World Model、Matrix-Game 4.0 则强调持续状态或可玩交互。共享视频骨干不意味着具有同样的世界模型能力。

### 4.4 实时不能用一个 FPS 数字概括

必须注明分辨率、硬件数量、生成步数、chunk 长度，以及是否计入编码、解码、网络和缓冲。

- Streaming Code World Model 的 README 报告在一张 H200 上用 5.1 秒生成 0.71 秒 chunk，并明确尚未实时。
- StreamRender-H3 官方博客报告 8 张 GB200 上单个流式 diffusion render step 为 218 ms。该组件耗时不能直接与另一系统的按键到显示延迟比较。
- Matrix-Game 4.0 摘要分别报告单张 RTX 5090 的 480p / 60 FPS gameplay、112 ms key-press-to-display latency，以及另一配置下 83 FPS 稳态吞吐。它们保留各自测量语境。

这些是作者报告，未在本项目独立复现。

### 4.5 逆向问题需要不确定性与可辨识性

同一段视频可能对应多个可行参数或程序。能复现观察窗口不保证外推或干预正确。MPMWorlds 区分视觉参数推断和稳定外推；Modelica 工作说明低残差模型也可能违背能量约束；VeriPhy 保留证据不足时的 abstain。未来可以增设明确的 uncertainty 字段，但不能在首版凭空给所有论文打分。

### 4.6 世界必须通过它被构造来支持的任务来评价

Video2World 的功能正确性、CEGame-Bench 的真实输入通关测试，以及 AgentGarten 的学习用途，说明“看着像”“构建通过”和“能支撑任务”分别需要证据。目录以多维比较代替没有共同实验条件的总榜。

## 5. 名称边界与前序工作

- **Code World Model: Coding Agent as World Brain**：代码显式维护物理／交互世界；**CWM (Meta)**：模型学习预测软件执行世界。两者同名但研究对象不同。
- **Code2Worlds** 与 **Code2Worlds-2** 是不同工作；不要与 GUI 方向的 Code2World 混为一项。
- **Physis-Lang** 的核心表示是物理语言；放在相邻表示路线，不能仅因为使用 agent 就称为代码世界模型。
- **VideoCoCo** 首次提交于 2026-07-29，早于 Coding Agent as World Brain 的 2026-08-26。其 draft-conditioned 视频路线应保留。
- 更早的相关主线包括 World Programs（2019）、RoboGen（2023）、GIF-MCTS（2024）和 FactorSim（2024）。foundation 表示研究脉络，不构成首创或经典地位的判定。
- 本轮增加 SceneCraft（2024，Blender code 版本）、BlenderGym（2025）和 3DCodeBench（2026-05 首次提交）。SceneCraft 已将代码场景作为视频生成中间控制；它与同名 Layout-Guided 3D Scene Generation 论文是不同工作。
- Holodeck 和 PhysDreamer 为场景生成和逆物理提供参照，但未被标成代码转移函数生成方法。

## 6. 扩展规则

新类别必须对应现有维度无法表达的研究问题；新论文通常先使用已有类别。论文以主要实验目标决定主分类，其他能力采用交叉类别和维度。分类争议记录在 PR 中，附具体摘要、章节或官方文档依据。不得只依据标题自动把候选提升为正式收录。
