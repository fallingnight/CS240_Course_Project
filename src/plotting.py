"""Plotting helpers for influence maximization experiment outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


CORE_ALGORITHMS = ["random", "degree", "pagerank", "greedy", "celf"]

ALGORITHM_LABELS = {
    "random": "Random",
    "degree": "Weighted degree",
    "pagerank": "PageRank",
    "greedy": "Greedy",
    "celf": "CELF",
}

CORE_COLORS = {
    "random": "#9CA3AF",
    "degree": "#4B5563",
    "pagerank": "#0F766E",
    "greedy": "#D97706",
    "celf": "#2563EB",
}

DISTRIBUTED_COLORS = {
    2: "#7C3AED",
    4: "#DB2777",
    8: "#0891B2",
}

DISTRIBUTED_MARKERS = {
    1: "o",
    2: "s",
    5: "^",
}

METRICS = [
    ("estimated_spread", "Estimated IC spread"),
    ("quality_ratio_to_greedy", "Quality ratio to greedy"),
    ("runtime_seconds", "Runtime (seconds)"),
    ("spread_evaluations", "Spread evaluations"),
    ("transmitted_candidates", "Transmitted candidates"),
]


def save_metric_plots(
    results_csv: Path, output_dir: Path, filename_suffix: str = ""
) -> None:
    """Save one plot per major project metric."""
    output_dir.mkdir(parents=True, exist_ok=True)
    data = _with_case_labels(pd.read_csv(results_csv))
    plt.style.use("default")

    for metric, ylabel in METRICS:
        if metric == "transmitted_candidates":
            fig = _plot_distributed_only(data, metric, ylabel)
        else:
            fig = _plot_core_and_distributed(data, metric, ylabel)
        fig.savefig(
            output_dir / f"{metric}{filename_suffix}.png",
            dpi=220,
            bbox_inches="tight",
        )
        plt.close(fig)
    _save_comparison_plots(data, output_dir, filename_suffix)


def _save_comparison_plots(
    data: pd.DataFrame, output_dir: Path, filename_suffix: str
) -> None:
    comparison_dir = output_dir / "comparisons"
    comparison_dir.mkdir(parents=True, exist_ok=True)

    for metric, ylabel in METRICS:
        metric_suffix = "" if metric == "estimated_spread" else f"_{metric}"
        fig = _plot_vertical_bar_comparison(data, metric, ylabel)
        fig.savefig(
            comparison_dir / f"vertical_comparison{metric_suffix}{filename_suffix}.png",
            dpi=220,
            bbox_inches="tight",
        )
        plt.close(fig)

        horizontal_data = data[data["graph"] != "karate"]
        if horizontal_data.empty:
            continue
        fig = _plot_horizontal_bar_comparison(horizontal_data, metric, ylabel)
        fig.savefig(
            comparison_dir / f"horizontal_comparison{metric_suffix}{filename_suffix}.png",
            dpi=220,
            bbox_inches="tight",
        )
        plt.close(fig)


def _with_case_labels(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    cases = data[["graph", "size_parameter", "n_nodes"]].drop_duplicates()
    cases = cases.reset_index(drop=True)
    cases["case_index"] = cases.index
    cases["case_label"] = cases.apply(_case_label, axis=1)
    return data.merge(cases, on=["graph", "size_parameter", "n_nodes"], how="left")


def _method_node_matrix(data: pd.DataFrame, metric: str) -> pd.DataFrame:
    algorithms = _ordered_algorithms(data)
    cases = _ordered_case_labels(data)
    matrix = data.pivot_table(
        index="algorithm",
        columns="case_label",
        values=metric,
        aggfunc="mean",
    )
    return matrix.reindex(index=algorithms, columns=cases)


def _node_method_matrix(data: pd.DataFrame, metric: str) -> pd.DataFrame:
    algorithms = _ordered_algorithms(data)
    cases = _ordered_case_labels(data)
    matrix = data.pivot_table(
        index="case_label",
        columns="algorithm",
        values=metric,
        aggfunc="mean",
    )
    return matrix.reindex(index=cases, columns=algorithms)


def _ordered_algorithms(data: pd.DataFrame) -> list[str]:
    algorithms = list(data["algorithm"].drop_duplicates())
    core = [algorithm for algorithm in CORE_ALGORITHMS if algorithm in algorithms]
    distributed = sorted(
        [algorithm for algorithm in algorithms if algorithm.startswith("distributed")],
        key=_distributed_sort_key,
    )
    other = [
        algorithm
        for algorithm in algorithms
        if algorithm not in core and algorithm not in distributed
    ]
    return [*core, *distributed, *other]


def _distributed_sort_key(algorithm: str) -> tuple[int, int]:
    parts = algorithm.split("_")
    if len(parts) != 3:
        return (999, 999)
    return (
        int(parts[1].removeprefix("m")),
        int(parts[2].removeprefix("q").removesuffix("k")),
    )


def _ordered_case_labels(data: pd.DataFrame) -> list[str]:
    return (
        data[["case_index", "case_label"]]
        .drop_duplicates()
        .sort_values("case_index")["case_label"]
        .tolist()
    )


def _plot_vertical_bar_comparison(
    data: pd.DataFrame, metric: str, ylabel: str
) -> plt.Figure:
    summary = _node_algorithm_summary(data, metric)
    algorithms = _ordered_algorithms(data)
    node_sizes = sorted(summary["n_nodes"].unique())
    x_positions = range(len(algorithms))
    bar_width = min(0.16, 0.78 / max(1, len(node_sizes)))
    colors = plt.cm.Set2(range(len(node_sizes)))

    fig, ax = plt.subplots(figsize=(13.5, 5.8))
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#FFFFFF")

    for offset_index, node_size in enumerate(node_sizes):
        frame = summary[summary["n_nodes"] == node_size].set_index("algorithm")
        values = [frame[metric].get(algorithm, 0.0) for algorithm in algorithms]
        offset = (offset_index - (len(node_sizes) - 1) / 2) * bar_width
        ax.bar(
            [x + offset for x in x_positions],
            values,
            width=bar_width,
            label=f"{node_size} nodes",
            color=colors[offset_index],
            edgecolor="white",
            linewidth=0.5,
        )

    ax.set_title(
        "Vertical comparison: node sizes within each method",
        loc="left",
        fontsize=15,
        fontweight="bold",
        pad=12,
    )
    ax.set_ylabel(ylabel, fontsize=11, color="#111827")
    ax.set_xlabel("Algorithm", fontsize=10, color="#374151", labelpad=14)
    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(
        [_display_algorithm_label(algorithm) for algorithm in algorithms],
        rotation=35,
        ha="right",
        fontsize=8,
    )
    _polish_bar_axis(ax)
    ax.legend(
        title="Node count",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.27),
        ncol=min(5, len(node_sizes)),
        frameon=False,
        fontsize=8,
        title_fontsize=9,
    )
    return fig


def _plot_horizontal_bar_comparison(
    data: pd.DataFrame, metric: str, xlabel: str
) -> plt.Figure:
    summary = _node_algorithm_summary(data, metric)
    algorithms = _ordered_algorithms(data)
    core_algorithms = [algorithm for algorithm in algorithms if algorithm in CORE_ALGORITHMS]
    distributed_algorithms = [
        algorithm for algorithm in algorithms if algorithm.startswith("distributed")
    ]
    node_sizes = sorted(summary["n_nodes"].unique())
    fig, axes = plt.subplots(
        len(node_sizes),
        2,
        figsize=(13.5, max(5.0, 4.4 * len(node_sizes))),
        sharey=True,
        squeeze=False,
    )
    fig.subplots_adjust(hspace=0.9, wspace=0.2, top=0.92, bottom=0.08)
    fig.patch.set_facecolor("#F8FAFC")

    max_value = float(summary[metric].max()) if not summary.empty else 0.0
    y_limit = max_value * 1.12 if max_value > 0 else 1.0

    for row_index, node_size in enumerate(node_sizes):
        frame = summary[summary["n_nodes"] == node_size].set_index("algorithm")
        _plot_method_bar_panel(
            axes[row_index][0],
            frame,
            core_algorithms,
            f"{node_size} nodes - core",
            metric,
            y_limit,
        )
        _plot_method_bar_panel(
            axes[row_index][1],
            frame,
            distributed_algorithms,
            f"{node_size} nodes - distributed",
            metric,
            y_limit,
        )
        axes[row_index][0].set_ylabel(xlabel, fontsize=9, color="#374151")

    fig.suptitle(
        "Horizontal comparison: methods within the same node count",
        x=0.04,
        y=1.03,
        ha="left",
        fontsize=15,
        fontweight="bold",
    )
    fig.supxlabel("Algorithm", y=-0.02, fontsize=10, color="#374151")
    return fig


def _plot_method_bar_panel(
    ax: plt.Axes,
    frame: pd.DataFrame,
    algorithms: list[str],
    title: str,
    metric: str,
    y_limit: float,
) -> None:
    values = [frame[metric].get(algorithm, 0.0) for algorithm in algorithms]
    colors = [_algorithm_color(algorithm) for algorithm in algorithms]
    x_positions = range(len(algorithms))
    ax.bar(
        list(x_positions),
        values,
        color=colors,
        edgecolor="white",
        linewidth=0.5,
    )
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_ylim(0, y_limit)
    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(
        [_display_algorithm_label(algorithm) for algorithm in algorithms],
        rotation=32,
        ha="right",
        fontsize=6 if len(algorithms) > 6 else 7,
    )
    _polish_bar_axis(ax)


def _algorithm_color(algorithm: str) -> str:
    if algorithm in CORE_COLORS:
        return CORE_COLORS[algorithm]
    if algorithm.startswith("distributed"):
        return DISTRIBUTED_COLORS.get(_distributed_sort_key(algorithm)[0], "#64748B")
    return "#64748B"


def _node_algorithm_summary(data: pd.DataFrame, metric: str) -> pd.DataFrame:
    return (
        data.groupby(["n_nodes", "algorithm"], as_index=False)[metric]
        .mean()
        .sort_values(["n_nodes", "algorithm"])
    )


def _polish_bar_axis(ax: plt.Axes) -> None:
    ax.grid(axis="y", color="#CBD5E1", linewidth=0.8, alpha=0.55)
    ax.grid(axis="x", color="#CBD5E1", linewidth=0.8, alpha=0.35)
    ax.set_axisbelow(True)
    ax.tick_params(colors="#374151")
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color("#CBD5E1")
    ax.spines["bottom"].set_color("#CBD5E1")


def _plot_heatmap(
    matrix: pd.DataFrame,
    title: str,
    xlabel: str,
    ylabel: str,
) -> plt.Figure:
    width = max(8.5, 0.52 * len(matrix.columns) + 3.8)
    height = max(5.2, 0.34 * len(matrix.index) + 2.5)
    fig, ax = plt.subplots(figsize=(width, height))
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#FFFFFF")

    image = ax.imshow(
        matrix.to_numpy(dtype=float),
        aspect="auto",
        cmap="viridis",
        extent=(-0.5, len(matrix.columns) - 0.5, len(matrix.index) - 0.5, -0.5),
    )
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel(xlabel, fontsize=10, color="#374151", labelpad=12)
    ax.set_ylabel(ylabel, fontsize=10, color="#374151", labelpad=12)
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, fontsize=7, rotation=35, ha="right")
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels([_display_algorithm_label(v) for v in matrix.index], fontsize=8)
    ax.tick_params(colors="#374151")
    for spine in ax.spines.values():
        spine.set_visible(False)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.025, pad=0.02)
    colorbar.ax.tick_params(labelsize=8, colors="#374151")
    return fig


def _display_algorithm_label(algorithm: str) -> str:
    if algorithm in ALGORITHM_LABELS:
        return ALGORITHM_LABELS[algorithm]
    if algorithm.startswith("distributed"):
        _, m_part, q_part = algorithm.split("_")
        return f"m={m_part.removeprefix('m')}, q={q_part.removeprefix('q')}"
    return algorithm


def _case_label(row: pd.Series) -> str:
    graph_name = {
        "erdos_renyi": "ER",
        "barabasi_albert": "BA",
        "watts_strogatz": "WS",
        "karate": "Karate",
    }.get(str(row["graph"]), str(row["graph"]).replace("_", " ").title())
    return f"{graph_name}\n{int(row['n_nodes'])} nodes"


def _plot_core_and_distributed(
    data: pd.DataFrame, metric: str, ylabel: str
) -> plt.Figure:
    crowded = data[["graph", "size_parameter", "n_nodes"]].drop_duplicates().shape[0] > 6
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(12.5, 5.2),
        sharey=False,
        gridspec_kw={"width_ratios": [1.0, 1.35], "wspace": 0.08},
    )
    fig.patch.set_facecolor("#F8FAFC")
    _plot_core_panel(axes[0], data, metric)
    _plot_distributed_panel(axes[1], data, metric)

    axes[0].set_ylabel(ylabel, fontsize=11, color="#111827")
    axes[0].set_title("Core methods", loc="left", fontweight="bold", fontsize=12)
    axes[1].set_title(
        "Distributed candidate sharing", loc="left", fontweight="bold", fontsize=12
    )
    fig.suptitle(ylabel, x=0.055, y=1.02, ha="left", fontsize=15, fontweight="bold")
    fig.supxlabel(
        "Benchmark instance",
        y=-0.06 if crowded else 0.02,
        fontsize=10,
        color="#374151",
    )
    _add_quality_reference_line(axes, metric)
    _polish_axes(axes, data)
    _add_split_legend(fig, axes)
    return fig


def _plot_distributed_only(
    data: pd.DataFrame, metric: str, ylabel: str
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10.8, 5.2))
    fig.patch.set_facecolor("#F8FAFC")
    _plot_distributed_panel(ax, data, metric)
    ax.set_title(ylabel, loc="left", fontsize=15, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=11, color="#111827")
    ax.set_xlabel("Benchmark instance", fontsize=10, color="#374151", labelpad=18)
    _polish_axes([ax], data)
    ax.legend(
        title="Distributed setting",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.23),
        ncol=3,
        frameon=False,
        fontsize=8,
        title_fontsize=9,
    )
    return fig


def _plot_core_panel(ax: plt.Axes, data: pd.DataFrame, metric: str) -> None:
    core = data[data["algorithm"].isin(CORE_ALGORITHMS)]
    for algorithm in CORE_ALGORITHMS:
        frame = core[core["algorithm"] == algorithm].sort_values("case_index")
        ax.plot(
            frame["case_index"],
            frame[metric],
            label=ALGORITHM_LABELS[algorithm],
            color=CORE_COLORS[algorithm],
            marker="o",
            markersize=5,
            linewidth=2.2 if algorithm in {"greedy", "celf"} else 1.8,
            alpha=0.95 if algorithm in {"greedy", "celf"} else 0.78,
        )


def _plot_distributed_panel(ax: plt.Axes, data: pd.DataFrame, metric: str) -> None:
    distributed = _distributed_settings(data)
    for _, frame in distributed.groupby(["m", "q_multiplier"], sort=True):
        frame = frame.sort_values("case_index")
        first = frame.iloc[0]
        m = int(first["m"])
        q_multiplier = int(first["q_multiplier"])
        ax.plot(
            frame["case_index"],
            frame[metric],
            label=f"m={m}, q={q_multiplier}k",
            color=DISTRIBUTED_COLORS[m],
            marker=DISTRIBUTED_MARKERS[q_multiplier],
            markersize=4.8,
            linewidth=1.8,
            alpha={1: 0.72, 2: 0.86, 5: 1.0}[q_multiplier],
        )


def _distributed_settings(data: pd.DataFrame) -> pd.DataFrame:
    distributed = data[data["algorithm"].str.startswith("distributed")].copy()
    parsed = distributed["algorithm"].str.extract(r"m(?P<m>\d+)_q(?P<q_multiplier>\d+)k")
    distributed["m"] = parsed["m"].astype(int)
    distributed["q_multiplier"] = parsed["q_multiplier"].astype(int)
    return distributed


def _add_quality_reference_line(axes: list[plt.Axes], metric: str) -> None:
    if metric != "quality_ratio_to_greedy":
        return
    for ax in axes:
        ax.axhline(
            1.0,
            color="#111827",
            linestyle=(0, (4, 4)),
            linewidth=1.1,
            alpha=0.55,
            zorder=0,
        )


def _polish_axes(axes: list[plt.Axes], data: pd.DataFrame) -> None:
    cases = data[["case_index", "case_label"]].drop_duplicates().sort_values("case_index")
    x_values = cases["case_index"].tolist()
    x_labels = cases["case_label"].tolist()
    crowded = len(x_values) > 6
    for ax in axes:
        ax.set_facecolor("#FFFFFF")
        ax.set_xticks(x_values)
        ax.set_xticklabels(
            x_labels,
            fontsize=7 if crowded else 8,
            rotation=28 if crowded else 0,
            ha="right" if crowded else "center",
            rotation_mode="anchor",
        )
        ax.tick_params(axis="y", labelsize=9, colors="#374151")
        ax.tick_params(axis="x", colors="#374151")
        ax.grid(axis="y", color="#CBD5E1", linewidth=0.8, alpha=0.55)
        ax.grid(axis="x", visible=False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#CBD5E1")
        ax.spines["bottom"].set_color("#CBD5E1")
        ax.margins(x=0.04, y=0.12)


def _add_split_legend(fig: plt.Figure, axes: list[plt.Axes]) -> None:
    core_handles, core_labels = axes[0].get_legend_handles_labels()
    dist_handles, dist_labels = axes[1].get_legend_handles_labels()
    fig.legend(
        core_handles,
        core_labels,
        loc="lower left",
        bbox_to_anchor=(0.06, -0.11),
        ncol=len(core_labels),
        frameon=False,
        fontsize=8,
    )
    fig.legend(
        dist_handles,
        dist_labels,
        loc="lower right",
        bbox_to_anchor=(0.97, -0.13),
        ncol=3,
        frameon=False,
        fontsize=8,
    )
