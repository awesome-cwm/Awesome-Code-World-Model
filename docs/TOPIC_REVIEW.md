# Per-paper Topic Review

Every record was individually checked against the primary sources linked below. README placement is an editorial choice based on the main contribution; website topics overlap. Reading scope is stated per source. No independent reproduction is claimed.

The topic vocabulary is defined in [the topic guide](TAXONOMY.md). Reasons and source links are also available in `data/papers.json`.

## SolarRenderer

- **Record:** `solarrenderer`
- **Reviewed:** 2026-10-22
- **README:** Acceleration
- **Website:** Neural Rendering, Acceleration, Real-Time, Streaming, Post-Training, Dataset
- **Placement reason:** The main contribution is efficient reference rendering; it does not supply the world's transition dynamics.

**Topic evidence**

- **Neural Rendering:** Converts engine or simulator structure into realistic video through a structure-conditioned generative renderer.
- **Acceleration:** Four-step structure-guided distribution matching reports a 12.3-fold speedup over fifty-step sampling.
- **Real-Time:** Section 3.4 reports up to 28 FPS for the causal 768p renderer with a streaming decoder.
- **Streaming:** Block-causal generation outputs each block immediately and updates a bounded history cache.
- **Post-Training:** Separate control and acceleration LoRAs adapt and distill a pretrained frozen video backbone.
- **Dataset:** Contributes a frame-aligned corpus of 136K clips and links its dataset release.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.28630) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.
- [Source 2](https://arxiv.org/html/2610.28630v1) — `full_text`. Read sections 3.3–3.4, data construction, implementation and throughput evidence.

**Limits / unresolved details**

- The 28 FPS claim concerns the causal renderer; it is not an end-to-end user-input latency measurement. Hardware was not specified beside that claim in the read section.

## NeoWorld-3

- **Record:** `neoworld-3`
- **Reviewed:** 2026-10-22
- **README:** World Reconstruction
- **Website:** World Reconstruction, Physics, Interactive
- **Placement reason:** The central task is recovering operational physical worlds from observations, with interaction readiness beyond visual resemblance.

**Topic evidence**

- **World Reconstruction:** Recovers articulated objects and compositional 3D scenes from visual observations as tunable programs.
- **Physics:** The reconstruction engine includes differentiable parameter refinement and physical validation for simulation-ready twins.
- **Interactive:** The resulting worlds support physical manipulation, validated by zero-shot transfer of trajectories to a real dual-arm robot.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.27690) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.

## Matrix-Game 4.0

- **Record:** `matrix-game-4`
- **Reviewed:** 2026-10-22
- **README:** General World Model
- **Website:** General World Model, Interactive, Memory, Real-Time, Acceleration, Streaming, Action Control, World Generation, World Editing, Neural Rendering, Post-Training
- **Placement reason:** README placement emphasizes the integrated playable-world system; website topics expose its substantive control, memory and rendering components.

**Topic evidence**

- **General World Model:** Integrates a persistent game engine, a coding agent and a neural renderer into a complete playable-world framework.
- **Interactive:** Player inputs change engine state and rules before updated observations are displayed.
- **Memory:** Uses persistent engine state and retrieved spatial-memory reference frames to preserve revisited scenes.
- **Real-Time:** Reports 480p 60 FPS gameplay and 112 ms key-to-display latency on one RTX 5090.
- **Acceleration:** Few-step distillation, fused kernels and inference optimizations reduce rendering cost.
- **Streaming:** A causal renderer emits four-frame chunks while retaining a bounded clean-history cache.
- **Action Control:** Keyboard actions drive the demonstrated shooter and driving games.
- **World Generation:** A coding agent creates scenes and gameplay from player requests.
- **World Editing:** Natural-language requests modify existing scenes and game mechanics.
- **Neural Rendering:** Renders engine low-poly proxies as detailed visual observations.
- **Post-Training:** Fine-tunes a pretrained video model and performs staged causal consistency and distribution-matching distillation.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.27999) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.
- [Source 2](https://arxiv.org/html/2610.27999v1) — `full_text`. Read roadmap, sections 4–5, memory conditioning and evaluation; training uses one model per game.

**Limits / unresolved details**

- General World Model denotes an integrated framework, not universal zero-shot gameplay: section 4.2 trains one renderer per game.
- No Long Video Generation tag: sustained gameplay is motivated, but a distinct long-duration video evaluation was not found in the read sections.

## CEGame-Bench

- **Record:** `cegame-bench`
- **Reviewed:** 2026-10-22
- **README:** Benchmark
- **Website:** Benchmark, World Generation, Interactive
- **Placement reason:** This is a benchmark of executable playable-world creation, rather than a general world model or long-video method.

**Topic evidence**

- **Benchmark:** Introduces complete-game creation tasks and hidden real-input evaluators across five production game engines.
- **World Generation:** Agents must construct complete games from empty projects and design documents.
- **Interactive:** The central acceptance criterion is actual playable behavior, completion and saved-world return under real player inputs.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.26098) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.

## Physical System Models in Modelica

- **Record:** `modelica-agents`
- **Reviewed:** 2026-10-22
- **README:** Evaluation
- **Website:** Evaluation, Physics, World Reconstruction
- **Placement reason:** The principal scientific contribution is the analysis of model acceptance, non-identifiability and interpretability, so README placement is Evaluation.

**Topic evidence**

