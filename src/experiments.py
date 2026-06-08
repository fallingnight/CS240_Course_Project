"""Experiment runner for distributed influence maximization."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from baselines import (
    degree_selection,
    evaluate_fixed_seed_set,
    pagerank_selection,
    random_selection,
)
from distributed import distributed_greedy_influence_maximization
from graphs import make_benchmark_graph
from greedy import celf_influence_maximization, greedy_influence_maximization
from metrics import quality_ratio
from plotting import save_metric_plots
from simulation import estimate_spread


ExperimentCase = tuple[str, int, int]


def experiment_cases(
    scale: str, synthetic_sizes: list[int] | None = None
) -> list[ExperimentCase]:
    """Return benchmark cases for the requested experiment scale."""
    synthetic_sizes = _validate_synthetic_sizes(synthetic_sizes)
    if scale == "small":
        if synthetic_sizes is not None:
            return [
                *[("erdos_renyi", size, 5) for size in synthetic_sizes],
                *[("barabasi_albert", size, 5) for size in synthetic_sizes],
                *[("watts_strogatz", size, 5) for size in synthetic_sizes],
                ("karate", 34, 5),
            ]
        return [
            ("erdos_renyi", 40, 5),
            ("erdos_renyi", 70, 6),
            ("barabasi_albert", 40, 5),
            ("barabasi_albert", 70, 6),
            ("watts_strogatz", 40, 5),
            ("watts_strogatz", 70, 6),
            ("karate", 34, 5),
        ]
    if scale == "large":
        synthetic_sizes = synthetic_sizes or [50, 100, 200]
        return [
            *[("erdos_renyi", size, 10) for size in synthetic_sizes],
            *[("barabasi_albert", size, 10) for size in synthetic_sizes],
            *[("watts_strogatz", size, 10) for size in synthetic_sizes],
            ("karate", 34, 5),
        ]
    raise ValueError(f"Unknown experiment scale: {scale}")


def _validate_synthetic_sizes(synthetic_sizes: list[int] | None) -> list[int] | None:
    if synthetic_sizes is None:
        return None
    if any(size <= 0 for size in synthetic_sizes):
        raise ValueError("synthetic graph sizes must be positive.")
    return synthetic_sizes


def _run_algorithm(
    algorithm_name: str,
    graph,
    k: int,
    simulations: int,
    experiment_seed: int,
    baseline_seed: int,
    case_id: int,
):
    if algorithm_name == "random":
        return evaluate_fixed_seed_set(
            graph,
            random_selection(graph, k, seed=baseline_seed),
            simulations=simulations,
            seed=baseline_seed,
        )
    if algorithm_name == "degree":
        return evaluate_fixed_seed_set(
            graph,
            degree_selection(graph, k),
            simulations=simulations,
            seed=baseline_seed + 1,
        )
    if algorithm_name == "pagerank":
        return evaluate_fixed_seed_set(
            graph,
            pagerank_selection(graph, k),
            simulations=simulations,
            seed=baseline_seed + 2,
        )
    if algorithm_name == "greedy":
        return greedy_influence_maximization(
            graph, k=k, simulations=simulations, seed=experiment_seed + 100 * case_id
        )
    if algorithm_name == "celf":
        return celf_influence_maximization(
            graph, k=k, simulations=simulations, seed=baseline_seed + 3
        )
    if algorithm_name.startswith("distributed_"):
        _, m_part, q_part = algorithm_name.split("_")
        n_partitions = int(m_part.removeprefix("m"))
        multiplier = int(q_part.removeprefix("q").removesuffix("k"))
        local_budget = min(graph.number_of_nodes(), multiplier * k)
        return distributed_greedy_influence_maximization(
            graph,
            k=k,
            n_partitions=n_partitions,
            local_budget=local_budget,
            simulations=max(10, simulations // 3),
            seed=baseline_seed + n_partitions * 10 + multiplier,
        )
    raise ValueError(f"Unknown algorithm: {algorithm_name}")


def run_experiments(
    output_dir: Path,
    seed: int = 7,
    simulations: int = 40,
    scale: str = "small",
    synthetic_sizes: list[int] | None = None,
    show_progress: bool = True,
) -> pd.DataFrame:
    """Run proposal-aligned influence maximization benchmarks."""
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    cases = experiment_cases(scale, synthetic_sizes=synthetic_sizes)

    case_iterator = tqdm(
        enumerate(cases),
        total=len(cases),
        desc="Graph cases",
        disable=not show_progress,
        dynamic_ncols=True,
    )
    for case_id, (graph_kind, size, k) in case_iterator:
        case_iterator.set_postfix_str(f"{graph_kind} n={size} k={k}")
        graph = make_benchmark_graph(graph_kind, size=size, seed=seed + case_id)
        baseline_seed = seed + 1000 * case_id
        results = {}
        algorithm_names = [
            "random",
            "degree",
            "pagerank",
            "greedy",
            "celf",
            *[
                f"distributed_m{n_partitions}_q{multiplier}k"
                for n_partitions in [2, 4, 8]
                for multiplier in [1, 2, 5]
            ],
        ]

        algorithm_iterator = tqdm(
            algorithm_names,
            desc="Algorithms",
            leave=False,
            disable=not show_progress,
            dynamic_ncols=True,
        )
        for algorithm_name in algorithm_iterator:
            algorithm_iterator.set_postfix_str(algorithm_name)
            results[algorithm_name] = _run_algorithm(
                algorithm_name,
                graph,
                k=k,
                simulations=simulations,
                experiment_seed=seed,
                baseline_seed=baseline_seed,
                case_id=case_id,
            )

        evaluation_seed = seed + 50_000 + case_id
        fair_spreads = {
            name: estimate_spread(
                graph, result.seeds, simulations=simulations, seed=evaluation_seed
            )
            for name, result in results.items()
        }
        centralized_fair_spread = fair_spreads["greedy"]

        for algorithm_name, result in results.items():
            records.append(
                {
                    "graph": graph_kind,
                    "size_parameter": size,
                    "n_nodes": graph.number_of_nodes(),
                    "n_edges": graph.number_of_edges(),
                    "k": k,
                    "algorithm": algorithm_name,
                    "seeds": " ".join(map(str, result.seeds)),
                    "selection_estimated_spread": result.estimated_spread,
                    "estimated_spread": fair_spreads[algorithm_name],
                    "quality_ratio_to_greedy": quality_ratio(
                        fair_spreads[algorithm_name], centralized_fair_spread
                    ),
                    "runtime_seconds": result.runtime_seconds,
                    "spread_evaluations": result.spread_evaluations,
                    "transmitted_candidates": result.transmitted_candidates,
                }
            )
        _write_outputs(pd.DataFrame.from_records(records), output_dir, scale)

    data = pd.DataFrame.from_records(records)
    _write_outputs(data, output_dir, scale)
    return data


def _write_outputs(data: pd.DataFrame, output_dir: Path, scale: str) -> None:
    filename_suffix = "" if scale == "small" else f"_{scale}"
    results_csv = output_dir / f"influence_results{filename_suffix}.csv"
    data.to_csv(results_csv, index=False)
    save_metric_plots(results_csv, output_dir / "figures", filename_suffix)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, default=Path("outputs/influence_maximization")
    )
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--simulations", type=int, default=40)
    parser.add_argument(
        "--scale",
        choices=["small", "large"],
        default="small",
        help="Benchmark preset: small is quick, large matches the proposal scale.",
    )
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        help=(
            "Override synthetic graph sizes for the selected scale. "
            "Karate remains the fixed 34-node graph."
        ),
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable tqdm progress bars.",
    )
    args = parser.parse_args()
    data = run_experiments(
        args.output_dir,
        seed=args.seed,
        simulations=args.simulations,
        scale=args.scale,
        synthetic_sizes=args.sizes,
        show_progress=not args.no_progress,
    )
    print(data.to_string(index=False))


if __name__ == "__main__":
    main()
