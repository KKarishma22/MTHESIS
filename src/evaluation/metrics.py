"""Evaluation metrics for classification experiments."""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    average: str = "weighted",
) -> dict[str, float]:
    """Compute standard classification metrics.

    Args:
        y_true: Ground-truth labels.
        y_pred: Predicted labels.
        average: Averaging strategy for multi-class metrics (passed to
            scikit-learn).

    Returns:
        Dictionary with keys ``accuracy``, ``precision``, ``recall``,
        and ``f1``.
    """
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average=average, zero_division=0),
        "recall": recall_score(y_true, y_pred, average=average, zero_division=0),
        "f1": f1_score(y_true, y_pred, average=average, zero_division=0),
    }


def get_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Return the confusion matrix.

    Args:
        y_true: Ground-truth labels.
        y_pred: Predicted labels.

    Returns:
        Confusion matrix as a 2-D NumPy array.
    """
    return confusion_matrix(y_true, y_pred)


def get_classification_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    target_names: list[str] | None = None,
) -> str:
    """Return a full classification report as a string.

    Args:
        y_true: Ground-truth labels.
        y_pred: Predicted labels.
        target_names: Optional list of class names for display.

    Returns:
        Formatted classification report string.
    """
    return classification_report(
        y_true, y_pred, target_names=target_names, zero_division=0
    )