- **Evaluation:** Studies what behavioral acceptance, physical invariants and expert inspection certify about agent-produced physical models.
- **Physics:** Uses Modelica physical systems and an energy-balance check that rejects an energy-creating fitted model.
- **World Reconstruction:** Agents identify and calibrate executable device models from descriptions and measured responses.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.25019) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.
- [Source 2](https://arxiv.org/html/2610.25019v1) — `full_text`. Read introduction, task/protocol, discussion and section 7: fitting measurements does not certify structure, physics or adaptability.

**Limits / unresolved details**

- This is an empirical calibration and acceptance study, not a newly introduced standardized public benchmark.

## Mallea

- **Record:** `mallea`
- **Reviewed:** 2026-10-22
- **README:** Memory
- **Website:** General World Model, Memory, Interactive, World Generation, World Editing, Neural Rendering, Action Control
- **Placement reason:** Object-aware appearance memory is a distinctive research focus and provides the single README home; the website also records construction and editing.

**Topic evidence**

- **General World Model:** Combines world construction, executable transitions, intervention and generative observations in one object-centered framework.
- **Memory:** Introduces object texture memory indexed by persistent identities and validated against appearance-related state.
- **Interactive:** Optional user actions steer the running world and text requests intervene during execution.
- **World Generation:** A coding agent constructs object representations, attributes and behavior rules from text.
- **World Editing:** Runtime edits extend fields and rules while preserving unrelated state and object identities.
- **Neural Rendering:** A generative renderer combines current geometry with state-compatible remembered appearance.
- **Action Control:** The transition formulation accepts user actions that change the executable world alongside textual edits.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.21283) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.
- [Source 2](https://arxiv.org/html/2610.21283v1) — `full_text`. Read sections 3.1–3.4, qualitative results and conclusion; object texture validity and runtime revision checks are specified.

**Limits / unresolved details**

- Only qualitative examples are currently presented; memory ablations and long-horizon revisit benchmarks are announced for later release.
- No Real-Time or Long Video Generation tag: the read paper does not establish measured real-time performance or a demonstrated long-duration video result.

## 3DCodeVerse

- **Record:** `3dcodeverse`
- **Reviewed:** 2026-10-22
- **README:** Dataset
- **Website:** Dataset, World Generation, Post-Training
- **Placement reason:** The large 3D-code corpus is the most useful unique README placement; harness generation and post-training are additional substantial contributions.

**Topic evidence**

- **Dataset:** Introduces a large packaged corpus of executable 3D programs with conditions, assets and verification records.
- **World Generation:** Its harness creates and refines objects, articulated assets, scenes and graphics through 3D code.
- **Post-Training:** Studies LoRA supervised fine-tuning and execution/geometry preference optimization on the curated corpus.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.22341) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.
- [Source 2](https://arxiv.org/html/2610.22341v1) — `full_text`. Read dataset structure, section 5.2 and appendix post-training results, distinguishing programs from condition–code pair counts.

**Limits / unresolved details**

- The harness uses several coding agents; that does not warrant Multi-Agent, which is reserved for agents interacting inside a simulated world.
- No separate Benchmark tag: 3DCodeBench is a held-out evaluation suite and a separate catalog paper, rather than the main contribution here.

## BlenderWorld

- **Record:** `blenderworld`
- **Reviewed:** 2026-10-22
- **README:** Benchmark
- **Website:** Benchmark, World Generation, World Reconstruction, World Editing
- **Placement reason:** The contribution is a reference-driven 3D creation benchmark spanning creation, reconstruction and modification.

**Topic evidence**

- **Benchmark:** Provides 223 realistic 3D production briefs and 2,651 binary rubrics with a unified artifact evaluation protocol.
- **World Generation:** Includes reference-based design of new 3D objects, layouts and scenes.
- **World Reconstruction:** Tasks require structural reproduction of image, video and other real-world references.
- **World Editing:** Explicitly covers modification of 3D content as well as reconstruction and reference-based design.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.23986) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.
- [Source 2](https://arxiv.org/html/2610.23986v1) — `full_text`. Read task coverage and benchmark construction; section 2 explicitly lists reconstruction, modification and reference-based design.

**Limits / unresolved details**

- Interactive and parametric evaluation is listed as future work; do not tag Interactive solely because the deliverables are editable Blender files.

## RoboSimStudio

- **Record:** `robosimstudio`
- **Reviewed:** 2026-10-22
- **README:** World Reconstruction
- **Website:** World Reconstruction, Physics, Interactive, World Editing
- **Placement reason:** The central workflow is interactive physical Real2Sim calibration, rather than general-purpose scene generation.

**Topic evidence**

- **World Reconstruction:** Refines robot-manipulation simulations until their behavior matches observed real-world demonstrations.
- **Physics:** Exposes and couples contact models, solver choices, stiffness, friction and deformable-body dynamics.
- **Interactive:** Humans directly manipulate simulations and receive visual or force feedback within the Real2Sim loop.
- **World Editing:** A shared scene representation allows humans and coding agents to change solvers, contacts, materials and layouts.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.18835) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.
- [Source 2](https://arxiv.org/html/2610.18835v2) — `full_text`. Read sections 1, 3 and case studies: scene-level physics choices remain explicit and editable without rewriting the task.

## Code2Worlds-2

- **Record:** `code2worlds-2`
- **Reviewed:** 2026-10-22
- **README:** World Generation
- **Website:** World Generation, Physics, Interactive, Benchmark
- **Placement reason:** The main method creates simulation-ready worlds, so its unique README home remains World Generation; the new state-based SimCode4D protocol also warrants a website Benchmark topic.

**Topic evidence**

- **World Generation:** Turns text-generated 4D scenes into MuJoCo-loadable embodied simulation environments.
- **Physics:** Adds collision geometry, physical attributes, contact dynamics and simulator-driven refinement.
- **Interactive:** Targets robot-interactable scenes and verifies reachability, contacts and articulated interaction readiness.
- **Benchmark:** Introduces SimCode4D as a stated contribution: five task templates, a frozen 15-case suite, typed state predicates and evaluator-owned simulator probes (section IV).

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.17651) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.
- [Source 2](https://arxiv.org/html/2610.17651v1#S4) — `full_text`. Read introduction contributions and section IV-A?IV-C: SimCode4D specifies frozen cases, input/output contracts, build gates, physical admissibility and task-completion checks.

## PhysCodeGym

- **Record:** `physcodegym`
- **Reviewed:** 2026-10-22
- **README:** Benchmark
- **Website:** Benchmark, World Reconstruction, Physics
- **Placement reason:** The benchmark evaluates whether observation-matching reconstructed programs remain physically reliable under intervention.

**Topic evidence**

- **Benchmark:** Introduces 156 video-to-simulation tasks and six visual and physical reconstruction metrics.
- **World Reconstruction:** Agents recover dynamic scenes as executable Blender programs from observed videos.
- **Physics:** Program inspection, measurements and counterfactual interventions test contact, support and other physical consistency.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.17288) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.

## PhySimCode

- **Record:** `physimcode`
- **Reviewed:** 2026-10-22
- **README:** Benchmark
- **Website:** Benchmark, Dataset, World Reconstruction, Physics
- **Placement reason:** This is a benchmark and paired physical-simulation data resource, not a new universal simulation model.

**Topic evidence**

- **Benchmark:** Defines physics-video-to-code evaluation covering laws, parameters, simulation equivalence and executability.
- **Dataset:** Provides aligned simulation programs, physical parameters and videos; the public evaluation release has 2,430 videos.
- **World Reconstruction:** Models infer governing dynamics and parameters from a raw video to reproduce it with runnable simulations.
- **Physics:** Targets quantitative laws and parameters across 162 physical phenomena.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.15722) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.

**Limits / unresolved details**

- The paper's 160.6K generated samples and public 2,430-video evaluation release are different resource scopes; do not present the larger count as the linked public release.

## ANTE

- **Record:** `ante`
- **Reviewed:** 2026-10-22
- **README:** Post-Training
- **Website:** Post-Training, Code Execution, Planning, Agent Learning
- **Placement reason:** The main methodological contribution is training a policy and its internal execution world model together.

**Topic evidence**

- **Post-Training:** Supervised belief training and belief-anchored reinforcement learning teach a coding policy to predict before acting.
- **Code Execution:** Predicts tool and test outcomes before software actions and verifies those forecasts through real execution.
- **Planning:** At inference, ANTE-TTO ranks alternative actions using their predicted outcomes and executes the selected candidate.
- **Agent Learning:** Uses the learned world-model forecasts to supply per-step credit and improve the coding agent's policy.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.15368) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.
- [Source 2](https://arxiv.org/html/2610.15368v1) — `full_text`. Read sections 3.1–3.4 and 4.4: the foresight mechanism ranks candidates rather than executing all alternatives.

**Limits / unresolved details**

- Planning here means forecast-based action selection, not a claim of multi-step tree search.
- No Memory tag: a belief state is used, but explicit long-term memory is not the studied mechanism.

## ExeWorldBench

- **Record:** `exeworldbench`
- **Reviewed:** 2026-10-22
- **README:** Benchmark
- **Website:** Benchmark, Physics, World Reconstruction, World Generation
- **Placement reason:** The primary contribution is evaluating physically executable world construction across reconstruction and synthesis settings.

**Topic evidence**

- **Benchmark:** Introduces mechanism, composition and intent-driven executable-world tasks with a unified evaluation.
- **Physics:** Evaluates mechanical and causal realization through functioning physical interactions.
- **World Reconstruction:** Mechanism and compositional tasks turn visually observed mechanisms into executable 3D systems.
- **World Generation:** Intent-driven synthesis tasks construct new executable worlds from goals and physical requirements.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.15166) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.

## AgentGarten

- **Record:** `agentgarten`
- **Reviewed:** 2026-10-22
- **README:** Agent Learning
- **Website:** Agent Learning, General World Model, Interactive, Real-Time, Acceleration, Streaming, Long Video Generation, Multi-Agent, Action Control, Neural Rendering, Post-Training
- **Placement reason:** README placement follows the paper's agent-learning objective while the website exposes its integrated rendering and interaction contributions.

**Topic evidence**

