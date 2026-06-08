"""Graph structure visualizations for benchmark instances."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

from experiments import experiment_cases
from graphs import make_benchmark_graph


def save_small_graph_structure_plots(
    output_dir: Path = Path("outputs/influence_maximization/figures/graphs"),
    seed: int = 7,
) -> None:
    """Save topology plots for the small benchmark graph instances."""
    output_dir.mkdir(parents=True, exist_ok=True)
    graph_entries = []
    for case_id, (graph_kind, size, _) in enumerate(experiment_cases("small")):
        graph = make_benchmark_graph(graph_kind, size=size, seed=seed + case_id)
        label = _case_label(graph_kind, graph.number_of_nodes())
        graph_entries.append((graph_kind, size, label, graph))
        fig = _draw_graph_structure(graph, label, layout_seed=seed + case_id)
        fig.savefig(
            output_dir / f"{graph_kind}_{graph.number_of_nodes()}_structure.png",
            dpi=220,
            bbox_inches="tight",
        )
        plt.close(fig)

    overview = _draw_graph_overview(graph_entries, seed)
    overview.savefig(
        output_dir / "small_graph_structures.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(overview)


def _draw_graph_structure(
    graph: nx.DiGraph, title: str, layout_seed: int
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    fig.patch.set_facecolor("#F8FAFC")
    _draw_graph_on_axis(ax, graph, title, layout_seed, with_colorbar=True)
    return fig


def _draw_graph_overview(
    graph_entries: list[tuple[str, int, str, nx.DiGraph]], seed: int
) -> plt.Figure:
    n_columns = 3
    n_rows = math.ceil(len(graph_entries) / n_columns)
    fig, axes = plt.subplots(n_rows, n_columns, figsize=(14.5, 4.3 * n_rows))
    fig.patch.set_facecolor("#F8FAFC")
    axes = axes.reshape(n_rows, n_columns)
    for idx, (_, _, label, graph) in enumerate(graph_entries):
        ax = axes[idx // 3][idx % 3]
        _draw_graph_on_axis(ax, graph, label, seed + idx, with_colorbar=False)
    for idx in range(len(graph_entries), n_rows * n_columns):
        axes[idx // 3][idx % 3].set_axis_off()
    fig.suptitle(
        "Small benchmark graph structures",
        x=0.04,
        y=1.02,
        ha="left",
        fontsize=16,
        fontweight="bold",
    )
    fig.tight_layout()
    return fig


def _draw_graph_on_axis(
    ax: plt.Axes,
    graph: nx.DiGraph,
    title: str,
    layout_seed: int,
    with_colorbar: bool,
) -> None:
    undirected = graph.to_undirected()
    positions = nx.spring_layout(undirected, seed=layout_seed, iterations=120)
    node_scores = [float(graph.out_degree(node, weight="prob")) for node in graph.nodes()]
    node_sizes = [70 + 35 * undirected.degree(node) for node in graph.nodes()]

    ax.set_facecolor("#FFFFFF")
    nx.draw_networkx_edges(
        undirected,
        positions,
        ax=ax,
        edge_color="#CBD5E1",
        width=0.8,
        alpha=0.55,
    )
    nodes = nx.draw_networkx_nodes(
        undirected,
        positions,
        ax=ax,
        node_color=node_scores,
        node_size=node_sizes,
        cmap="viridis",
        edgecolors="#FFFFFF",
        linewidths=0.7,
    )
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold")
    ax.set_axis_off()
    if with_colorbar:
        colorbar = ax.figure.colorbar(nodes, ax=ax, fraction=0.035, pad=0.02)
        colorbar.set_label("Weighted out-degree", fontsize=9)
        colorbar.ax.tick_params(labelsize=8)


def _case_label(graph_kind: str, n_nodes: int) -> str:
    graph_name = {
        "erdos_renyi": "ER",
        "barabasi_albert": "BA",
        "watts_strogatz": "WS",
        "karate": "Karate",
    }.get(graph_kind, graph_kind.replace("_", " ").title())
    return f"{graph_name} {n_nodes} nodes"


if __name__ == "__main__":
    save_small_graph_structure_plots()
