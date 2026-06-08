# CS240 课程项目

本仓库包含 **CS240：算法设计与分析，2026 年春季学期** 的课程项目材料。

## 项目选题

**通信受限的分布式影响力最大化**

本项目基于 **Topic 3: Influence Maximization**。项目目标是展示经典的子模优化
与贪心近似算法如何用于现代网络传播问题，并进一步研究：当中心化贪心选择被
“局部贪心 + 有限候选通信”的分布式方案替代时，影响范围、运行时间和通信量会如何变化。

## 已实现方法

- 随机种子 baseline
- 加权出度 baseline
- PageRank baseline
- Independent Cascade 模型下的中心化 Monte Carlo greedy
- CELF / lazy greedy：利用缓存边际收益上界减少重复 spread evaluation
- GreeDI-style 分布式 greedy：每个 worker 只发送本地候选集合

## 项目结构

| 路径 | 说明 |
| --- | --- |
| `src/graphs.py` | 合成图和小型真实图生成，并设置 IC 传播概率 |
| `src/simulation.py` | Independent Cascade 模拟与 Monte Carlo spread 估计 |
| `src/baselines.py` | random、degree、PageRank 以及固定 seed set 评估 |
| `src/greedy.py` | 中心化 greedy 和 CELF/lazy greedy |
| `src/distributed.py` | GreeDI-style 本地候选共享和节点划分 |
| `src/results.py` | 共享的 `SelectionResult` 和 seed set 类型定义 |
| `src/algorithms.py` | 兼容导出层，统一 re-export 各类算法 |
| `src/metrics.py` | quality ratio、通信代理指标和 marginal gain 工具 |
| `src/experiments.py` | 端到端实验入口 |
| `src/plotting.py` | 图像生成 |
| `src/graph_visualization.py` | small 规模图结构可视化 |
| `tests/` | 轻量级单元测试 |
| `outputs/` | 生成的 CSV 结果和实验图 |
| `references/` | 项目参考论文 |

## 想改某部分代码时看哪里

| 想修改的内容 | 对应文件 |
| --- | --- |
| IC 传播逻辑或 Monte Carlo spread 估计 | `src/simulation.py` |
| 图类型或传播概率规则 | `src/graphs.py` |
| random / degree / PageRank baseline | `src/baselines.py` |
| 中心化 greedy 选种子逻辑 | `src/greedy.py` |
| CELF 懒惰贪心的优先队列逻辑 | `src/greedy.py` |
| 分布式 `m` 个分区和本地候选预算 `q` | `src/distributed.py` |
| 实验用例、CSV 指标、`m/q` sweep | `src/experiments.py` |
| 要画哪些图以及图的格式 | `src/plotting.py` |
| small 图结构可视化 | `src/graph_visualization.py` |
| spread/runtime/evaluations 等统一结果字段 | `src/results.py` |

`src/algorithms.py` 保留了旧的统一导入方式，但新的代码建议直接从对应功能模块导入。

## 环境配置

创建并激活虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装依赖和本地包：

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
```

## 运行实验

```powershell
python src/experiments.py --seed 7 --simulations 40
```

该命令会生成：

- `outputs/influence_maximization/influence_results.csv`
- `outputs/influence_maximization/figures/estimated_spread.png`
- `outputs/influence_maximization/figures/quality_ratio_to_greedy.png`
- `outputs/influence_maximization/figures/runtime_seconds.png`
- `outputs/influence_maximization/figures/spread_evaluations.png`
- `outputs/influence_maximization/figures/transmitted_candidates.png`

默认的 `--scale small` 使用 ER/BA/WS 的 `n = 40, 70`，并保留固定 34 节点
Karate 图。使用 `--scale large` 会运行 ER/BA/WS 的 `n = 50, 100, 200`；
large 结果会单独保存为 `outputs/influence_maximization/influence_results_large.csv`
和 `outputs/influence_maximization/figures/*_large.png`。合成图规模可以通过
`--sizes` 手动指定，`--no-progress` 可以关闭进度条。

只有在明确想单独保存某次运行时，才需要使用 `--output-dir SOME_PATH`，例如快速
smoke test。

分布式实验中的主要变量是：

- `m`：分区数量，当前测试 `2`、`4`、`8`
- `q`：每个 worker 返回的本地候选预算，当前测试 `k`、`2k`、`5k`

主要报告指标包括 estimated spread、runtime、spread evaluations、相对于中心化 greedy
的 distributed quality ratio，以及 transmitted candidate count。

CSV 中有两个 spread 字段：

- `selection_estimated_spread`：算法选 seed 时内部使用的 spread 估计。
- `estimated_spread`：用统一 evaluation seed 对最终 seed set 重新评估得到的 spread，
  用于计算 `quality_ratio_to_greedy`。

## 结果图

最新生成的实验图保存在 `outputs/influence_maximization/figures/`。

`comparisons/` 子目录保存所有报告指标的节点数比较和方法比较柱状图。`graphs/`
子目录保存由 `src/graph_visualization.py` 生成的 small 图结构可视化。

<table>
  <tr>
    <td><img src="outputs/influence_maximization/figures/estimated_spread.png" alt="Estimated IC spread"></td>
    <td><img src="outputs/influence_maximization/figures/quality_ratio_to_greedy.png" alt="Quality ratio to greedy"></td>
  </tr>
  <tr>
    <td align="center">Estimated IC spread</td>
    <td align="center">相对于中心化 greedy 的质量比</td>
  </tr>
  <tr>
    <td><img src="outputs/influence_maximization/figures/runtime_seconds.png" alt="Runtime"></td>
    <td><img src="outputs/influence_maximization/figures/spread_evaluations.png" alt="Spread evaluations"></td>
  </tr>
  <tr>
    <td align="center">运行时间</td>
    <td align="center">Spread evaluations</td>
  </tr>
  <tr>
    <td colspan="2"><img src="outputs/influence_maximization/figures/transmitted_candidates.png" alt="Transmitted candidates"></td>
  </tr>
  <tr>
    <td colspan="2" align="center">Transmitted candidates</td>
  </tr>
</table>

## 运行测试

```powershell
python -m pytest
```

如果全局 Python 环境没有安装依赖，使用项目虚拟环境：

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## 说明

本实现刻意保持在课程项目可复现范围内，而不是追求 state-of-the-art 系统性能。
PaC-IM、IMM/RIS、GreediRIS，以及近期 MapReduce/adaptive submodular algorithms
主要作为 related work 和 optional extension 背景。