- **Agent Learning:** Agents improve through repeated interaction and inherited playbooks across diverse code worlds.
- **General World Model:** A common framework integrates program-controlled simulator state, observation rendering and agent interaction across environments.
- **Interactive:** Agents and users act on code worlds and observe the resulting neural-rendered state changes.
- **Real-Time:** Reports over 35 FPS at 480×832 on one H100, including condition encoding, four-step generation, decoding and host transfer.
- **Acceleration:** Uses few-step distillation, custom Triton kernels, CUDA graphs and a tiny decoder.
- **Streaming:** Processes incoming blocks with a bounded KV cache and streams decoded observations.
- **Long Video Generation:** Adversarial Forcing specifically limits visual degradation in long video rollouts; section 4.1 compares 30-second generations.
- **Multi-Agent:** Evaluates hider–seeker, shared-state racing, bridge coordination and herding with multiple agents inside a world.
- **Action Control:** Keyboard, mouse, gamepad or movement/action programs advance the simulated environment.
- **Neural Rendering:** A shared geometry-conditioned renderer maps different simulation backends to visual observations.
- **Post-Training:** Adapts a pretrained video model and introduces Adversarial Forcing distillation.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.12374) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.
- [Source 2](https://arxiv.org/html/2610.12374v2) — `full_text`. Read sections 2–5, especially streaming, throughput, 30-second visual rollouts and world-internal multi-agent experiments.

**Limits / unresolved details**

- The learning comparison uses pretrained agents and written playbooks; its rounds are not directly comparable to tabula-rasa RL episodes.
- The reported FPS is generation throughput, not a measured key-to-display latency.

## WorldSolver

- **Record:** `worldsolver`
- **Reviewed:** 2026-10-22
- **README:** Benchmark
- **Website:** Benchmark, Physics
- **Placement reason:** The task is implementing simulation solvers inside fixed scaffolds, so Physics is substantive but full-world generation is not assumed.

**Topic evidence**

- **Benchmark:** Provides 168 solver-generation tasks drawn from 61 graphics papers across seven physical domains.
- **Physics:** Requires executable numerical solvers to reproduce physically plausible dynamic phenomena.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.08720) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.

## Video2World

- **Record:** `video2world`
- **Reviewed:** 2026-10-22
- **README:** Benchmark
- **Website:** Benchmark, World Reconstruction, Physics, Interactive
- **Placement reason:** The benchmark's main distinction is operational video-to-simulation reconstruction, including executable interaction rather than appearance alone.

**Topic evidence**

- **Benchmark:** Introduces 222 reconstruction instances from embodied videos and evaluates nine coding-agent systems.
- **World Reconstruction:** Agents reconstruct observed environments and robot behavior as executable simulations.
- **Physics:** Dynamic fidelity and physical reasoning are explicit evaluation targets alongside geometric fidelity.
- **Interactive:** Functional correctness tests whether reconstructed worlds support the intended embodied interaction.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.04432) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.

## 4DCodeBench

- **Record:** `4dcodebench`
- **Reviewed:** 2026-10-22
- **README:** Benchmark
- **Website:** Benchmark, World Reconstruction, Physics
- **Placement reason:** The study measures dynamic reconstruction capabilities; it does not propose a long-video generator.

**Topic evidence**

- **Benchmark:** Defines inverse-graphics evaluation of dynamic scenes through generated executable graphics programs.
- **World Reconstruction:** Agents infer scene structure and temporal dynamics from real or synthetic reference videos.
- **Physics:** Tasks span physical behaviors such as deformation, fluid flow and fracture.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.03715) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.

## IGMWorld / IGMBench

- **Record:** `igmworld`
- **Reviewed:** 2026-10-22
- **README:** Benchmark
- **Website:** Benchmark, World Editing
- **Placement reason:** IGMBench's central research question is the reliability of behavioral world edits rather than new-world generation or action-control design.

**Topic evidence**

- **Benchmark:** Introduces 110 game-modding tasks with executable state, behavioral, preservation and visual criteria.
- **World Editing:** Studies edits to existing worlds at property, entity, dynamics and system depth while preserving unaffected properties.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2610.02331) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.

**Limits / unresolved details**

- The source explicitly distinguishes world editing from world interaction; playing an existing game does not by itself justify an Interactive tag.

## Physis-Lang

- **Record:** `physis-lang`
- **Reviewed:** 2026-10-22
- **README:** Physics
- **Website:** Physics, Post-Training, Benchmark
- **Placement reason:** Its main contribution is physical reasoning language and training for video models; it is a comparison work rather than an executable-world program method.

**Topic evidence**

- **Physics:** Optimizes language representations of physical entities, causes, laws and temporal processes to improve physical video plausibility.
- **Post-Training:** Uses language-guided data curation and supervised fine-tuning of Wan and Cosmos backbones.
- **Benchmark:** Introduces PhysCapBench as a stated contribution, with 246 videos, 3,794 human-verified assertions, and physical-caption precision/recall/F1 protocols (sections 4.1?4.2).

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2609.40358) — `primary_abstract`. Read the author abstract; the paper identity matches the catalog.
- [Source 2](https://arxiv.org/html/2609.40358v1) — `full_text`. Read introduction contributions, sections 4.1?4.2, appendix B.1 and section 5.4.3: new PhysCapBench task/annotations/protocol and prompting versus fine-tuning.

**Limits / unresolved details**

- The method does not synthesize executable world code.

## Text2Sim

- **Record:** `text2sim`
- **Reviewed:** 2026-10-22
- **README:** World Generation
- **Website:** World Generation, Physics
- **Placement reason:** The main contribution is authoring runnable physical simulations from language, rather than a general visual world model or a benchmark resource.

**Topic evidence**

- **World Generation:** The pipeline turns text requests into complete executable cases including assets, layout, controls, and rendering.
- **Physics:** Physics expertise and execution-based repair are evaluated across rigid, articulated, deformable, and cloth phenomena.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2609.36593) — `primary_abstract`. Read the current v2 author abstract online; title and identifier match.
- [Source 2](https://arxiv.org/html/2609.36593v2) — `full_text`. Read design goals and editable-output/application passages. Debug Cards distill reusable experience, not model weights.

**Limits / unresolved details**

- Dataset construction is an application and the abstract promises releases; no Dataset or Post-Training tag is inferred from these statements.

## Code4Scene

- **Record:** `code4scene`
- **Reviewed:** 2026-10-22
- **README:** Benchmark
- **Website:** Benchmark, World Generation, World Editing, Physics
- **Placement reason:** Its principal contribution is a controlled scene construction/editing benchmark and evaluation protocol.

**Topic evidence**

- **Benchmark:** Introduces 190 Unreal Engine cases and compares 14 coding-agent configurations under a shared execution interface.
- **World Generation:** The construction setting tests creating whole scenes from open-ended language specifications.
- **World Editing:** The editing setting requires recovering target state while preserving unrelated scene content.
- **Physics:** Engine-native static physical validity, including spatial defects hidden by plausible renders, is a named evaluation axis.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2609.36777) — `primary_abstract`. Read the author abstract online; matches the catalog identity.

## GPUPhysBench

- **Record:** `gpuphysbench`
- **Reviewed:** 2026-10-22
- **README:** Benchmark
- **Website:** Benchmark, Physics, Acceleration
- **Placement reason:** A dedicated GPU simulation benchmark makes both physical correctness and runtime optimization central.

**Topic evidence**

- **Benchmark:** Introduces 50 tasks, fixed agent time budgets, and expert reference implementations.
- **Physics:** Tasks cover fluid, deformable-solid, and granular simulation operators and complete simulators.
- **Acceleration:** Agents optimize GPU implementations, and runtime relative to expert code is a central reported outcome.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2609.35639) — `primary_abstract`. Read the author abstract online, including numerical-correctness and runtime comparisons.

