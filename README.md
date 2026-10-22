<div align="center">
<h1>📜 Awesome Code World Model</h1>
<p><b>Code World Model papers organized by core research challenges.</b></p>
<img src="site/banner.svg" width="100%" alt="Code World Model: code builds worlds; code explains worlds">
</div>

---

<table align="center" width="100%" border="0" cellspacing="0" cellpadding="0">
  <tr>
    <td align="center">✅ <b>Open Source</b></td>
    <td align="center">❌️ <b>Not Open Source</b></td>
  </tr>
</table>

`[YYYY-MM]` indicates the first submission month; unconfirmed dates appear as `[Date TBC]`.

**58 unique papers / projects · 22 flat topics** · Topic assignments reviewed **2026-10-22**.

📊 **[Benchmarks & Evaluation](#benchmarks)** · [Benchmark Atlas](docs/BENCHMARKS.md) · 🛠️ **[Datasets, Harnesses & Streaming Systems](#infrastructure)**

---

<a id="news-updates"></a>

## 🚩 News & Updates

Major collection updates and announcements. Scroll down for the complete topic list; use the website's month navigation for recent work.

🏷️ **[2026-10-22] Flat Topics & Per-paper Review** — Reviewed all 58 records against primary sources and reorganized the collection into 22 flat topics. Each paper has one README entry and may match several website topics. The website supports checkbox intersections with search and publication months. Assignment reasons and source-reading scope are recorded in the per-paper review.

📊 **[2026-10-21] Benchmark Atlas & Infrastructure** — Added 14 works across benchmarks, datasets and infrastructure. The Benchmark Atlas records inputs, executable artifacts, evaluation evidence and scope limits; data and harness resources are linked.

🔥 **[2026-10-21] Initial Collection** — 44 papers and projects covering Code World Model (generation) and Code as Model (understanding), including earlier foundations and the latest October releases.

🗂️ **[2026-10-21] Original Research Taxonomy (superseded)** — The initial categories and comparison dimensions were replaced by the flat topic scheme on 2026-10-22.

🤖 **[2026-10-21] Daily Discovery Prototype** — Daily arXiv and GitHub discovery is implemented as a candidate-review workflow. Automated promotion and a full literature-review agent remain future work.

💡 **[Ongoing] Community Contributions Welcome** — Suggest missing papers, earlier foundations, public resources, or classification corrections through an issue or PR. See [CONTRIBUTING.md](CONTRIBUTING.md).


---

## Browse by Topic

Each paper is listed **exactly once** below, under the topic that best describes its main contribution. The website uses the same flat vocabulary and allows each paper to appear under **multiple topics**. Select several website topics to find their intersection. Only topics with a designated README entry become headings here; all 22 topics remain available on the website.

- [General World Model](#general-world-model) (5)
- [Memory](#memory) (1)
- [Real-Time](#real-time) (1)
- [Acceleration](#acceleration) (1)
- [Streaming](#streaming) (2)
- [Physics](#physics) (3)
- [World Generation](#world-generation) (11)
- [World Reconstruction](#world-reconstruction) (3)
- [Neural Rendering](#neural-rendering) (2)
- [Planning](#planning) (4)
- [Agent Learning](#agent-learning) (4)
- [Code Execution](#code-execution) (1)
- [Post-Training](#post-training) (1)
- [Benchmark](#benchmark) (14)
- [Dataset](#dataset) (2)
- [Evaluation](#evaluation) (3)

[All 22 topic filters](https://awesome-cwm.github.io/Awesome-Code-World-Model/) · [Topic definitions](docs/TAXONOMY.md) · [Per-paper review and sources](docs/TOPIC_REVIEW.md)


---

<a id="general-world-model"></a>

## General World Model

Integrated world-model frameworks combining world state, evolution, interaction, or observations; a system-level scope, not a quality ranking.

[Browse all papers tagged General World Model →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=general-world-model)

[2026-10] ✅[Matrix-Game 4.0: Harnessing Video Models for Real-Time Playable Game Worlds](https://arxiv.org/abs/2610.27999) · [Project](https://matrix-game-v4-0.github.io/page/)

[2026-09] ✅[GameDirector: Decoupling Gameplay Logic from Rendering for Player-Configurable Game World Models](https://arxiv.org/abs/2609.25652) · [Project](https://jimntu.github.io/gamedirector/)

[2026-09] ✅[Code Plans, Diffusion Renders: Open-Ended Generative World Modeling](https://arxiv.org/abs/2609.26458) · [Project](https://becauseimbatman0.github.io/CoDeR)

[2026-09] ✅[Programmable World Model](https://arxiv.org/abs/2609.10540) · [Project](https://alaya-lab.github.io/pwm) · [Code](https://github.com/AlayaLab/pwm)

[2026-08] ✅[Code World Model: Coding Agent as World Brain](https://arxiv.org/abs/2608.25927) · [Code](https://github.com/buaacyw/code-world-model) · [Project](https://buaacyw.github.io/cwm/)


---

<a id="memory"></a>

## Memory

Persistent state, historical information, off-screen entities, identity, or memory consistency.

[Browse all papers tagged Memory →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=memory)

[2026-10] ✅[Mallea: Building, Steering, and Memorizing Worlds with Coding Agent](https://arxiv.org/abs/2610.21283) · [Project](https://lxycopper.github.io/Mallea)


---

<a id="real-time"></a>

## Real-Time

Reported real-time generation, simulation, or low-latency interaction, with the original hardware and timing conditions.

[Browse all papers tagged Real-Time →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=real-time)

[Date TBC] ✅[StreamRender-H3: Interactive Coding Worlds with Real-time Streaming Diffusion Render](https://nvlabs.github.io/Sana/Sol-Engine/StreamRender-H3/) · [Code](https://github.com/NVlabs/Sana/tree/sol-engine/models/streamrender_h3)


---

<a id="acceleration"></a>

## Acceleration

Reducing inference, execution, or rendering time and computational cost.

[Browse all papers tagged Acceleration →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=acceleration)

[2026-10] ✅[SolarRenderer: Few-Step Generative Reference Rendering](https://arxiv.org/abs/2610.28630) · [Project](https://enderfga.cn/SolarRenderer) · [Code](https://github.com/Enderfga/SolarRenderer)


---

<a id="streaming"></a>

## Streaming

Incremental input, continuous output, or causal chunk-by-chunk generation; not automatically real time.

[Browse all papers tagged Streaming →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=streaming)

[Date TBC] ✅[Streaming Code World Model](https://github.com/TingtingLiao/streaming-code-world-model) · [Weights](https://huggingface.co/Luffuly/streaming-code-world-model)

[Date TBC] ✅[H3 Streaming VAE Decoder: Training-Free Streaming without Future Latents](https://solarx-team.github.io/H3-Streaming-VAE-Decoder/) · [Code](https://github.com/SolarX-Team/H3-Streaming-VAE-Decoder)


---

<a id="physics"></a>

## Physics

Physical mechanisms, motion, contact, collisions, materials, or physical consistency.

[Browse all papers tagged Physics →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=physics)

[2026-09] ❌️[Physis-Lang: Self-Evolving Language as a Physical Representation for Video World Model](https://arxiv.org/abs/2609.40358)

[2026-08] ✅[Code as Worlds: Agentic Discovery of Executable World Representations for Physical Reasoning](https://arxiv.org/abs/2608.27549) · [Project](https://mirros-lab.github.io/code-as-world)

[2024-04] ✅[PhysDreamer: Physics-Based Interaction with 3D Objects via Video Generation](https://arxiv.org/abs/2404.13026) · [Project](https://physdreamer.github.io/)


---

<a id="world-generation"></a>

## World Generation

Creating scenes, assets, games, or simulation environments from desired specifications.

[Browse all papers tagged World Generation →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=world-generation)

[2026-10] ✅[Code2Worlds-2: Physically Plausible Agent Harness for Embodied World Simulation](https://arxiv.org/abs/2610.17651) · [Code](https://github.com/AIGeeksGroup/Code2Worlds-2) · [Project](https://aigeeksgroup.github.io/Code2Worlds-2)

[2026-09] ❌️[Text2Sim: Agentic Physics-Based Simulation Generation with Distilled Expertise](https://arxiv.org/abs/2609.36593)

[2026-09] ❌️[WorldAgent: Verification-Guided Agentic Physical World Construction](https://arxiv.org/abs/2609.33208)

[2026-07] ✅[GS-Agent: Creating 4D Physical Worlds With Generative Simulation](https://arxiv.org/abs/2607.21522) · [Project](https://umass-embodied-agi.github.io/gs-agent/)

[2026-07] ✅[SimWorlds: A Multi-Agent System for Dynamic 3D Scene Creation](https://arxiv.org/abs/2607.01766) · [Project](https://dynsimworlds.github.io)

[2026-05] ✅[SceneCode: Executable World Programs for Editable Indoor Scenes with Articulated Objects](https://arxiv.org/abs/2605.19587) · [Project](https://scene-code.github.io/)

[2026-02] ✅[Code2Worlds: Empowering Coding LLMs for 4D World Generation](https://arxiv.org/abs/2602.11757) · [Code](https://github.com/AIGeeksGroup/Code2Worlds) · [Project](https://aigeeksgroup.github.io/Code2Worlds)

[2024-09] ✅[FactorSim: Generative Simulation via Factorized Representation](https://arxiv.org/abs/2409.17652) · [Project](https://cs.stanford.edu/~sunfanyun/factorsim/)

[2024-03] ❌️[SceneCraft: An LLM Agent for Synthesizing 3D Scene as Blender Code](https://arxiv.org/abs/2403.01248)

[2023-12] ✅[Holodeck: Language Guided Generation of 3D Embodied AI Environments](https://arxiv.org/abs/2312.09067) · [Code](https://github.com/allenai/Holodeck) · [Project](https://yueyang1996.github.io/holodeck/)

[Date TBC] ✅[WorldStream: Building 3D Worlds as You Explore](https://krennic999.github.io/WorldStream/blog/) · [Project](https://github.com/krennic999/WorldStream) · [Project](https://krennic999.github.io/WorldStream/)


---

<a id="world-reconstruction"></a>

## World Reconstruction

Recovering scenes, physics, or rules from reference images, video, trajectories, or observations.

[Browse all papers tagged World Reconstruction →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=world-reconstruction)

[2026-10] ❌️[NeoWorld-3: From Pixels to Code-Defined Physical Worlds](https://arxiv.org/abs/2610.27690)

[2026-10] ✅[RoboSimStudio: An Interactive Toolkit for Human and Agent Rapid Real2Sim of Robot Manipulation Tasks](https://arxiv.org/abs/2610.18835) · [Project](https://robosimstudio.github.io)

[2026-09] ❌️[Recursive Code World Models: Building Complex Worlds through Recursive Scene Programs](https://arxiv.org/abs/2609.11499)


---

<a id="neural-rendering"></a>

## Neural Rendering

Neural image or video generation conditioned on code, executable state, geometry, or proxies.

[Browse all papers tagged Neural Rendering →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=neural-rendering)

[2026-07] ✅[VideoCoCo: Code-as-CoT for Physically-Consistent Video Generation via an Agentic Dual-Engine System](https://arxiv.org/abs/2607.27380) · [Code](https://github.com/micky-li-hd/VideoCoCo)

[Date TBC] ✅[Code Video Model](https://code-video-model.github.io/tech_report.pdf) · [Project](https://code-video-model.github.io/) · [Code](https://github.com/code-video-model/CodeVideoModel) · [Data](https://huggingface.co/datasets/code-video-model/CodeVideoBench)


---

<a id="planning"></a>

## Planning

Searching or imagining actions with world models to choose a plan.

[Browse all papers tagged Planning →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=planning)

[2026-07] ✅[VisualPatchWorld: Code World Models as Latent Structured Representations for Planning](https://arxiv.org/abs/2607.25236) · [Code](https://github.com/HKBU-KnowComp/VisualPatchWorld/)

[2025-10] ❌️[Code World Models for General Game Playing](https://arxiv.org/abs/2510.04542)

[2024-05] ✅[Generating Code World Models with Large Language Models Guided by Monte Carlo Tree Search](https://arxiv.org/abs/2405.15383) · [Project](https://sites.google.com/view/code-world-models/home)

[2019-12] ❌️[World Programs for Model-Based Learning and Planning in Compositional State and Action Spaces](https://arxiv.org/abs/1912.13007)


---

<a id="agent-learning"></a>

## Agent Learning

Using generated worlds, simulated experience, or world-model feedback to improve an acting or reasoning agent.

[Browse all papers tagged Agent Learning →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=agent-learning)

[2026-10] ✅[AgentGarten: Code Worlds for Evolving Agents](https://arxiv.org/abs/2610.12374) · [Project](https://mirros-lab.github.io/agent-garten)

[2026-05] ❌️[SimWorld Studio: Automatic Environment Generation with Evolving Coding Agent for Embodied Agent Learning](https://arxiv.org/abs/2605.09423)

[2026-02] ✅[SWE-World: Building Software Engineering Agents in Docker-Free Environments](https://arxiv.org/abs/2602.03419) · [Code](https://github.com/RUCAIBox/SWE-World)

[2023-11] ✅[RoboGen: Towards Unleashing Infinite Data for Automated Robot Learning via Generative Simulation](https://arxiv.org/abs/2311.01455) · [Code](https://github.com/Genesis-Embodied-AI/RoboGen) · [Project](https://robogen-ai.github.io/)


---

<a id="code-execution"></a>

## Code Execution

Modeling execution semantics, predicting computational states, or investigating execution correctness; not every method that runs code.

[Browse all papers tagged Code Execution →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=code-execution)

[2025-09] ✅[CWM: An Open-Weights LLM for Research on Code Generation with World Models](https://arxiv.org/abs/2510.02387) · [Code](https://github.com/facebookresearch/cwm)


---

<a id="post-training"></a>

## Post-Training

Fine-tuning, reinforcement learning, distillation, or adaptation of existing models.

[Browse all papers tagged Post-Training →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=post-training)

[2026-10] ❌️[ANTE: Anticipate, Then Execute -- Learning Internal World Models for Coding Agents from Verified Beliefs](https://arxiv.org/abs/2610.15368)


---

<a id="benchmark"></a>

## Benchmark

Reusable test tasks and scoring protocols; a method-side benchmark does not automatically become the README category.

[Browse all papers tagged Benchmark →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=benchmark)

[2026-10] ❌️[From Code to Playable Systems: CEGame-Bench for Long-Horizon Game Creation Agents](https://arxiv.org/abs/2610.26098)

[2026-10] ✅[BlenderWorld: Benchmarking Visual Agents for 3D Creation from Real-World References](https://arxiv.org/abs/2610.23986) · [Code](https://github.com/QwenLM/BlenderWorld) · [Project](https://blenderworld.github.io/) · [Data](https://huggingface.co/datasets/Qwen/BlenderWorld)

[2026-10] ✅[PhysCodeGym: Benchmarking Coding Agents for Physically Verifiable 4D Reconstruction](https://arxiv.org/abs/2610.17288) · [Code](https://github.com/ShaoShuai0605/PhysCodeGym) · [Data](https://huggingface.co/datasets/ShaoShuai0605/PhysCodeGym)

[2026-10] ✅[PhySimCode: A Benchmark and Evaluation Method for Physics Video to Code Generation](https://arxiv.org/abs/2610.15722) · [Code](https://github.com/SourajaKundu/PhySimCode) · [Project](https://sourajakundu.github.io/PhySimCode/) · [Data](https://huggingface.co/datasets/SourajaKundu123/PhySimCode)

[2026-10] ✅[ExeWorldBench: Benchmarking Code-Based Executable 3D World Modeling](https://arxiv.org/abs/2610.15166) · [Project](https://helen1p.github.io/ExeWorldBench/) · [Project](https://github.com/Helen1p/ExeWorldBench) · [Data](https://huggingface.co/datasets/HelenPeng/ExeWorldBench)

[2026-10] ✅[WorldSolver: Can LLM Agents Simulate the Physical Dynamics via Solver Generation?](https://arxiv.org/abs/2610.08720) · [Code](https://github.com/sirujiang/WorldSolver)

[2026-10] ✅[Video2World: Benchmarking Coding Agents for Interactive World Modeling from Embodied Videos](https://arxiv.org/abs/2610.04432) · [Project](https://aetherlabsai.github.io/Video2World) · [Code](https://github.com/AetherLabsAI/Video2World) · [Data](https://huggingface.co/datasets/AetherLabs-AI/Video2World)

[2026-10] ✅[4DCodeBench: Benchmarking Agents on Inverse Graphics of Dynamic Scenes](https://arxiv.org/abs/2610.03715) · [Code](https://github.com/4DCodeBench/4DCodeBench) · [Project](https://4dcodebench.com/) · [Data](https://huggingface.co/datasets/4DCodeBench/Dataset-Real-World) · [Data](https://huggingface.co/datasets/4DCodeBench/Dataset-Synthetic)

[2026-10] ✅[World Editing: Intervening on Executable Worlds at Increasing Depth](https://arxiv.org/abs/2610.02331) · [Code](https://github.com/vinesmsuic/IGMWorld/) · [Project](https://vinesmsuic.github.io/IGMWorld/)

[2026-09] ✅[Code4Scene: Benchmarking Coding Agents for Constructing and Editing 3D Scenes](https://arxiv.org/abs/2609.36777) · [Code](https://github.com/SimWorld-AI/Code4Scene) · [Project](https://simworld-ai-code4scene.static.hf.space)

[2026-09] ❌️[GPUPhysBench: Benchmarking Coding Agents for Correct and Efficient GPU Physics Simulation](https://arxiv.org/abs/2609.35639)

[2026-09] ✅[BVB: Benchmarking Agentic Video Understanding via Programmatic Reconstruction in Blender](https://arxiv.org/abs/2609.15478) · [Code](https://github.com/yunlong10/BVB) · [Project](https://yoloytang.me/BVB/)

[2026-05] ✅[3DCodeBench: Benchmarking Agentic Procedural 3D Modeling Via Code](https://arxiv.org/abs/2606.01057) · [Code](https://github.com/gaoypeng/3dcodebench) · [Project](https://www.3dcodebench.com/) · [Data](https://huggingface.co/datasets/YipengGao/3DCode)

[2025-04] ✅[BlenderGym: Benchmarking Foundational Model Systems for Graphics Editing](https://arxiv.org/abs/2504.01786) · [Code](https://github.com/richard-guyunqi/BlenderGym-Open) · [Project](https://blendergym.github.io/) · [Data](https://huggingface.co/datasets/richard-guyunqi/BG_bench_data)


---

<a id="dataset"></a>

## Dataset

Constructed or published world programs, scenes, trajectories, simulations, or paired data resources. Public release scope is recorded separately.

[Browse all papers tagged Dataset →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=dataset)

[2026-10] ✅[3DCodeVerse: Exploring 3D Worlds as Code](https://arxiv.org/abs/2610.22341) · [Project](https://3dcodeverse.com/) · [Code](https://github.com/gaoypeng/3dcodeverse) · [Data](https://huggingface.co/datasets/ilabai/3dcodeverse)

[2026-06] ✅[MPMWorlds: Material-Point-Method Simulations for Inferring and Extrapolating Physical Dynamics](https://arxiv.org/abs/2606.01538) · [Project](https://zzigak.github.io/mpmworlds/)


---

<a id="evaluation"></a>

## Evaluation

Focused evaluation, diagnosis, and analysis of capabilities, evidence, or failure modes.

[Browse all papers tagged Evaluation →](https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=evaluation)

[2026-10] ❌️[LLM Agents as Suppliers of Physical System Models: Calibration and Acceptance in Modelica](https://arxiv.org/abs/2610.25019)

[2026-09] ❌️[VeriPhy: Agentic Physical Reasoning for World Model Evaluation and Refinement](https://arxiv.org/abs/2609.03153)

[2026-02] ❌️[Debugging code world models](https://arxiv.org/abs/2602.07672)


---

<a id="benchmarks"></a>

## Benchmarks & Resources

[Benchmark Atlas](docs/BENCHMARKS.md) compares inputs, executable artifacts, evaluation evidence, and limitations. Named suites within method papers, such as CombatStateBench and SimCode4D, remain associated with their original paper; they are not duplicate paper records.

<a id="infrastructure"></a>
Datasets, execution harnesses, rendering components, and streaming systems are included in the topic list above. Supporting components remain distinguished in the source metadata and editorial descriptions.

## Reading & Review

The [topic guide](docs/TAXONOMY.md) explains the vocabulary. The [per-paper review](docs/TOPIC_REVIEW.md) records the single README placement, overlapping website topics, primary sources, and unresolved details for every record. The review uses author abstracts, official project documentation, and selected method or evaluation sections; it is not an independent reproduction.

For new work, use the website's publication-month navigation. Each paper has one bibliography entry in this README; recent-paper and reading-path lists are kept out of the README to preserve that rule.

<a id="citation"></a>

## Citation

Please cite the original papers. Download [all BibTeX entries](site/papers.bib) and use the entries for the papers you reference.

## Contributing & Maintenance

See [CONTRIBUTING.md](CONTRIBUTING.md) to suggest a paper or correction. [Research notes](docs/RESEARCH.md) document the original scope and identity checks.

`data/papers.json` is the single source of truth. `data/taxonomy.json` defines the flat topics; `classification.readme_topic` gives one README placement, while `classification.topics` gives all reviewed website topics. Source links and reasons are stored with each assignment. The README, website data, review report, and exports are generated together.

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 -m http.server 8000 --directory site
```

Open `http://localhost:8000`, or open `site/index.html` directly. [GitHub Pages deployment](docs/DEPLOYMENT.md) · [Daily discovery prototype](docs/CRAWLER_HANDOFF.md) · [JSON](data/papers.json) · [CSV](site/papers.csv).

The daily discovery prototype proposes candidates for review. It does not silently promote papers into the curated list.

## Acknowledgments & License

The simple list and topic naming draw inspiration from [Awesome Interactive World Model](https://github.com/EasonTuT/Awesome-Interactive-World-Model); compound indexing also draws inspiration from [Awesome 3D Gaussian Splatting](https://mrnerf.github.io/awesome-3D-gaussian-splatting/). The flat topic scheme follows the maintainer's direction. Metadata, editorial decisions, and implementation are maintained independently.

Repository code and original editorial content: [MIT](LICENSE). Paper titles, abstracts, and external resources remain attributable to their respective authors and providers.
