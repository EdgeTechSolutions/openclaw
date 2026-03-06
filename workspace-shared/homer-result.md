# LLM & Foundation Model Research Tracker

**Last updated: 5 March 2026 | Scan period: Feb 26 – Mar 5, 2026 (cumulative from Feb 19)**

---

## 🏗️ Architecture Innovations

| Paper | Date | ⭐ | Key Contribution |
|-------|------|-----|------------------|
| [Recursive Language Models (RLMs)](https://arxiv.org/abs/2512.24601) — Zhang et al. | Dec 2025 | ⭐⭐⭐⭐⭐ | Inference strategy that treats long prompts as external environment; LLM recursively calls itself over snippets. Enables near-infinite context processing via REPL. **Why it matters:** Paradigm-shifting approach to context length limitations. Already being reproduced and integrated into frameworks like LangGraph. |
| [Qwen3.5-397B-A17B](https://qwenlm.github.io/) — Alibaba | Feb 2026 | ⭐⭐⭐⭐⭐ | Flagship 397B-parameter MoE model with 17B active parameters. Native multimodal, 256K context, 201 languages. **Why it matters:** Largest open-weight MoE demonstrating that massive sparse models can be practical for deployment. |
| [Qwen3.5 Small Series](https://qwenlm.github.io/) — Alibaba | Feb-Mar 2026 | ⭐⭐⭐⭐ | Family of native multimodal MoE models from 0.8B to 35B parameters. The 9B model beats OpenAI's gpt-oss-120B on some benchmarks while running on standard laptops. **Why it matters:** Proves edge deployment of capable multimodal models is viable today. |
| [Kimi K2.5](https://moonshot.ai/) — Moonshot AI | Jan 2026 | ⭐⭐⭐⭐ | 1T-parameter MoE (384 experts, 8 active per token, 32B active). 61-layer architecture with MoonViT 400M vision encoder. Trained with PARL RL. 76.8% SWE-Bench. **Why it matters:** Trillion-parameter open-weight model with native vision and agentic capabilities. |
| [DeepSeek-R1](https://arxiv.org/abs/2501.12948) — DeepSeek-AI | Jan 2025 | ⭐⭐⭐⭐⭐ | First open-weight reasoning model trained via pure RL without supervised fine-tuning. Matches o1 performance on math and coding benchmarks. **Why it matters:** Demonstrated that reasoning capabilities can emerge from RL alone, democratizing access to o1-class models. |
| [Kimi k1.5](https://arxiv.org/abs/2501.12599) — Moonshot AI | Jan 2025 | ⭐⭐⭐⭐ | Scaling RL with LLMs. Long-horizon reasoning with multimodal capabilities. Strong performance on math, code, and vision tasks. **Why it matters:** Showed competitive reasoning model training at scale outside major labs. |
| [Beyond Language Modeling: Multimodal Pretraining](https://arxiv.org/abs/2603.03276) — Tong et al. | Mar 2026 | ⭐⭐⭐⭐ | Controlled from-scratch pretraining experiments showing MoE architecture harmonizes scaling asymmetry between language and vision. **Why it matters:** Critical empirical clarity on native multimodal model design space. |
| [Titans: Learning to Memorize at Test Time](https://arxiv.org/abs/2501.00663) — Google | Dec 2024 | ⭐⭐⭐⭐ | Neural long-term memory module that learns to memorize historical context. Combines short-term attention with persistent memory. **Why it matters:** Addresses quadratic attention cost while enabling effective long-context modeling. |

---

## ⚡ Training Techniques

| Paper | Date | ⭐ | Key Contribution |
|-------|------|-----|------------------|
| [Adaptive Drafter for RL Training](https://arxiv.org/abs/2511.16665) — Hu, Yang et al. (MIT/NVIDIA) | Nov 2025 | ⭐⭐⭐⭐⭐ | Uses idle GPU time during RL rollouts to train speculative drafter model. Doubles training speed with zero accuracy loss. **Why it matters:** Lossless 2x RL training speedup by leveraging wasted compute. Full-stack system, immediately practical. |
| [CUDA Agent](https://arxiv.org/abs/2602.24286) — ByteDance/Tsinghua | Feb 2026 | ⭐⭐⭐⭐ | Large-scale agentic RL system for CUDA kernel expertise. Open-sourced dataset (CUDA-Agent-Ops-6K). **Why it matters:** Shows LLMs can learn to write high-performance GPU kernels via RL. |
| [SWE-RL](https://arxiv.org/abs/2502.18449) — Meta | Feb 2025 | ⭐⭐⭐⭐⭐ | First RL-based reasoning for real-world software engineering. Llama3-SWE-RL-70B achieves 41% on SWE-bench Verified. **Why it matters:** Best medium-sized LLM performance on real GitHub issues, comparable to GPT-4o. |
| [StitchCUDA](https://arxiv.org/abs/2603.02637) — | Mar 2026 | ⭐⭐⭐ | Multi-agent framework with rubric-based agentic RL for GPU programming. Prevents reward hacking. **Why it matters:** Complementary to CUDA Agent, focusing on multi-agent approach and reward hacking prevention. |
| [s1: Simple Test-Time Scaling](https://arxiv.org/abs/2501.19393) — | Jan 2025 | ⭐⭐⭐⭐ | Simplest approach to test-time scaling. Budget forcing controls compute. s1-32B exceeds o1-preview on MATH/AIME. **Why it matters:** Demonstrates strong reasoning with minimal resources—1000 examples and simple techniques. |
| [Training LLMs to Reason Efficiently](https://arxiv.org/abs/2502.04463) — | Feb 2025 | ⭐⭐⭐⭐ | Uses RL to train models to dynamically allocate inference compute based on task complexity. **Why it matters:** Achieves substantial efficiency gains while maintaining accuracy. |
| [Self-Rewarding Correction for Mathematical Reasoning](https://arxiv.org/abs/2502.19613) — | Feb 2025 | ⭐⭐⭐ | Two-staged framework for self-rewarding reasoning models using only self-generated data. **Why it matters:** Enables autonomous error detection and correction without external feedback. |
| [VEM: Environment-Free Exploration for GUI Agents](https://arxiv.org/abs/2502.18906) — | Feb 2025 | ⭐⭐⭐ | Value Environment Model enables GUI agent training without costly environment interactions. **Why it matters:** State-of-the-art GUI automation without interaction costs. |

---

## 📐 Efficiency & Quantization

| Paper | Date | ⭐ | Key Contribution |
|-------|------|-----|------------------|
| [NVFP4 Quantization on Blackwell](https://arxiv.org/abs/2601.20088) — Microsoft/NVIDIA | Jan 2026 | ⭐⭐⭐⭐⭐ | E2M1 FP4 codebook with blockwise FP8 scaling. DeepSeek-V3.2 on GB200 serves 16x more users per GPU. DeepInfra: $0.20→$0.05 per M tokens. **Why it matters:** Production-ready 4-bit inference at massive scale. 16x serving improvement is transformative. |
| [CoT-Valve: Length-Compressible Chain-of-Thought](https://arxiv.org/abs/2502.09601) — | Feb 2025 | ⭐⭐⭐⭐ | Enables models to generate reasoning chains of varying lengths. Reduces inference overhead dynamically. **Why it matters:** Controllable CoT length allows efficiency-quality tradeoffs at inference time. |
| [FP4 Quantization for LLM Training](https://arxiv.org/abs/2501.17116) — | Jan 2025 | ⭐⭐⭐⭐ | First FP4 training framework for LLMs with differentiable quantization estimator. Scales to 13B parameters. **Why it matters:** Foundation for efficient ultra-low precision training on next-gen hardware. |
| [TeleRAG: Efficient RAG with Lookahead Retrieval](https://arxiv.org/abs/2502.20969) — | Feb 2025 | ⭐⭐⭐ | Lookahead retrieval reduces RAG latency by overlapping computation. **Why it matters:** Practical speedup for production RAG systems. |
| [Lottery LLM Hypothesis](https://arxiv.org/abs/2502.17535) — | Feb 2025 | ⭐⭐⭐ | Hypothesizes smaller "lottery LLMs" can match larger models with reasoning and tools. **Why it matters:** Challenges assumptions about model compression and what capabilities to preserve. |
| [The Curse of Depth in LLMs](https://arxiv.org/abs/2502.05795) — | Feb 2025 | ⭐⭐⭐ | Identifies why deep layers are ineffective in modern LLMs. Proposes LayerNorm Scaling fix. **Why it matters:** Explains and addresses widespread training inefficiency in deep networks. |
| [Native Sparse Attention](https://arxiv.org/abs/2502.11089) — DeepSeek | Feb 2025 | ⭐⭐⭐⭐ | Hardware-aligned sparse attention enabling efficient long-context modeling. **Why it matters:** Practical sparse attention that's trainable end-to-end. |

---

## 🛡️ Alignment & Safety

| Paper | Date | ⭐ | Key Contribution |
|-------|------|-----|------------------|
| [GuardAlign: Test-time Safety Alignment in VLMs](https://arxiv.org/abs/2602.24027) — | Feb 2026 | ⭐⭐⭐⭐ | Inference-time safety alignment for VLMs. No retraining. Highest helpfulness while ensuring safety. **Why it matters:** Zero-cost safety for multimodal models at inference time. |
| [Multilingual Safety Alignment via Sparse Weight Editing](https://arxiv.org/abs/2602.22554) — | Feb 2026 | ⭐⭐⭐⭐ | Addresses safety disparities where low-resource languages bypass guardrails. Uses sparse editing instead of multilingual SFT. **Why it matters:** Critical for global LLM deployment where safety must work in all languages. |
| [Hidden Risks of Large Reasoning Models](https://arxiv.org/abs/2502.12659) — | Feb 2025 | ⭐⭐⭐⭐ | Comprehensive safety assessment of DeepSeek-R1. Reveals safety gaps in open reasoning models. **Why it matters:** Documents that stronger reasoning correlates with greater potential harm. |
| [Defensive Refusal Bias](https://arxiv.org/abs/2603.01246) — | Mar 2026 | ⭐⭐⭐ | Shows safety alignment fails cyber defenders—legitimate security queries refused while harmful outputs slip through. **Why it matters:** Important practical finding about over-refusal harming legitimate use. |
| [Model Tampering Attacks](https://arxiv.org/abs/2502.05209) — | Feb 2025 | ⭐⭐⭐ | Demonstrates attacks that enable more rigorous LLM capability evaluations. **Why it matters:** Methodological advance for safety evaluations. |

---

## 🌐 Multimodal Models

| Paper | Date | ⭐ | Key Contribution |
|-------|------|-----|------------------|
| [Phi-4-Reasoning-Vision-15B](https://arxiv.org/abs/2603.01743) — Microsoft | Mar 2026 | ⭐⭐⭐⭐⭐ | Small multimodal reasoning model (15B) with mid-fusion vision. High-fidelity vision reasoning for agents and scientific workflows. **Why it matters:** State-of-the-art SLM with vision + reasoning. Proves small models can do structured multi-step visual reasoning. |
| [Smol2Operator](https://huggingface.co/) — Hugging Face | Feb-Mar 2026 | ⭐⭐⭐⭐ | Fully open-source pipeline to train 2.2B VLM into agentic GUI coder. End-to-end from data to deployment. **Why it matters:** Democratizes agentic GUI automation with tiny model. Fully open pipeline. |
| [Qwen3-Omni](https://arxiv.org/abs/2509.17765) — Alibaba | Sep 2025 | ⭐⭐⭐⭐ | Single model matching SOTA across text, image, audio, video without degradation vs single-modal counterparts. **Why it matters:** First no-compromise unified multimodal model. |
| [Qwen2.5-VL](https://arxiv.org/abs/2502.13923) — Alibaba | Feb 2025 | ⭐⭐⭐⭐ | Vision-language model with strong OCR, document understanding, and video capabilities. **Why it matters:** Strong open multimodal model for real-world vision tasks. |

---

## 🧠 Reasoning & Scaling

| Paper | Date | ⭐ | Key Contribution |
|-------|------|-----|------------------|
| [Gemini Deep Think / Aletheia](https://deepmind.google/) — Google DeepMind | Jan-Feb 2026 | ⭐⭐⭐⭐⭐ | Long-horizon research agent on Gemini 3. 90% on IMO-ProofBench Advanced. Solved 6 of 10 FirstProof open math problems. **Why it matters:** Demonstrates AI solving genuine open research problems, not just benchmarks. Better reasoning at lower compute is the holy grail. |
| [Dyve: Dynamic Process Verification](https://arxiv.org/abs/2502.11157) — | Feb 2025 | ⭐⭐⭐⭐ | Integrates fast/slow thinking for reasoning error detection. Step-wise consensus-filtered process supervision. **Why it matters:** Significant improvement in reasoning verification and Best-of-N settings. |
| [Huginn: Recurrent Depth for Test-Time Scaling](https://arxiv.org/abs/2502.05171) — UMD | Feb 2025 | ⭐⭐⭐⭐ | Iterates recurrent block for arbitrary depth at test-time. Implicit latent reasoning without extra tokens. **Why it matters:** Novel paradigm—scaling compute without token generation. |
| [LLM Post-Training Survey](https://arxiv.org/abs/2502.21321) — | Feb 2025 | ⭐⭐⭐⭐ | Comprehensive survey of fine-tuning, RL, and test-time scaling for reasoning models. **Why it matters:** Essential reference for understanding post-training methodology landscape. |
| [Towards Large Reasoning Models](https://arxiv.org/abs/2501.09686) — | Jan 2025 | ⭐⭐⭐⭐ | Survey of reinforced reasoning with LLMs. Covers RL paradigms for reasoning. **Why it matters:** Roadmap for building reasoning-capable models. |
| [Truth as a Trajectory](https://arxiv.org/abs/2603.01326) — | Mar 2026 | ⭐⭐⭐ | Analyzes internal representations for LLM reasoning. Studies truth value propagation through layers. **Why it matters:** Interpretability insight into reasoning mechanics. |
| [Scale-Distribution Decoupling](https://arxiv.org/abs/2502.15499) — | Feb 2025 | ⭐⭐⭐ | Stabilizes LLM training by decoupling scale and distribution. Prevents gradient explosion in deep networks. **Why it matters:** Practical training stability improvement for large models. |

---

*Maintained by automated weekly scan. Next update: ~Mar 12, 2026.*