**Limits / unresolved details**

- Efficient GPU code is not sufficient evidence of real-time end-to-end operation; Real-Time is omitted.

## WorldAgent

- **Record:** `worldagent`
- **Reviewed:** 2026-10-22
- **README:** World Generation
- **Website:** World Generation, Physics, Benchmark
- **Placement reason:** The method's central output is a verified physical world constructed from a natural-language request.

**Topic evidence**

- **World Generation:** A world-construction layer expands one prompt into specifications, geometry, and executable simulation steps.
- **Physics:** Verification checks numerical simulation states and implicit physical constraints, then revises failing construction steps.
- **Benchmark:** Introduces AgenticSimBench: 13 compositional physical-world prompts with seven physical, shot, content, and visual metrics, formally defined in Appendix C.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2609.33208) — `primary_abstract`. Read the author abstract online, including construction/verification responsibilities and AgenticSimBench.
- [Source 2](https://arxiv.org/html/2609.33208v1) — `full_text`. Read contributions and section 4.2: AgenticSimBench is newly constructed, with explicit task scope and seven scoring metrics.

**Limits / unresolved details**

- Benchmark is an additional website relationship; the README retains World Generation as the dominant method contribution.

## GameDirector

- **Record:** `game-director`
- **Reviewed:** 2026-10-22
- **README:** General World Model
- **Website:** General World Model, Memory, Interactive, Real-Time, Streaming, Multi-Agent, Action Control, World Editing, Neural Rendering, Long Video Generation
- **Placement reason:** An integrated game-world framework joins persistent mechanics, player interaction, NPC behavior, and visual generation.

**Topic evidence**

- **General World Model:** Combines perception, state tracking, rule enforcement, and generated gameplay in a closed loop.
- **Memory:** An external tracker maintains health, meters, cooldowns, and terminal states across play.
- **Interactive:** Generated observations feed back into decisions after player actions.
- **Real-Time:** Section 4.1 reports 20 FPS closed-loop operation for the studied three-game setup, using 832-by-480 generation.
- **Streaming:** Section 3.4 generates four-frame steps and feeds them back for subsequent control.
- **Multi-Agent:** The player and independently controlled boss act against one another under shared combat state.
- **Action Control:** Player inputs and validated boss actions condition the generated video.
- **World Editing:** Players configure characters, combat attributes, skills, and rules.
- **Neural Rendering:** The video model visually realizes decisions produced by the explicit logic layer.
- **Long Video Generation:** Appendix A.3 evaluates generated gameplay using minute-long control sequences.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2609.25652) — `primary_abstract`. Read the matching author abstract.
- [Source 2](https://arxiv.org/html/2609.25652v1) — `full_text`. Read sections 3.2-3.4, 4.1, and Appendix A.2-A.3.

**Limits / unresolved details**

- Reported frame rate was not reproduced; inference hardware was not specified in the passages read.

## CoDeR

- **Record:** `coder`
- **Reviewed:** 2026-10-22
- **README:** General World Model
- **Website:** General World Model, Memory, Interactive, Multi-Agent, Action Control, World Generation, Neural Rendering, Long Video Generation, Post-Training
- **Placement reason:** An integrated executable-world and generative-observation framework explicitly studies persistent state, interaction, and multiple inhabitants.

**Topic evidence**

- **General World Model:** Connects world rules, executable evolution, and perceptual observations in one framework.
- **Memory:** Registers generated appearance back into the world and tests revisits and off-screen evolution.
- **Interactive:** Demonstrates environment interactions such as opening doors and piloting vehicles.
- **Multi-Agent:** Multi-Traveler tests show one inhabitant's actions changing another's observations of shared state.
- **Action Control:** Code-defined actions extend the action space beyond a fixed predefined menu.
- **World Generation:** Logical-space construction builds and composes world modules from high-level intent.
- **Neural Rendering:** An Artist video model renders whitebox/depth conditions into visual observations.
- **Long Video Generation:** Autoregressive chunk rollout is explicitly examined, including degradation near 5,000 frames.
- **Post-Training:** Section 4.2 adapts MiniMax-H3 to code-world whitebox/depth/registered observations using Visual Cue Hacking pairs, backbone LoRA, and full ControlNet tuning.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2609.26458) — `primary_abstract`. Read the matching author abstract.
- [Source 2](https://arxiv.org/html/2609.26458v1) — `full_text`. Read sections 3.2, 4.1-4.3, and the long-video limitation; section 4.2 specifically trains the new code-world observation interface.

**Limits / unresolved details**

- No Real-Time claim is inferred from persistent interaction. Long rollouts explicitly accumulate visual errors.

## BVB / Blender-VideoBench

- **Record:** `bvb`
- **Reviewed:** 2026-10-22
- **README:** Benchmark
- **Website:** Benchmark, World Reconstruction
- **Placement reason:** Its main contribution tests video understanding by requiring executable animated reconstructions.

**Topic evidence**

- **Benchmark:** Provides a shared Blender reconstruction harness, cost limits, dual evaluation axes, and comparison of 51 configurations.
- **World Reconstruction:** Agents reconstruct real-world videos as animated scenes, preserving spatiotemporal facts and appearance.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2609.15478) — `primary_abstract`. Read the current v3 author abstract, including the reconstruction task and evaluation setup.

## Recursive Code World Models

- **Record:** `recursive-cwm`
- **Reviewed:** 2026-10-22
- **README:** World Reconstruction
- **Website:** World Reconstruction
- **Placement reason:** Recursive perception and refinement recover a complex 3D scene from one image; recursion is a construction strategy rather than a separate topic.

**Topic evidence**

- **World Reconstruction:** Recursive Scene Programs and a global-local-global solver reconstruct fine geometry while maintaining reference alignment and scene relations.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2609.11499) — `primary_abstract`. Read the current v2 author abstract and matched the single-reference-image reconstruction objective.

**Limits / unresolved details**

- Perception/editing loops refine the reconstruction; they are not by themselves evidence of a separate user-facing World Editing contribution.

## Programmable World Model

- **Record:** `programmable-world-model`
- **Reviewed:** 2026-10-22
- **README:** General World Model
- **Website:** General World Model, Memory, Interactive, Action Control, World Editing, Neural Rendering, Long Video Generation, Benchmark, Post-Training
- **Placement reason:** A complete programmable world loop links canonical state transitions and controllable visual observations.

**Topic evidence**

