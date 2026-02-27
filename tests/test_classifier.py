"""Tests for the Classifier wrapper."""

import numpy as np
import pytest
from sklearn.datasets import make_classification

from models.classifier import Classifier


@pytest.fixture
def binary_data():
    X, y = make_classification(n_samples=100, n_features=10, random_state=42)
    return X, y


def test_random_forest_fit_predict(binary_data):
    X, y = binary_data
    clf = Classifier("random_forest", n_estimators=10, random_state=42)
    clf.fit(X, y)
    preds = clf.predict(X)
    assert preds.shape == y.shape
    assert set(preds).issubset({0, 1})


def test_logistic_regression_fit_predict(binary_data):
    X, y = binary_data
    clf = Classifier("logistic_regression", max_iter=1000, random_state=42)
    clf.fit(X, y)
    preds = clf.predict(X)
    assert preds.shape == y.shape


def test_svm_fit_predict(binary_data):
    X, y = binary_data
    clf = Classifier("svm", kernel="rbf")
    clf.fit(X, y)
    preds = clf.predict(X)
    assert preds.shape == y.shape


def test_predict_proba_random_forest(binary_data):
    X, y = binary_data
    clf = Classifier("random_forest", n_estimators=10, random_state=42)
    clf.fit(X, y)
    proba = clf.predict_proba(X)
    assert proba.shape == (len(X), 2)
    assert np.allclose(proba.sum(axis=1), 1.0)


def test_unknown_model_raises():
    with pytest.raises(ValueError, match="Unknown model"):
        Classifier("neural_net")


def test_method_chaining(binary_data):
    X, y = binary_data
    clf = Classifier("random_forest", n_estimators=5, random_state=0)
    returned = clf.fit(X, y)
    assert returned is clf
