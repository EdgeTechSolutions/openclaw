# 🧠 LLM Research Tracker

**Last updated: 12 March 2026 | Scan period: Mar 5–12, 2026 (cumulative from Feb 4)**

> Curated weekly digest of high-impact LLM research papers. Scored ⭐–⭐⭐⭐⭐⭐ by relevance to production LLM systems.

---

## 🏗️ Architecture Innovations

| Paper | Authors | Date | Score |
|-------|---------|------|-------|
| [Lost in Backpropagation: The LM Head is a Gradient Bottleneck](https://arxiv.org/abs/2603.10145) | Godey et al. | Mar 10, 2026 | ⭐⭐⭐⭐⭐ |
| [The Dual-Stream Transformer: Channelized Architecture for Interpretable Language Modeling](https://arxiv.org/abs/2603.07461) | Kerce et al. (DARPA) | Mar 8, 2026 | ⭐⭐⭐⭐ |
| [Linear-InfSA: Linear Transformers with Infinite Self-Attention](https://arxiv.org/abs/2603.00175) | Groffo et al. | Mar 2026 | ⭐⭐⭐⭐ |

### [Lost in Backpropagation: The LM Head is a Gradient Bottleneck](https://arxiv.org/abs/2603.10145)
**Godey et al. | Mar 10, 2026 | ⭐⭐⭐⭐⭐**

Shows the softmax bottleneck is also an OPTIMIZATION bottleneck. 95–99% of gradient norm is suppressed by the output layer due to rank-D projection of V-dimensional gradients. Makes trivial patterns unlearnable. Affects training dynamics of ALL LLMs.

> **Why it matters:** Identifies an inherent architectural flaw contributing to training inefficiencies at scale — calls for new LM head designs.

---

### [The Dual-Stream Transformer: Channelized Architecture for Interpretable Language Modeling](https://arxiv.org/abs/2603.07461)
**Kerce et al. (DARPA-funded) | Mar 8, 2026 | ⭐⭐⭐⭐**

Decomposes the residual stream into two functionally distinct components: a token stream (attention) and a context stream (FFN). Kronecker mixing strategy costs only 2.5% performance while enabling interpretability. Robust to attention amplification up to 16x.

> **Why it matters:** Foundation for interpretable language models where internal structure is exposed by design — crucial for safety/trust.

---

### [Linear-InfSA: Linear Transformers with Infinite Self-Attention](https://arxiv.org/abs/2603.00175)
**Groffo et al. | Mar 2026 | ⭐⭐⭐⭐**

Spectral reformulation treating attention as diffusion on a token graph. Linear-time variant keeps fixed-size state (independent of sequence length). 84.7% top-1 on ImageNet-1K in 4-layer ViT, 13x better throughput/energy than equal-depth ViT. Handles 332k tokens on single A100.

> **Why it matters:** Links self-attention to graph centrality (Katz, PageRank) for interpretable token weighting — with linear complexity.

---

## ⚡ Training Techniques

| Paper | Authors | Date | Score |
|-------|---------|------|-------|
| [CLIPO: Contrastive Learning in Policy Optimization Generalizes RLVR](https://arxiv.org/abs/2603.10101) | Cui et al. (Qwen) | Mar 10, 2026 | ⭐⭐⭐⭐⭐ |
| [V₀.₅: Generalist Value Model as Prior for Sparse RL Rollouts](https://arxiv.org/abs/2603.10848) | Zhang et al. | Mar 11, 2026 | ⭐⭐⭐⭐⭐ |
| [GOLF: Bootstrapping Exploration with Group-Level NL Feedback in RL](https://arxiv.org/abs/2603.04597) | Huang et al. | Mar 4, 2026 | ⭐⭐⭐⭐ |
| [ICRL: In-Context Reinforcement Learning for Tool Use in LLMs](https://arxiv.org/abs/2603.08068) | Zhao et al. | Mar 9, 2026 | ⭐⭐⭐⭐ |
| [OpenClaw-RL: Train Any Agent Simply by Talking](https://arxiv.org/abs/2603.10165) | Gen-Verse | Mar 12, 2026 | ⭐⭐⭐⭐ |

### [CLIPO: Contrastive Learning in Policy Optimization Generalizes RLVR](https://arxiv.org/abs/2603.10101)
**Cui et al. (Qwen) | Mar 10, 2026 | ⭐⭐⭐⭐⭐**

Adds contrastive loss over successful rollouts to RLVR, capturing invariant structure across correct reasoning paths. Mitigates step-level reasoning inconsistencies and hallucinatory artifacts from process-wrong but outcome-correct rollouts. Code at [github.com/Qwen-Applications/CLIPO](https://github.com/Qwen-Applications/CLIPO).

> **Why it matters:** Directly addresses hallucination in RLVR — from Qwen team, immediately applicable.

---

### [V₀.₅: Generalist Value Model as Prior for Sparse RL Rollouts](https://arxiv.org/abs/2603.10848)
**Zhang et al. | Mar 11, 2026 | ⭐⭐⭐⭐⭐**

Fuses pre-trained generalist value model prior with empirical mean from sparse rollouts via real-time statistical testing and dynamic budget allocation. Constructs robust advantage baselines that balance compute efficiency with low variance. Outperforms GRPO and DAPO by ~10% on six math benchmarks.

> **Why it matters:** Makes RLVR practical with just group_size=4 instead of 64+ — massive compute savings.

---

### [GOLF: Bootstrapping Exploration with Group-Level NL Feedback in RL](https://arxiv.org/abs/2603.04597)
**Huang et al. | Mar 4, 2026 | ⭐⭐⭐⭐**

Exploits group-level language feedback (external critiques + intra-group attempts) to guide targeted exploration. 2.2x improvement in sample efficiency vs scalar-reward-only RL. Jointly optimizes generation and refinement.

> **Why it matters:** Bridges the gap between rich NL feedback and scalar RL rewards — a virtuous cycle of improvement.

---

### [ICRL: In-Context Reinforcement Learning for Tool Use in LLMs](https://arxiv.org/abs/2603.08068)
**Zhao et al. | Mar 9, 2026 | ⭐⭐⭐⭐**

Eliminates SFT cold-start for tool use via RL-only framework using few-shot prompting during rollouts. Gradually reduces in-context examples to zero-shot. SOTA on reasoning and tool-use benchmarks.

> **Why it matters:** Data-efficient alternative to expensive SFT-then-RL pipeline for tool use.

---

### [OpenClaw-RL: Train Any Agent Simply by Talking](https://arxiv.org/abs/2603.10165)
**Gen-Verse | Mar 12, 2026 | ⭐⭐⭐⭐**

Framework that recovers next-state signals from ALL agent interactions (conversations, terminal, GUI, SWE) as online learning source. Hindsight-Guided On-Policy Distillation (OPD) provides token-level directional advantage supervision richer than scalar rewards. Asynchronous design: serve + judge + train simultaneously.

> **Why it matters:** Personal agents that improve simply by being used — universal RL across all interaction modalities.

---

## 📐 Efficiency & Quantization

*[Existing papers from Feb 4 – Mar 5 preserved — see note below]*

---

## 🛡️ Alignment & Safety

| Paper | Authors | Date | Score |
|-------|---------|------|-------|
| [VISA: Value Injection via Shielded Adaptation for Personalized LLM Alignment](https://arxiv.org/abs/2603.04822) | Chen et al. | Mar 5, 2026 | ⭐⭐⭐⭐ |
| [VRM: Variational Reward Modeling for Authentic Human Preferences](https://arxiv.org/abs/2603.04974) | Liu et al. | Mar 5, 2026 | ⭐⭐⭐⭐ |

### [VISA: Value Injection via Shielded Adaptation for Personalized LLM Alignment](https://arxiv.org/abs/2603.04822)
**Chen et al. | Mar 5, 2026 | ⭐⭐⭐⭐**

Closed-loop framework with high-precision value detector + semantic-to-value translator + GRPO-trained value-rewriter. Balances fine-grained value precision with semantic integrity preservation, mitigating alignment tax.

> **Why it matters:** Precise control over model's value expression without sacrificing factual consistency — outperforms GPT-4o.

---

### [VRM: Variational Reward Modeling for Authentic Human Preferences](https://arxiv.org/abs/2603.04974)
**Liu et al. | Mar 5, 2026 | ⭐⭐⭐⭐**

Models human evaluation process by incorporating high-dimensional objective weights and low-dimensional semantic features as latent variables via variational inference. Achieves tighter generalization error bound than traditional reward models.

> **Why it matters:** Addresses reward hacking by modeling HOW humans evaluate, not just WHAT they prefer.

---

## 🌐 Multimodal Models

| Paper | Authors | Date | Score |
|-------|---------|------|-------|
| [LLM2Vec-Gen: Generative Embeddings from Large Language Models](https://arxiv.org/abs/2603.10913) | BehnamGhader et al. | Mar 11, 2026 | ⭐⭐⭐⭐ |
| [UniCom: Unified Multimodal Modeling via Compressed Continuous Semantic Representations](https://arxiv.org/abs/2603.10702) | Zhao et al. | Mar 11, 2026 | ⭐⭐⭐⭐ |
| [RL-MoLoRA: Reinforcement Routing for Mixtures of LoRAs](https://arxiv.org/abs/2603.10160) | Qiu et al. (Meta) | Mar 12, 2026 | ⭐⭐⭐⭐ |
| [PRISM-Δ: Differential Subspace Steering for Prompt Highlighting](https://arxiv.org/abs/2603.10705) | Ge et al. | Mar 11, 2026 | ⭐⭐⭐ |

### [LLM2Vec-Gen: Generative Embeddings from Large Language Models](https://arxiv.org/abs/2603.10913)
**BehnamGhader et al. | Mar 11, 2026 | ⭐⭐⭐⭐**

Novel paradigm: learns to represent LLM's potential response instead of encoding input. Frozen LLM backbone, only unlabeled queries needed. +9.3% MTEB over best unsupervised teacher. 43.2% reduction in harmful content retrieval, 29.3% improvement in reasoning for embeddings.

> **Why it matters:** Transfers LLM capabilities (safety, reasoning) to embedding tasks — embeddings you can decode back into text.

---

### [UniCom: Unified Multimodal Modeling via Compressed Continuous Semantic Representations](https://arxiv.org/abs/2603.10702)
**Zhao et al. | Mar 11, 2026 | ⭐⭐⭐⭐**

Resolves the discretization dilemma: channel dimension reduction (not spatial downsampling) + attention-based semantic compressor. Transfusion architecture outperforms query-based designs. SOTA generation among unified models.

> **Why it matters:** Preserves rich semantic priors for exceptional controllability without relying on VAE.

---

### [RL-MoLoRA: Reinforcement Routing for Mixtures of LoRAs](https://arxiv.org/abs/2603.10160)
**Qiu et al. (Meta) | Mar 12, 2026 | ⭐⭐⭐⭐**

Addresses extreme imbalance in MoE-of-LoRAs routing where 1–2 LoRAs dominate. Uses RL-based routing to balance utilization across all LoRAs, unlocking full expressive power of MoLoRA.

> **Why it matters:** Makes MoE-of-LoRAs actually work as intended — critical for efficient fine-tuning.

---

### [PRISM-Δ: Differential Subspace Steering for Prompt Highlighting](https://arxiv.org/abs/2603.10705)
**Ge et al. | Mar 11, 2026 | ⭐⭐⭐**

Decomposes positive/negative cross-covariance matrices for discriminative steering directions. Continuous softplus importance weights per attention head. Compatible with FlashAttention.

> **Why it matters:** Practical prompt highlighting with minimal fluency cost — useful for RAG and long-context retrieval.

---

## 🧠 Reasoning & Agents

| Paper | Authors | Date | Score |
|-------|---------|------|-------|
| [KARL: Knowledge Agents via Reinforcement Learning](https://arxiv.org/abs/2603.05218) | Chang, Drozdov et al. (Databricks/Cornell) | Mar 5, 2026 | ⭐⭐⭐⭐⭐ |
| [RetroAgent: From Solving to Evolving via Retrospective Dual Intrinsic Feedback](https://arxiv.org/abs/2603.08561) | Zhang et al. | Mar 9, 2026 | ⭐⭐⭐⭐ |
| [HCAPO: Hindsight Credit Assignment for Long-Horizon LLM Agents](https://arxiv.org/abs/2603.08754) | Tan et al. | Mar 7, 2026 | ⭐⭐⭐⭐ |
| [Causal Concept Graphs (CCG) for Stepwise Reasoning](https://arxiv.org/abs/2603.10377) | Mohammad et al. | Mar 11, 2026 | ⭐⭐⭐⭐ |

### [KARL: Knowledge Agents via Reinforcement Learning](https://arxiv.org/abs/2603.05218)
**Chang, Drozdov et al. (Databricks/Cornell) | Mar 5, 2026 | ⭐⭐⭐⭐⭐**

Enterprise search agent trained via multi-task RL on KARLBench (6 search regimes). Iterative large-batch off-policy RL paradigm. Pareto-optimal vs Claude 4.6 and GPT 5.2 on cost-quality and latency-quality tradeoffs. Surpasses strongest closed models with sufficient test-time compute.

> **Why it matters:** Proves tailored synthetic data + multi-task RL can beat frontier closed models for enterprise search — at lower cost.

---

### [RetroAgent: From Solving to Evolving via Retrospective Dual Intrinsic Feedback](https://arxiv.org/abs/2603.08561)
**Zhang et al. | Mar 9, 2026 | ⭐⭐⭐⭐**

Online RL framework with hindsight self-reflection producing dual intrinsic feedback: numerical (incremental subtask completion) and language (reusable lessons in memory). SimUtil-UCB balances relevance, utility, and exploration. +18.3% ALFWorld, +27.1% Sokoban over GRPO.

> **Why it matters:** Agents that evolve through experience, not just solve static tasks.

---

### [HCAPO: Hindsight Credit Assignment for Long-Horizon LLM Agents](https://arxiv.org/abs/2603.08754)
**Tan et al. | Mar 7, 2026 | ⭐⭐⭐⭐**

First framework integrating hindsight credit assignment into LLM agents. Uses LLM as post-hoc critic to refine step-level Q-values. +7.7% WebShop, +13.8% ALFWorld over GRPO.

> **Why it matters:** Solves sparse reward problem in long-horizon agent tasks.

---

### [Causal Concept Graphs (CCG) for Stepwise Reasoning](https://arxiv.org/abs/2603.10377)
**Mohammad et al. | Mar 11, 2026 | ⭐⭐⭐⭐**

DAG over sparse interpretable latent features where edges capture causal dependencies. Combines task-conditioned SAEs with DAGMA structure learning. CFS=5.654 vs ROME tracing (3.382), SAE-only (2.479).

> **Why it matters:** Goes beyond localizing concepts to understanding how they INTERACT during reasoning.

---

*Next update: ~Mar 19, 2026*