- **General World Model:** Combines executable entity/rule state, player-driven transitions, control compilation, and generated observations.
- **Memory:** Maintains off-screen entities and hidden attributes, plus temporal and geometry-aligned visual memory.
- **Interactive:** The engine validates and executes player actions, then renders the resulting state.
- **Action Control:** Player commands and object motion are compiled into explicit visual conditioning.
- **World Editing:** Programs define editable entity attributes, relations, and rules governing gameplay.
- **Neural Rendering:** A pretrained generative renderer transforms projected box controls into visual detail.
- **Long Video Generation:** Section 4.4.2 adds chunk-autoregressive rendering with temporal and spatial memory for extended sequences.
- **Benchmark:** CombatStateBench introduces 50 verified combat clips, synchronized engine state, and Count Accuracy/State Accuracy scoring over sampled frames and death events.
- **Post-Training:** Section 4.4.1 freezes pretrained LingBot-World-v1 and trains a new Structured Spatial ControlNet to follow engine-derived identity, semantic, and motion controls.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2609.10540) — `primary_abstract`. Read the current v2 author abstract.
- [Source 2](https://arxiv.org/html/2609.10540v2) — `full_text`. Read sections 4.1-4.4 and 5.1-5.2: executable transitions, cross-chunk memory, and the new CombatStateBench tasks/scoring protocol.

**Limits / unresolved details**

- Chunk-causal rendering alone is not treated as sufficient proof of a dedicated streaming implementation or real-time operation. CombatStateBench does not replace the method's README category.

## VeriPhy

- **Record:** `veriphy`
- **Reviewed:** 2026-10-22
- **README:** Evaluation
- **Website:** Evaluation, Physics
- **Placement reason:** The central contribution is an auditable physical verifier with evidence-linked diagnoses, rather than a general world generator.

**Topic evidence**

- **Evaluation:** Produces localized supported/contradicted/unknown judgments and compares them with annotated generation failures.
- **Physics:** Compiles physical obligations and measures trajectories and other typed physical quantities to diagnose implausibility.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2609.03153) — `primary_abstract`. Read the author abstract, including corpus and evidence-provenance claims.
- [Source 2](https://arxiv.org/html/2609.03153v1) — `full_text`. Read section 5.5 and scope statements about prompt-only refinement and independent ratings.

**Limits / unresolved details**

- The refinement loop improves its triggering metric but the reported independent rater shows no change; this is not evidence of a generally improved generator or a Post-Training method.

## Code as Worlds

- **Record:** `code-as-worlds`
- **Reviewed:** 2026-10-22
- **README:** Physics
- **Website:** Physics, World Generation, World Reconstruction, Post-Training
- **Placement reason:** Verified physical worlds support quantitative physical reasoning, making Physics the most informative single README category.

**Topic evidence**

- **Physics:** Explicit physical composition, parameters, and evolution support quantitative reasoning about mechanisms.
- **World Generation:** A text-driven pipeline proposes and verifies executable physical-world hypotheses.
- **World Reconstruction:** A video-driven discovery loop recovers executable representations from observed physical events.
- **Post-Training:** Section 5.4.1 uses supervised fine-tuning followed by GRPO on world-derived physical questions.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2608.27549) — `primary_abstract`. Read the matching author abstract.
- [Source 2](https://arxiv.org/html/2608.27549v1) — `full_text`. Read the text/video construction description and the two-phase training protocol in section 5.4.1.

**Limits / unresolved details**

- Training a visual physical-reasoning model is not automatically Agent Learning, which is reserved for policy or acting-agent improvement.

## Code World Model

- **Record:** `code-world-model`
- **Reviewed:** 2026-10-22
- **README:** General World Model
- **Website:** General World Model, Memory, Interactive, Action Control, World Editing, Neural Rendering, Long Video Generation, Post-Training
- **Placement reason:** The paper proposes the integrated agent-code-state-proxy-observation architecture, with a limited interactive-world prototype.

**Topic evidence**

- **General World Model:** A coding agent governs executable world evolution and a video model supplies visual observations.
- **Memory:** World state preserves identities, rules, relations, history, and consequences outside the current view.
- **Interactive:** Agent-built worlds accept actions and feed updated state into subsequent observations.
- **Action Control:** Frame-aligned proxies constrain character positions, motions, and action trajectories.
- **World Editing:** The agent locally revises state and operating mechanisms through modifiable code.
- **Neural Rendering:** Proxy videos condition an adapted video model to realize the executable state visually.
- **Long Video Generation:** Section 4.1 describes continuation using overlapping 124-frame windows.
- **Post-Training:** The main proxy-observation interface is learned by adapting pretrained MiniMax-H3 with rank-128 LoRA on aligned gameplay pairs, rather than merely training a comparison baseline.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2608.25927) — `primary_abstract`. Read the matching author abstract.
- [Source 2](https://arxiv.org/html/2608.25927v1) — `full_text`. Read sections 3.1, 4.1, and 5, including windowed inference and prototype limits.

**Limits / unresolved details**

- Section 5 explicitly says autoregressive real-time generation is not implemented. Complete autonomous open-world construction remains future work.

## VideoCoCo

- **Record:** `videococo`
- **Reviewed:** 2026-10-22
- **README:** Neural Rendering
- **Website:** Neural Rendering, Physics, Dataset, Post-Training
- **Placement reason:** The paper's distinctive output is physically consistent video obtained by transforming an executable simulation draft.

**Topic evidence**

- **Neural Rendering:** A generative video engine edits deterministic Blender drafts into photorealistic observations.
- **Physics:** Executable process-level plans address physical dynamics and are evaluated on physics-oriented video quality benchmarks.
- **Dataset:** Introduces VideoCoCo-3K as a named contribution: 3,000 aligned draft-instruction-target triplets. Official code currently provides an eight-triplet sample; full release is unverified.
- **Post-Training:** Adapts pretrained OmniWeaving to simulation drafts and explicitly compares full fine-tuning, LoRA adaptation, and no-tuning variants.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2607.27380) — `primary_abstract`. Read the current v2 author abstract, including dual-engine stages and VideoCoCo-3K.
- [Source 2](https://arxiv.org/html/2607.27380v2) — `full_text`. Read contributions, sections 3.3-3.4, and Table 3: new aligned data construction and editor-adaptation ablations.
- [Source 3](https://github.com/micky-li-hd/VideoCoCo/blob/main/README.md) — `official_project`. Read the official README via GitHub connector: eight toy triplets are released; it explicitly distinguishes them from a training-scale corpus.

**Limits / unresolved details**

- Full VideoCoCo-3K public release is not established. Dataset describes the named data contribution and available toy sample, not a claim that all 3,000 training triplets can be downloaded.

## VisualPatchWorld

- **Record:** `visualpatchworld`
- **Reviewed:** 2026-10-22
- **README:** Planning
- **Website:** Planning, World Reconstruction, Physics
- **Placement reason:** The induced executable dynamics are judged primarily by their usefulness for model-predictive planning and control.

**Topic evidence**

- **Planning:** Recovered programs roll forward inside model-predictive control and improve navigation/manipulation planning success.
- **World Reconstruction:** Active probes choose a dynamics form and recorded state-action traces fit its unknown parameters.
- **Physics:** The method addresses dynamical form, contact-rich motion, grasping, and physical parameter identification.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2607.25236) — `primary_abstract`. Read the author abstract, including identification procedure and planning experiments.

## GS-Agent

- **Record:** `gs-agent`
- **Reviewed:** 2026-10-22
- **README:** World Generation
- **Website:** World Generation, Physics
- **Placement reason:** The main contribution automates construction of dynamic physical worlds from language.

**Topic evidence**

- **World Generation:** Creates 4D worlds by coordinating assets, layout, material tuning, motion, cameras, and lighting.
- **Physics:** Physics-engine feedback drives physical plausibility for interacting liquids, deformable objects, and rigid bodies.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2607.21522) — `primary_abstract`. Read the author abstract and distinguished authoring agents from world inhabitants.

**Limits / unresolved details**

- Multi-agent refers to specialized authoring agents, so the world-inhabitant Multi-Agent topic is omitted.

## SimWorlds

- **Record:** `simworlds`
- **Reviewed:** 2026-10-22
- **README:** World Generation
- **Website:** World Generation, Physics, World Editing, Benchmark
- **Placement reason:** Its primary deliverable is a dynamic procedural scene-authoring system, with a benchmark supporting method evaluation.

**Topic evidence**

