"""Tests for evaluation metrics."""

import numpy as np
import pytest

from evaluation.metrics import (
    compute_metrics,
    get_confusion_matrix,
    get_classification_report,
)


@pytest.fixture
def perfect_predictions():
    y_true = np.array([0, 1, 2, 0, 1, 2])
    y_pred = np.array([0, 1, 2, 0, 1, 2])
    return y_true, y_pred


@pytest.fixture
def imperfect_predictions():
    y_true = np.array([0, 1, 2, 0, 1, 2])
    y_pred = np.array([0, 2, 1, 0, 1, 2])
    return y_true, y_pred


def test_compute_metrics_perfect(perfect_predictions):
    y_true, y_pred = perfect_predictions
    metrics = compute_metrics(y_true, y_pred)
    assert metrics["accuracy"] == pytest.approx(1.0)
    assert metrics["f1"] == pytest.approx(1.0)
    assert metrics["precision"] == pytest.approx(1.0)
    assert metrics["recall"] == pytest.approx(1.0)


def test_compute_metrics_imperfect(imperfect_predictions):
    y_true, y_pred = imperfect_predictions
    metrics = compute_metrics(y_true, y_pred)
    assert 0.0 < metrics["accuracy"] < 1.0
    assert 0.0 < metrics["f1"] < 1.0


def test_compute_metrics_keys(perfect_predictions):
    y_true, y_pred = perfect_predictions
    metrics = compute_metrics(y_true, y_pred)
    assert set(metrics.keys()) == {"accuracy", "precision", "recall", "f1"}


def test_get_confusion_matrix_shape(perfect_predictions):
    y_true, y_pred = perfect_predictions
    cm = get_confusion_matrix(y_true, y_pred)
    assert cm.shape == (3, 3)


def test_get_confusion_matrix_perfect(perfect_predictions):
    y_true, y_pred = perfect_predictions
    cm = get_confusion_matrix(y_true, y_pred)
    assert np.trace(cm) == len(y_true)


def test_get_classification_report_returns_string(perfect_predictions):
    y_true, y_pred = perfect_predictions
    report = get_classification_report(y_true, y_pred, target_names=["A", "B", "C"])
    assert isinstance(report, str)
    assert "A" in report
