"""Machine learning classifier wrapper."""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC


_SUPPORTED_MODELS = {
    "random_forest": RandomForestClassifier,
    "logistic_regression": LogisticRegression,
    "svm": SVC,
}


class Classifier:
    """A lightweight wrapper around common scikit-learn classifiers.

    Args:
        model_name: One of ``"random_forest"``, ``"logistic_regression"``,
            or ``"svm"``.
        **kwargs: Keyword arguments forwarded to the underlying estimator.
    """

    def __init__(self, model_name: str = "random_forest", **kwargs) -> None:
        if model_name not in _SUPPORTED_MODELS:
            raise ValueError(
                f"Unknown model {model_name!r}. "
                f"Choose from: {list(_SUPPORTED_MODELS)}"
            )
        self.model_name = model_name
        self.model = _SUPPORTED_MODELS[model_name](**kwargs)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "Classifier":
        """Train the classifier.

        Args:
            X: Training feature matrix.
            y: Training labels.

        Returns:
            Self (for method chaining).
        """
        self.model.fit(X, y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels for *X*.

        Args:
            X: Feature matrix.

        Returns:
            Predicted labels.
        """
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities for *X* (if supported by the model).

        Args:
            X: Feature matrix.

        Returns:
            Array of class probabilities.

        Raises:
            AttributeError: If the underlying model does not support probability
                estimates.
        """
        if not hasattr(self.model, "predict_proba"):
            raise AttributeError(
                f"{self.model_name!r} does not support probability predictions. "
                "Use predict() instead."
            )
        return self.model.predict_proba(X)