- **World Generation:** A planner-coder-reviewer workflow creates dynamic 4D Blender scenes from text.
- **Physics:** Coordinates physical solvers and uses runtime-state inspection to detect mechanisms that rendered images conceal.
- **World Editing:** Edit mode updates existing scenes from text and target images; section 4.2 evaluates these edits separately on reused BlenderBench tasks.
- **Benchmark:** Introduces 4DBuildBench: 50 prompts spanning five physical solvers, three dynamic difficulty levels, and static scenes, with engine-state MPR/SPR and itemized visual judging.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2607.01766) — `primary_abstract`. Read the matching author abstract, including the newly introduced 4DBuildBench.
- [Source 2](https://arxiv.org/html/2607.01766v1) — `full_text`. Read sections 4.1-4.2 and Appendix D: new 4DBuildBench composition/scoring, plus separate existing-scene editing experiments.

**Limits / unresolved details**

- The multi-agent title describes scene-authoring agents rather than autonomous inhabitants. Benchmark records the new 4DBuildBench, not mere reuse of BlenderBench; the README remains World Generation.

## MPMWorlds

- **Record:** `mpmworlds`
- **Reviewed:** 2026-10-22
- **README:** Dataset
- **Website:** Dataset, Physics, World Reconstruction, Evaluation
- **Placement reason:** The paper centers on a new paired physical-simulation dataset and comparative study; Dataset best represents its main contribution.

**Topic evidence**

- **Dataset:** Provides paired source code, configurations, and rendered simulations covering varied physical materials.
- **Physics:** Investigates physical-parameter inference and extrapolation across fluids and deformable materials.
- **World Reconstruction:** Code models infer complete runnable physical scenes from an observed video prefix and optional side information.
- **Evaluation:** Controlled comparisons isolate geometric and dynamical weaknesses of code generation and video diffusion.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2606.01538) — `primary_abstract`. Read the current v2 author abstract.
- [Source 2](https://arxiv.org/html/2606.01538v2) — `full_text`. Read contributions, sections 3-4, dataset statistics, input conditions, and physical-extrapolation analysis.

**Limits / unresolved details**

- Simulations last ten seconds; longer-horizon physical extrapolation is not sufficient to assign Long Video Generation. Ordinary fine-tuning of comparison baselines is not treated as a separate Post-Training contribution.

## 3DCodeBench / 3DCodeArena

- **Record:** `3dcodebench`
- **Reviewed:** 2026-10-22
- **README:** Benchmark
- **Website:** Benchmark, World Generation, Dataset
- **Placement reason:** A procedural 3D modeling benchmark, public human-preference arena, and associated data are the principal deliverables.

**Topic evidence**

- **Benchmark:** Defines standardized procedural-modeling evaluation for 12 VLM agents and human preference rankings.
- **World Generation:** Tests code-based creation of engine-ready 3D assets from multimodal references.
- **Dataset:** Releases a curated collection pairing text/image prompts, procedural programs, and 3D objects.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2606.01057) — `primary_abstract`. Read the author abstract including benchmark, arena, and released multimodal triplets.

## SceneCode

- **Record:** `scene-code`
- **Reviewed:** 2026-10-22
- **README:** World Generation
- **Website:** World Generation, World Editing, Interactive, Physics
- **Placement reason:** The framework creates indoor environments with editable, physically interactable articulated assets.

**Topic evidence**

- **World Generation:** Compiles language into house layouts, per-object programs, and assembled simulation-ready scenes.
- **World Editing:** Section 4.3 demonstrates changing named asset parameters and locally re-executing individual objects.
- **Interactive:** Section 4.4 demonstrates robots physically opening/sliding generated articulated parts.
- **Physics:** Programs compile collision and joint metadata for contact-based MuJoCo manipulation.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2605.19587) — `primary_abstract`. Read the matching author abstract.
- [Source 2](https://arxiv.org/html/2605.19587v1) — `full_text`. Read code-level editing and robot interaction demonstrations in sections 4.3-4.4.

**Limits / unresolved details**

- A persistent construction registry is not treated as a world-memory research contribution.

## SimWorld Studio

- **Record:** `simworld-studio`
- **Reviewed:** 2026-10-22
- **README:** Agent Learning
- **Website:** Agent Learning, World Generation, Interactive
- **Placement reason:** The central contribution is co-evolving generated embodied environments and learner curricula.

**Topic evidence**

- **Agent Learning:** Learner feedback drives adaptive curricula; navigation training gains over fixed environments are evaluated.
- **World Generation:** SimCoder constructs 3D environments from language or images using engine-level code.
- **Interactive:** Generated environments expose Gym-style interfaces for embodied interaction and learning.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2605.09423) — `primary_abstract`. Read the complete author abstract, including generation, verifier feedback and curriculum experiments.

**Limits / unresolved details**

- Self-evolving skills are not evidence of world-model parameter post-training.

## Code2Worlds

- **Record:** `code2worlds`
- **Reviewed:** 2026-10-22
- **README:** World Generation
- **Website:** World Generation, Physics, Benchmark
- **Placement reason:** The method generates dynamic 4D worlds through simulation code and physics-aware refinement.

**Topic evidence**

- **World Generation:** Dual-stream code generation separates object construction from environmental orchestration.
- **Physics:** A dynamics-scripting agent and motion critic address physical hallucinations in generated simulations.
- **Benchmark:** Introduces Code4D for object, scene and dynamic generation, with CLIP/VBench, SGS, Richness, HRS and physical-failure protocols.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2602.11757) — `primary_abstract`. Read the complete author abstract and its dynamic-fidelity contribution.
- [Source 2](https://arxiv.org/html/2602.11757) — `full_text`. Read Code4D contribution statement, Section 4.1 benchmark/metrics and Appendix D task construction/release details.

**Limits / unresolved details**

- Code4D is introduced by this paper; full benchmark prompts and scripts are promised upon acceptance, not independently verified as released.

## Debugging Code World Models

- **Record:** `debugging-cwm`
- **Reviewed:** 2026-10-22
- **README:** Evaluation
- **Website:** Evaluation, Code Execution, Memory
- **Placement reason:** This is a diagnostic analysis of execution semantics and long-horizon state-tracking failures.

**Topic evidence**

- **Evaluation:** Controlled interventions separate trace truncation, string errors and action hallucination.
- **Code Execution:** The object of study is neural prediction of Python execution traces and runtime variables.
- **Memory:** Experiments isolate state propagation over long operation sequences under corrected versus generated actions.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2602.07672) — `primary_abstract`. Read the complete author abstract.
- [Source 2](https://arxiv.org/html/2602.07672v2) — `full_text`. Read introduction and contribution statements; inspected long-horizon experiment framing, not every appendix.

**Limits / unresolved details**

- The permutation task adapts an existing benchmark; this analysis is not classified as a new benchmark release.

## SWE-World

- **Record:** `swe-world`
- **Reviewed:** 2026-10-22
- **README:** Agent Learning
- **Website:** Agent Learning, Code Execution, Post-Training
- **Placement reason:** A learned execution surrogate enables Docker-free software-agent optimization.

**Topic evidence**

- **Agent Learning:** Agents learn inside a surrogate software environment instead of repeatedly constructing containers.
- **Code Execution:** Models predict intermediate execution outcomes and final program-test feedback.
- **Post-Training:** The paper evaluates Docker-free supervised fine-tuning and reinforcement learning of coding agents.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2602.03419) — `primary_abstract`. Read the complete author abstract and reported SFT/RL results.

**Limits / unresolved details**

- This is a computational environment model, not a physical-world simulator.
- Container removal is not sufficient evidence of measured real-time execution or an inference acceleration contribution.

## Code World Models for General Game Playing

- **Record:** `general-game-playing`
- **Reviewed:** 2026-10-22
- **README:** Planning
- **Website:** Planning, World Reconstruction, Multi-Agent
- **Placement reason:** Executable game rules and hidden-state inference support strong search-based game play.

**Topic evidence**

