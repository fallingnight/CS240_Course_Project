# Topic 3 Proposal Review / Topic 3 提案审查

## Overview / 概述

This review checks the **Topic 3: Influence Maximization** proposal (both English and Chinese versions) against the requirements in the CS240 Course Project Announcement.

> [!NOTE]
> The proposal deadline is **May 17**, and the document should be roughly **1–2 pages**.

---

## Requirements Checklist / 要求清单

The Announcement §4.A specifies **6 required sections** for the proposal. Here's how both versions stack up:

| # | Required Section | English (`Proposal.tex`) | Chinese (`Proposal.zh.tex`) | Status |
|---|---|---|---|---|
| 1 | **Topic Selection** — chosen topic, brief motivation, application background | ✅ §1 "Topic Selection" | ✅ §1 "选题说明" | ✅ Pass |
| 2 | **Problem Formulation** — clear problem definition, input/output, optimization objective | ✅ §2 "Problem Formulation" | ✅ §2 "问题形式化" | ✅ Pass |
| 3 | **Related Work** — ≥2 papers, specify which paper/method to reproduce | ✅ §3 "Related Work" (3 papers, Kempe et al. as main) | ✅ §3 "相关工作" (3 papers, Kempe et al. as main) | ✅ Pass |
| 4 | **Algorithm and Technical Plan** — core algorithms, implementation approach, datasets/evaluation | ✅ §4 "Algorithm and Technical Plan" | ✅ §4 "算法与技术计划" | ✅ Pass |
| 5 | **Project Scope and Expected Goals** — what to reproduce, optional extensions | ✅ §5 "Project Scope and Expected Goals" | ✅ §5 "项目范围与预期目标" | ✅ Pass |
| 6 | **Team Information** — member list, division of contributions | ✅ §6 "Team Information" (table format) | ✅ §6 "团队信息" (list format) | ✅ Pass |

> [!TIP]
> **All 6 required sections are present in both versions.** The proposal structurally satisfies the announcement requirements.

---

## Detailed Section Analysis / 逐节详细分析

### 1. Topic Selection / 选题说明

**English version:**

- Clearly states Topic 3: Influence Maximization
- Provides motivation: viral marketing, social-network analysis
- Highlights algorithmic connection to classical approximation algorithms
- Narrows scope to **distributed influence maximization with submodular optimization**

**Chinese version:**

- Same content, additionally mentions multi-agent coordination and distributed optimization perspectives (多智能体网络中的协同决策)
- Slightly richer motivation connecting to control/multi-agent research

**评价：** 两个版本均满足要求。中文版在动机部分比英文版更丰富一些，提到了多智能体决策与控制的联系。

---

### 2. Problem Formulation / 问题形式化

**Both versions include:**

- ✅ Graph $G=(V,E)$ with propagation probabilities
- ✅ Formal optimization objective: $\max_{S \subseteq V, |S| \leq k} \sigma(S)$
- ✅ Input/output description (graph + parameters → seed set)
- ✅ Submodularity property with formal inequality
- ✅ NP-hardness and $(1-1/e)$ approximation guarantee

**评价：** 形式化定义非常清晰完整，包括了输入/输出描述和优化目标，完全满足要求。

---

### 3. Related Work / 相关工作

**Both versions cite 3 papers:**

| Paper | Role |
|---|---|
| Kempe, Kleinberg, Tardos | **Main paper for reproduction** — introduced influence maximization, proved NP-hardness, greedy $(1-1/e)$ guarantee |
| Nemhauser, Wolsey, Fisher | Theoretical foundation — classical submodular maximization result |
| Leskovec et al. (CELF) | Algorithmic acceleration — lazy greedy optimization |

**评价：** 超出最低要求（至少 2 篇），列出 3 篇。明确指出 Kempe et al. 为主要复现论文。满足要求。

> [!NOTE]
> **Minor suggestion / 小建议：** Both versions lack formal citations (no `\cite{}` or bibliography). For a formal proposal, consider adding a `\begin{thebibliography}` section or a `.bib` file with proper references. This is not strictly required by the announcement, but would improve professionalism.
>
> 两个版本都没有使用正式的引用格式（没有 `\cite{}` 或参考文献列表）。虽然 announcement 没有明确要求，但添加正式参考文献会更专业。

