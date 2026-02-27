"""Visualization utilities for exploratory data analysis and results."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def _save_or_show(fig: plt.Figure, save_path: str | None) -> None:
    """Save *fig* to *save_path*, or show it interactively if *save_path* is None."""
    if save_path:
        fig.savefig(save_path)
    else:
        plt.show()
    plt.close(fig)


def plot_confusion_matrix(
    cm: np.ndarray,
    class_names: list[str] | None = None,
    title: str = "Confusion Matrix",
    figsize: tuple[int, int] = (8, 6),
    save_path: str | None = None,
) -> None:
    """Plot a confusion matrix as a heat-map.

    Args:
        cm: Confusion matrix (square 2-D array).
        class_names: Optional list of class labels.
        title: Plot title.
        figsize: Figure size in inches.
        save_path: If given, save the figure to this path instead of showing it.
    """
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names or "auto",
        yticklabels=class_names or "auto",
        ax=ax,
    )
    ax.set_title(title)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    plt.tight_layout()
    _save_or_show(fig, save_path)


def plot_feature_importance(
    importances: np.ndarray,
    feature_names: list[str],
    top_n: int = 20,
    title: str = "Feature Importances",
    figsize: tuple[int, int] = (10, 6),
    save_path: str | None = None,
) -> None:
    """Plot feature importances as a horizontal bar chart.

    Args:
        importances: Array of importance scores (one per feature).
        feature_names: List of feature names corresponding to *importances*.
        top_n: Maximum number of features to display.
        title: Plot title.
        figsize: Figure size in inches.
        save_path: If given, save the figure to this path instead of showing it.
    """
    indices = np.argsort(importances)[::-1][:top_n]
    selected_names = [feature_names[i] for i in indices]
    selected_importances = importances[indices]

    fig, ax = plt.subplots(figsize=figsize)
    ax.barh(range(top_n), selected_importances[::-1], align="center")
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(selected_names[::-1])
    ax.set_title(title)
    ax.set_xlabel("Importance")
    plt.tight_layout()
    _save_or_show(fig, save_path)


def plot_metric_comparison(
    metrics: dict[str, dict[str, float]],
    title: str = "Model Comparison",
    figsize: tuple[int, int] = (10, 6),
    save_path: str | None = None,
) -> None:
    """Plot a grouped bar chart comparing metrics across multiple models.

    Args:
        metrics: Mapping of model name to its metrics dict
            (e.g. ``{"RF": {"accuracy": 0.9, "f1": 0.88}, ...}``).
        title: Plot title.
        figsize: Figure size in inches.
        save_path: If given, save the figure to this path instead of showing it.
    """
    model_names = list(metrics.keys())
    metric_names = list(next(iter(metrics.values())).keys())
    x = np.arange(len(metric_names))
    width = 0.8 / len(model_names)

    fig, ax = plt.subplots(figsize=figsize)
    for i, model in enumerate(model_names):
        values = [metrics[model][m] for m in metric_names]
        ax.bar(x + i * width, values, width, label=model)

    ax.set_title(title)
    ax.set_xticks(x + width * (len(model_names) - 1) / 2)
    ax.set_xticklabels(metric_names)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Score")
    ax.legend()
    plt.tight_layout()
    _save_or_show(fig, save_path)