- **Planning:** Synthesized transition, legality and value functions drive MCTS and information-set search.
- **World Reconstruction:** Game descriptions and observed trajectories are translated into state, transition, reward and observation rules.
- **Multi-Agent:** The work evaluates strategic play across two-player perfect- and imperfect-information games.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2510.04542) — `primary_abstract`. Read the complete author abstract.
- [Source 2](https://arxiv.org/html/2510.04542v1) — `full_text`. Read introduction, world-model definition and Section 5's ten-game setup, accuracy protocol and match evaluation.

**Limits / unresolved details**

- General game playing does not by itself mean a general-purpose flagship world model.
- No Benchmark tag: four new games support the method experiments, but the paper does not introduce a named benchmark suite as a research contribution.
- Code Execution is reserved for execution semantics research, not ordinary simulator rollouts.

## CWM (Meta)

- **Record:** `cwm-meta`
- **Reviewed:** 2026-10-22
- **README:** Code Execution
- **Website:** Code Execution, Post-Training
- **Placement reason:** The model grounds coding in computational state transitions and execution traces.

**Topic evidence**

- **Code Execution:** Mid-training teaches changes to Python runtime variables and agentic software environments; execution prediction is evaluated.
- **Post-Training:** The report provides supervised fine-tuning and multi-environment reasoning RL stages and released checkpoints.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2510.02387) — `primary_abstract`. Read the complete author abstract.
- [Source 2](https://arxiv.org/html/2510.02387v1) — `full_text`. Read introduction and trace-data definition; checked planning motivation and limitations.

**Limits / unresolved details**

- The modeled domain is program execution; this is not a generated embodied world.
- The report treats robust planning with the model largely as future research, so Planning is not assigned.
- General World Model is withheld because the contribution is a domain-specific coding model rather than a complete general interactive-world framework.

## BlenderGym

- **Record:** `blendergym`
- **Reviewed:** 2026-10-22
- **README:** Benchmark
- **Website:** Benchmark, World Editing, World Reconstruction, Evaluation
- **Placement reason:** A graphics-editing benchmark also analyzes generator and verifier inference scaling.

**Topic evidence**

- **Benchmark:** Introduces a comprehensive VLM benchmark for code-based 3D graphics editing.
- **World Editing:** Tasks require modifying graphics scenes, a central target of the benchmark.
- **World Reconstruction:** Evaluation uses code-based 3D reconstruction tasks.
- **Evaluation:** Separately analyzes generator/verifier scaling and allocation of inference compute.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2504.01786) — `primary_abstract`. Read the complete author abstract and inference-scaling analysis claims.

**Limits / unresolved details**

- Inference scaling allocates more computation; it is not automatically inference acceleration.

## FactorSim

- **Record:** `factorsim`
- **Reviewed:** 2026-10-22
- **README:** World Generation
- **Website:** World Generation, Agent Learning, Interactive, Benchmark
- **Placement reason:** Factorized generation constructs full simulators for policy transfer and introduces a test suite.

**Topic evidence**

- **World Generation:** Generates complete simulation code from language specifications using factored POMDP structure.
- **Agent Learning:** Policies trained in generated simulations are evaluated for zero-shot transfer.
- **Interactive:** Generation explicitly builds action handling, state-update logic and rendered feedback.
- **Benchmark:** A stated contribution is an eight-environment generative simulation benchmark with system-test and transfer metrics.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2409.17652) — `primary_abstract`. Read the complete author abstract.
- [Source 2](https://arxiv.org/html/2409.17652v2) — `full_text`. Read introduction and benchmark contribution, including MVC/action-loop examples and eight-task definition.

**Limits / unresolved details**

- Factorization reduces generation context; this does not establish real-time inference.
- Generated agents or enemies do not make multi-agent reasoning the paper's research focus.

## GIF-MCTS / CWMB

- **Record:** `gif-mcts`
- **Reviewed:** 2026-10-22
- **README:** Planning
- **Website:** Planning, World Reconstruction, Benchmark, Acceleration
- **Placement reason:** Search synthesizes transition models from observations for efficient model-based planning.

**Topic evidence**

- **Planning:** Synthesized Python transition/reward models are used directly for downstream planning.
- **World Reconstruction:** Generated models are revised to reproduce observed environment state transitions.
- **Benchmark:** Introduces CWMB: 18 environments with descriptions/trajectories; scores transition accuracy and normalized planning return.
- **Acceleration:** The paper reports faster downstream model-based inference from calling code rather than a neural world model.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2405.15383) — `primary_abstract`. Read the complete author abstract.
- [Source 2](https://arxiv.org/html/2405.15383v2) — `full_text`. Inspected synthesis method, Section 3 benchmark construction, Section 5.3 accuracy/return protocol and Appendix I task list.

**Limits / unresolved details**

- No Real-Time tag: relative inference-speed gains do not establish a real-time deployment budget.
- Search over candidate programs is not multi-agent world dynamics.

## PhysDreamer

- **Record:** `physdreamer`
- **Reviewed:** 2026-10-22
- **README:** Physics
- **Website:** Physics, Interactive, Action Control
- **Placement reason:** Video priors are distilled into object material dynamics for new physical interactions.

**Topic evidence**

- **Physics:** Estimates physical material properties and grounds deformable-object responses in simulation.
- **Interactive:** Static 3D objects are endowed with dynamics that respond to new external interactions.
- **Action Control:** Demonstrates responses conditioned on applied forces and agent manipulations.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2404.13026) — `primary_abstract`. Read the complete author abstract and stated force/manipulation scope.

**Limits / unresolved details**

- Distilling video priors into material parameters is not necessarily post-training the video model.
- This inverse-physics neighbor does not itself synthesize symbolic world programs.

## SceneCraft (Blender code)

- **Record:** `scenecraft`
- **Reviewed:** 2026-10-22
- **README:** World Generation
- **Website:** World Generation, World Reconstruction, Neural Rendering
- **Placement reason:** Scene graphs and Blender code build complex scenes, with reconstruction and video-control demonstrations.

**Topic evidence**

- **World Generation:** Produces Blender Python scripts arranging up to a hundred assets from text.
- **World Reconstruction:** Demonstrates reconstruction of detailed scenes from the Sintel movie.
- **Neural Rendering:** Generated scenes supply intermediate control signals to a generative video model.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2403.01248) — `primary_abstract`. Read the complete author abstract, including applications beyond text-to-scene generation.

**Limits / unresolved details**

- Reusable script-library learning is not persistent world-state memory or weight post-training.
- Spatial layout planning is not automatically action planning for an agent.

## Holodeck

- **Record:** `holodeck`
- **Reviewed:** 2026-10-22
- **README:** World Generation
- **Website:** World Generation, Agent Learning
- **Placement reason:** Language-generated 3D environments support navigation training in novel scene types.

**Topic evidence**

- **World Generation:** Builds indoor environments by selecting assets and solving LLM-generated spatial constraints.
- **Agent Learning:** Trains embodied navigation agents using generated environments without manually built scene data.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2312.09067) — `primary_abstract`. Read the complete author abstract and downstream navigation-training application.

**Limits / unresolved details**

- Scene layout generation alone is not a complete general-purpose world model.

## RoboGen

- **Record:** `robogen`
- **Reviewed:** 2026-10-22
- **README:** Agent Learning
- **Website:** Agent Learning, World Generation, Planning
- **Placement reason:** The propose-generate-learn cycle scales robot skill learning with generated simulations and supervision.

**Topic evidence**

- **Agent Learning:** Automatically acquires diverse robot policies and demonstrations through self-guided training.
- **World Generation:** Creates task-specific simulation environments, object sets and spatial layouts.
- **Planning:** Decomposes high-level tasks and selects motion planning, trajectory optimization or RL for individual subtasks.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/2311.01455) — `primary_abstract`. Read the complete author abstract and all phases of the learning pipeline.

**Limits / unresolved details**

- An endless stream of skill demonstrations is data generation, not streaming video generation.
- Training robot policies is covered by Agent Learning; no separate world-model post-training is claimed.

## World Programs

- **Record:** `world-programs`
- **Reviewed:** 2026-10-22
- **README:** Planning
- **Website:** Planning, World Reconstruction, Agent Learning
- **Placement reason:** Learned graph-rewrite actions and dynamics provide a simulator for compositional planning.

