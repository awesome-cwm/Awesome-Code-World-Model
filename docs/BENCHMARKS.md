# Benchmark Atlas / 基准索引

基准按任务、提交产物、评分证据与适用边界比较。任务设定与评测对象不同，分数不能跨基准直接排名。同一论文的配套 benchmark 作为具名协议索引，不重复计为新论文。

## Video reconstruction & inverse graphics

What observable scene structure and motion survive video-to-code reconstruction?

| Benchmark / Paper | Input | Submitted artifact | Evaluation evidence | Boundary / version |
| --- | --- | --- | --- | --- |
| [PhysCodeGym](https://github.com/ShaoShuai0605/PhysCodeGym) | 156 videos across rigid, liquid, deformable and wind-driven motion | Executable Blender simulation | Visual metrics, object/event rubrics, native physical measurements; 43 tasks with counterfactual checks | Counterfactual coverage is a subset, not a guarantee over arbitrary interventions. |
| [Video2World](https://aetherlabsai.github.io/Video2World) | 222 reconstruction instances from 189 embodied videos | Simulation scene + physical settings + robot behavior | Geometric fidelity, dynamic fidelity and functional task correctness | A visually accurate reconstruction can still fail the manipulation task. |
| [4DCodeBench](https://github.com/4DCodeBench/4DCodeBench) | 100 real + 100 synthetic videos | Executable dynamic graphics program | Appearance, 2D/3D geometry and motion; synthetic reference-world comparisons | Matching observed dynamics does not uniquely identify the governing mechanism. |
| [BVB / Blender-VideoBench](https://yoloytang.me/BVB/) | 288 indoor videos; agent sees video frames only | Animated Blender scene + camera | Dual VQA for retained facts; V-JEPA latent similarity for layout/motion | Video reconstruction scores do not establish contact physics or embodied task success. |

## Procedural 3D creation & scene editing

Does the delivered native scene satisfy the reference and preserve the intended structure?

| Benchmark / Paper | Input | Submitted artifact | Evaluation evidence | Boundary / version |
| --- | --- | --- | --- | --- |
| [BlenderWorld](https://github.com/QwenLM/BlenderWorld) | 223 tasks with text, images, videos and optional specifications | Editable .blend plus requested exports | 2,651 binary rubrics + multi-view holistic visual ratings | Broad creation coverage; not a dedicated dynamics or closed-loop physics benchmark. |
| [Code4Scene](https://arxiv.org/html/2609.36777v1) | Paper: 190 construction/editing cases, 95 public; repository: 160 construction tasks | Engine-native Unreal scene (.umap) | Task fulfillment, artifact integrity, static physical validity, repair and preservation | Paper and repository currently describe different releases; do not mix their sizes or leaderboard scores. |
| [4DBuildBench](https://arxiv.org/abs/2607.01766) | Text prompts for dynamic procedural scenes | Editable Blender 4D scene | Visual fidelity and physical consistency | Text-to-world construction, not inverse reconstruction from source video. |
| [3DCodeBench / 3DCodeArena](https://www.3dcodebench.com/) | Text and image references | Procedural 3D modeling code | Execution and 3D output quality; pairwise human preference in 3DCodeArena | Static asset quality does not by itself establish executable physical dynamics. |
| [Code4D](https://arxiv.org/abs/2602.11757) | Text descriptions of 4D worlds | Generated scene code with scripted dynamics | Scene generation quality, richness and dynamic fidelity | Visual motion critique is not equivalent to simulator-enforced contact physics. |
| [BlenderGym](https://arxiv.org/html/2504.01786v1) | Starting scene script + start/goal images; five editing families | Edited Blender Python script | Image/perceptual metrics and geometry distances against the target | Graphics editing and verifier scaling; not a video-to-physical-simulation benchmark. |

## Physical mechanisms, parameters & solvers

Does code recover the mechanism, satisfy physical checks and generalize beyond the observed motion?

| Benchmark / Paper | Input | Submitted artifact | Evaluation evidence | Boundary / version |
| --- | --- | --- | --- | --- |
| [PhysCodeGym](https://github.com/ShaoShuai0605/PhysCodeGym) | 156 videos across rigid, liquid, deformable and wind-driven motion | Executable Blender simulation | Visual metrics, object/event rubrics, native physical measurements; 43 tasks with counterfactual checks | Counterfactual coverage is a subset, not a guarantee over arbitrary interventions. |
| [PhySimCode](https://github.com/SourajaKundu/PhySimCode) | 2,430 evaluation videos + engine identifier; 162 phenomena | Physical-law/parameter explanation + runnable Python | Law correctness/equivalence, execution, parameter recovery and regenerated video similarity | The full described corpus has 160,614 samples; the linked release is the evaluation subset. |
| [ExeWorldBench](https://arxiv.org/abs/2610.15166) | Visual mechanisms, composed systems and high-level physical goals | Code-based executable 3D world | Mechanism, compositional and intent-driven executability | These three task levels assess more than render similarity; detailed scoring must follow the source protocol. |
| [WorldSolver](https://arxiv.org/abs/2610.08720) | 168 tasks from 61 graphics papers across seven physical domains | Solver code completed inside a fixed scaffold | Execution checks, visual fidelity and physical plausibility | Solver completion assumes a supplied environment; it is not unrestricted world reconstruction. |
| [GPUPhysBench](https://arxiv.org/html/2609.35639v1) | 50 specified GPU physics operators/simulators | GPU solver implementation | Numerical acceptance checks + runtime relative to expert implementations | Measures implementation correctness and efficiency, not physical-law discovery from observations. |
| [4DBuildBench](https://arxiv.org/abs/2607.01766) | Text prompts for dynamic procedural scenes | Editable Blender 4D scene | Visual fidelity and physical consistency | Text-to-world construction, not inverse reconstruction from source video. |
| [MPMWorlds](https://arxiv.org/abs/2606.01538) | 2D MPM simulation videos with varying physical side information | Inferred simulation code or video-model continuation | Parameter/geometry inference and future physical extrapolation | Inference and extrapolation are distinct; the comparisons concern the stated 2D MPM setting. |

## Executable interaction, state & intervention

Can the world complete tasks, preserve state and behave correctly after an edit?

| Benchmark / Paper | Input | Submitted artifact | Evaluation evidence | Boundary / version |
| --- | --- | --- | --- | --- |
| [CEGame-Bench](https://arxiv.org/abs/2610.26098) | Design document + empty project across five production engines | Complete executable game | Real-input play, gameplay completion, integration and saved-world behavior | A successful build or high integration score is insufficient for completion. |
| [SimCode4D](https://arxiv.org/abs/2610.17651) | Five embodied task templates | MuJoCo-loadable scene with contacts, joints and physical attributes | State-based physical and robot-interaction evaluation | Simulator compatibility should be separated from rendered appearance. |
| [ExeWorldBench](https://arxiv.org/abs/2610.15166) | Visual mechanisms, composed systems and high-level physical goals | Code-based executable 3D world | Mechanism, compositional and intent-driven executability | These three task levels assess more than render similarity; detailed scoring must follow the source protocol. |
| [Video2World](https://aetherlabsai.github.io/Video2World) | 222 reconstruction instances from 189 embodied videos | Simulation scene + physical settings + robot behavior | Geometric fidelity, dynamic fidelity and functional task correctness | A visually accurate reconstruction can still fail the manipulation task. |
| [IGMBench](https://vinesmsuic.github.io/IGMWorld/) | 110 Minecraft/Terraria editing tasks at four intervention depths | Executable game modification | Build/load, behavior, preservation and visual checks; over 1.1K criteria | Successful loading does not imply correct behavior or preservation of unaffected state. |
| [CombatStateBench](https://arxiv.org/abs/2609.10540) | Programmable combat worlds | State-driven interactive visual world | Entity count and state accuracy | Count/state fidelity does not exhaust general world intelligence or physical correctness. |
| [Code World Models Benchmark (CWMB)](https://arxiv.org/abs/2405.15383) | 18 RL environments with descriptions and curated trajectories | Python transition/world model | Program synthesis and downstream model-based planning | Transition-model utility is evaluated separately from visual rendering. |

## Code-guided video generation

How well does the rendered video follow the code-built spatial and temporal plan?

| Benchmark / Paper | Input | Submitted artifact | Evaluation evidence | Boundary / version |
| --- | --- | --- | --- | --- |
| [CodeVideoBench](https://code-video-model.github.io/) | Complex video-generation requests | Code-built previs followed by diffusion video | Composition, motion and spatiotemporal control in generated video | Video-generation evaluation does not establish a persistent interactive state machine. |

## 阅读建议

BVB → 4DCodeBench → PhysCodeGym → Video2World：依次关注时空事实、动态几何、物理机制与干预、具身任务。这个顺序是阅读路线，不是作者之间的继承关系。

BlenderGym → 3DCodeBench → BlenderWorld / Code4Scene：从受约束的目标匹配，走向程序化资产、开放创作和原生场景状态检查。3DCodeVerse 在这条线上提供数据与 harness；使用 3DCodeBench 评测不等于二者是同一 benchmark。

WorldSolver 与 GPUPhysBench 关注求解器实现；PhySimCode 还要求从视频识别规律和参数；ExeWorldBench 关注机制组合能否实际运行。

Code4Scene 的 arXiv 论文与仓库 README 当前描述不同版本，表内分别保留。PhySimCode 的完整生成语料规模和公开评测子集规模也分别记录。每项来源链接与核验日期保存在统一文献数据中。
