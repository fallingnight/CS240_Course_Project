"""Checks for experiment presets."""

import pytest

from experiments import _write_outputs, experiment_cases


def _minimal_results_frame():
    import pandas as pd

    return pd.DataFrame.from_records(
        [
            {
                "graph": "karate",
                "size_parameter": 34,
                "n_nodes": 34,
                "n_edges": 156,
                "k": 5,
                "algorithm": "greedy",
                "seeds": "0 1 2 3 4",
                "selection_estimated_spread": 10.0,
                "estimated_spread": 10.0,
                "quality_ratio_to_greedy": 1.0,
                "runtime_seconds": 0.1,
                "spread_evaluations": 1,
                "transmitted_candidates": 0,
            },
            {
                "graph": "karate",
                "size_parameter": 34,
                "n_nodes": 34,
                "n_edges": 156,
                "k": 5,
                "algorithm": "distributed_m2_q1k",
                "seeds": "0 1 2 3 4",
                "selection_estimated_spread": 9.0,
                "estimated_spread": 9.0,
                "quality_ratio_to_greedy": 0.9,
                "runtime_seconds": 0.2,
                "spread_evaluations": 2,
                "transmitted_candidates": 10,
            },
        ]
    )


def test_small_scale_preserves_quick_benchmarks() -> None:
    assert experiment_cases("small") == [
        ("erdos_renyi", 40, 5),
        ("erdos_renyi", 70, 6),
        ("barabasi_albert", 40, 5),
        ("barabasi_albert", 70, 6),
        ("watts_strogatz", 40, 5),
        ("watts_strogatz", 70, 6),
        ("karate", 34, 5),
    ]


def test_large_scale_matches_proposal_sizes() -> None:
    assert experiment_cases("large") == [
        ("erdos_renyi", 50, 10),
        ("erdos_renyi", 100, 10),
        ("erdos_renyi", 200, 10),
        ("barabasi_albert", 50, 10),
        ("barabasi_albert", 100, 10),
        ("barabasi_albert", 200, 10),
        ("watts_strogatz", 50, 10),
        ("watts_strogatz", 100, 10),
        ("watts_strogatz", 200, 10),
        ("karate", 34, 5),
    ]


def test_scale_sizes_can_be_overridden() -> None:
    assert experiment_cases("large", synthetic_sizes=[12, 24]) == [
        ("erdos_renyi", 12, 10),
        ("erdos_renyi", 24, 10),
        ("barabasi_albert", 12, 10),
        ("barabasi_albert", 24, 10),
        ("watts_strogatz", 12, 10),
        ("watts_strogatz", 24, 10),
        ("karate", 34, 5),
    ]


def test_unknown_scale_is_rejected() -> None:
    with pytest.raises(ValueError):
        experiment_cases("medium")


def test_non_positive_sizes_are_rejected() -> None:
    with pytest.raises(ValueError):
        experiment_cases("large", synthetic_sizes=[50, 0])


def test_large_outputs_use_distinct_filenames(tmp_path) -> None:
    data = _minimal_results_frame()
    _write_outputs(data, tmp_path, "small")
    _write_outputs(data, tmp_path, "large")

    assert (tmp_path / "influence_results.csv").exists()
    assert (tmp_path / "influence_results_large.csv").exists()
    assert (tmp_path / "figures" / "estimated_spread.png").exists()
    assert (tmp_path / "figures" / "estimated_spread_large.png").exists()
    assert (tmp_path / "figures" / "comparisons" / "vertical_comparison.png").exists()
    assert (
        tmp_path / "figures" / "comparisons" / "vertical_comparison_large.png"
    ).exists()