**Topic evidence**

- **Planning:** Uses induced world programs with search; the application is chemical synthesis planning.
- **World Reconstruction:** Induces unknown actions and transition dynamics from observed state-state pairs.
- **Agent Learning:** The formalism learns action policies and permits reinforcement learning with the induced simulator.

**Sources actually consulted**

- [Source 1](https://arxiv.org/abs/1912.13007) — `primary_abstract`. Read the complete author abstract.
- [Source 2](https://arxiv.org/html/1912.13007v1) — `full_text`. Read formalism and chemical-planning experiment sections, including learned policy and transition functions.

**Limits / unresolved details**

- The paper proposes a future community challenge, not a newly released benchmark suite.
- Graph rewriting and chemical reactions are not evidence of physics simulation.

## WorldStream

- **Record:** `worldstream`
- **Reviewed:** 2026-10-22
- **README:** World Generation
- **Website:** World Generation, Memory, Interactive, Streaming, World Editing
- **Placement reason:** Procedural world expansion, persistent records and language-driven edits support continued exploration.

**Topic evidence**

- **World Generation:** Hierarchical semantic plans drive local procedural generation of connected landscapes.
- **Memory:** Plans, object identities and accepted edits persist after geometry unloads and on revisits.
- **Interactive:** Language requests select executable NPC behaviors and update world state.
- **Streaming:** Movement-aware scheduling extends the map incrementally during exploration.
- **World Editing:** Users can modify existing regions or constrain future content through language.

**Sources actually consulted**

- [Source 1](https://krennic999.github.io/WorldStream/blog/) — `official_project`. Read system overview, planning, generation, persistence, interaction, latency and limitations sections.

**Limits / unresolved details**

- Streaming refers to spatial world expansion, not video generation.
- Warm-cache plan-to-visible latency is estimated at 2.3 seconds without sufficient hardware detail for an independent Real-Time claim.
- The article describes a procedural prototype; neural video integration is future work.

## StreamRender-H3

- **Record:** `streamrender-h3`
- **Reviewed:** 2026-10-22
- **README:** Real-Time
- **Website:** General World Model, Memory, Interactive, Real-Time, Acceleration, Long Video Generation, Streaming, Multi-Agent, Action Control, Neural Rendering, Post-Training
- **Placement reason:** An integrated engine-renderer loop makes continuous interactive video generation run in real time.

**Topic evidence**

- **General World Model:** Combines explicit world state, transitions, player actions and continuous observation generation through a replaceable engine interface.
- **Memory:** Persistent maps support revisits; sink frames preserve appearance across continuation windows.
- **Interactive:** New player inputs affect ongoing generated video within the running feedback loop.
- **Real-Time:** Reports real-time racing deployment, with 218 ms diffusion steps on eight GB200 GPUs.
- **Acceleration:** Kernel, cache and deployment changes reduce diffusion time by 3.67 times.
- **Long Video Generation:** Shows one-minute continuous generations and addresses accumulated continuation errors.
- **Streaming:** Generates and decodes successive chunks while new engine frames arrive.
- **Multi-Agent:** The same world updates player and rival cars driven by separate scripted drivers.
- **Action Control:** Keyboard or controller inputs steer, accelerate and brake the simulated car.
- **Neural Rendering:** Diffusion maps engine semantics to photorealistic frames.
- **Post-Training:** Fine-tunes MiniMax-H3 and distills generation to two steps.

**Sources actually consulted**

- [Source 1](https://nvlabs.github.io/Sana/Sol-Engine/StreamRender-H3/) — `official_project`. Read architecture, training, decoder, acceleration and deployment sections.

**Limits / unresolved details**

- Real-time figures depend on the reported multi-GPU deployment; decoder-only timings use one GB200.

## Streaming Code World Model

- **Record:** `streaming-cwm`
- **Reviewed:** 2026-10-22
- **README:** Streaming
- **Website:** Streaming, Long Video Generation, Acceleration, Neural Rendering, Post-Training
- **Placement reason:** A community extension makes proxy-conditioned video generation causal and accelerates it through distillation.

**Topic evidence**

- **Streaming:** Produces causal chunks from the start image, available proxies and previous chunks.
- **Long Video Generation:** Provides 60-second generation and noisy-history training to reduce long-stream drift.
- **Acceleration:** Four-step DMD achieves a reported nine-fold speedup over 35-step sampling.
- **Neural Rendering:** MiniMax-H3 renders videos conditioned on coarse code-world proxies.
- **Post-Training:** Includes causal diffusion-forcing fine-tuning and four-step DMD self-forcing training.

**Sources actually consulted**

- [Source 1](https://github.com/TingtingLiao/streaming-code-world-model/blob/main/README.md) — `official_project`. Read complete official README through the GitHub connector, including method, training, speed table and hardware.

**Limits / unresolved details**

- Explicitly not real time: one H200 takes 5.1 seconds to generate a 0.71-second chunk.
- This is a community extension, not an additional paper or the original Code World Model.
- Causal past-frame conditioning alone is not labeled a dedicated world-memory contribution.

## H3 Streaming VAE Decoder

- **Record:** `h3-streaming-vae`
- **Reviewed:** 2026-10-22
- **README:** Streaming
- **Website:** Streaming, Acceleration, Neural Rendering
- **Placement reason:** This component decodes arriving video latents causally and provides fused execution paths.

**Topic evidence**

- **Streaming:** Emits frames when a latent arrives, with no need for future latents.
- **Acceleration:** Offers fused decoder kernels and compiled paths for supported Blackwell hardware.
- **Neural Rendering:** Converts MiniMax-H3 or StreamRender-H3 latent representations into video frames.

**Sources actually consulted**

- [Source 1](https://github.com/SolarX-Team/H3-Streaming-VAE-Decoder/blob/main/README.md) — `official_project`. Read complete official README through the GitHub connector, including ownership of distilled weights and fused-kernel requirements.

**Limits / unresolved details**

- The project blog could not be fetched by the web tool; official repository documentation was successfully read.
- No Post-Training tag: it supports NVIDIA's separately distilled checkpoint, which is not trained in this repository.
- No standalone world state or action dynamics; no complete-world, interaction or real-time-throughput claim is inferred.

## Code Video Model

- **Record:** `code-video-model`
- **Reviewed:** 2026-10-22
- **README:** Neural Rendering
- **Website:** Neural Rendering, World Generation, World Editing, World Reconstruction, Physics, Benchmark
- **Placement reason:** Executable previs controls video structure while training-free diffusion conditioning preserves reference appearance.

**Topic evidence**

- **Neural Rendering:** A pretrained video model renders a code-built proxy using early-step conditioning.
- **World Generation:** Programs construct and animate scenes from prompts.
- **World Editing:** Code permits explicit object, layout and scene modifications.
- **World Reconstruction:** The project demonstrates 3D/4D reconstruction as a supported application.
- **Physics:** Program equations determine dynamics instead of leaving motion wholly implicit.
- **Benchmark:** Introduces CodeVideoBench: 22 cases over eight applications, with Structure, Style and Quality evaluation dimensions.

**Sources actually consulted**

- [Source 1](https://code-video-model.github.io/) — `official_project`. Read complete official project abstract and application gallery.
- [Source 2](https://github.com/code-video-model/CodeVideoModel/blob/main/README.md) — `official_project`. Read official Benchmark and Evaluation sections: task files, 22 cases/eight applications and per-dimension scoring script.

**Limits / unresolved details**

- The linked technical-report PDF exceeded the web tool's fetch-size limit; classification uses the successfully read official project and repository.
- The method is explicitly training-free; no Post-Training tag.
- Offline proxy-conditioned clips do not establish live interaction, streaming, real-time performance or long-video generation.