---

### 4. Algorithm and Technical Plan / 算法与技术计划

**Both versions describe 5 methods:**

1. Random baseline（随机基线）
2. Degree baseline（度数中心性基线）
3. Greedy influence maximization（经典贪心算法）
4. CELF lazy greedy（CELF 懒惰贪心）
5. Distributed extension（分布式扩展）

**Technical details covered:**

- ✅ Core algorithms: greedy, CELF, distributed consensus
- ✅ Implementation approach: Monte Carlo simulation for influence spread
- ✅ Datasets: synthetic graphs (Erdős–Rényi, Barabási–Albert, Watts–Strogatz) + small real network
- ✅ Evaluation metrics: influence spread, runtime, scalability, sensitivity to $k$

**评价：** 算法方案详细，涵盖核心算法（贪心、CELF）、实现方式（Monte Carlo）、数据集和评估指标。完全满足要求。

---

### 5. Project Scope and Expected Goals / 项目范围与预期目标

**Core goals (both versions):**

1. Greedy > random/degree baselines in influence spread
2. CELF ≈ greedy quality but faster
3. Influence grows with $k$, marginal gains decrease (submodularity)
4. Distributed scheme shows communication–quality tradeoff

**Optional extensions (both versions):**

- Different propagation probabilities
- Monte Carlo sample size stability analysis
- Communication-limited distributed selection
- Connection to distributed optimization theory

**评价：** 核心目标和可选拓展均有明确描述，满足要求。

---

### 6. Team Information / 团队信息

| Member | English Version | Chinese Version |
|---|---|---|
| Yixin Chen / 陈亦新 | Modeling and theory; Problem formulation and related work | 问题建模、相关工作与理论分析 |
| Bichi Zhang / 张弼弛 | Algorithms; Greedy, CELF, and complexity analysis | 贪心算法、CELF 算法与复杂度分析 |
| Yaoqin Ye / 叶瑶勤 | Experiments; Implementation, plots, and distributed extension | 实验实现、可视化与分布式扩展实验 |

**评价：** 分工明确，满足要求。英文版用表格形式，中文版用列表形式，两者都清楚。

---

## Overall Verdict / 总体评价

> [!IMPORTANT]
>
> ### ✅ The proposal **fully satisfies** all announcement requirements
>
> ### ✅ 该提案**完全满足** announcement 中的所有要求

### Strengths / 优点

1. **Structure matches perfectly** — All 6 required sections present and well-organized
2. **Mathematical rigor** — Formal problem definition with optimization objective and submodularity proof
3. **Comprehensive algorithm plan** — 5 methods from baseline to advanced (distributed)
4. **Clear reproduction target** — Kempe et al. explicitly named as the main paper
5. **Reasonable scope** — Core goals are achievable; extensions are well-thought-out
6. **Good team division** — Theory / Algorithm / Experiments split is logical

### Minor Suggestions for Improvement / 改进建议

| # | Suggestion | Priority |
|---|---|---|
| 1 | Add a formal bibliography/references section (`\bibliographystyle` + `\bibliography` or `thebibliography`) | Low — not required but more professional |
| 2 | English version: consider adding the multi-agent/control motivation that the Chinese version has | Low — nice to have |
| 3 | Consider mentioning specific real-world datasets by name (e.g., NetHEPT, Wiki-Vote, Epinions) instead of just "one small real network" | Low — shows preparation |
| 4 | Page count: verify both compiled PDFs are within the 1–2 page guideline | Medium — check PDF output |

---

## English–Chinese Consistency / 中英文一致性

The two versions are **highly consistent** in content and structure. Minor differences:

| Aspect | English | Chinese | Impact |
|---|---|---|---|
| Motivation depth | Standard | Richer (multi-agent perspective) | Minor — Chinese is slightly better |
| Team info format | Table with `\toprule/\midrule/\bottomrule` | Itemized list | Cosmetic only |
| Font size | 10pt | 11pt | Cosmetic only |
| Margins | 0.72in | 1in | Affects page count |

> [!TIP]
> Both versions convey the same technical content. The minor differences are stylistic and do not affect compliance with the announcement requirements.
