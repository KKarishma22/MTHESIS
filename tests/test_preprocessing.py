"""Tests for data preprocessing utilities."""

import numpy as np
import pandas as pd
import pytest

from data.preprocessing import (
    drop_missing,
    fill_missing,
    encode_labels,
    scale_features,
    split_data,
)


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "a": [1.0, 2.0, np.nan, 4.0],
            "b": [10.0, np.nan, np.nan, 40.0],
            "c": [100.0, 200.0, 300.0, 400.0],
        }
    )


def test_drop_missing_removes_high_missing_column(sample_df):
    result = drop_missing(sample_df, threshold=0.4)
    assert "b" not in result.columns
    assert "a" in result.columns
    assert "c" in result.columns


def test_drop_missing_keeps_all_below_threshold(sample_df):
    result = drop_missing(sample_df, threshold=1.0)
    assert list(result.columns) == ["a", "b", "c"]


def test_fill_missing_mean(sample_df):
    result = fill_missing(sample_df, strategy="mean")
    assert result.isnull().sum().sum() == 0
    assert result["a"].iloc[2] == pytest.approx((1.0 + 2.0 + 4.0) / 3)


def test_fill_missing_median(sample_df):
    result = fill_missing(sample_df, strategy="median")
    assert result.isnull().sum().sum() == 0


def test_fill_missing_mode(sample_df):
    result = fill_missing(sample_df, strategy="mode")
    assert result.isnull().sum().sum() == 0


def test_fill_missing_invalid_strategy(sample_df):
    with pytest.raises(ValueError, match="Unknown strategy"):
        fill_missing(sample_df, strategy="unknown")


def test_encode_labels():
    series = pd.Series(["cat", "dog", "cat", "bird"])
    encoded, encoder = encode_labels(series)
    assert len(encoded) == 4
    assert set(encoded) == {0, 1, 2}
    assert list(encoder.classes_) == ["bird", "cat", "dog"]


def test_scale_features():
    X_train = np.array([[1, 2], [3, 4], [5, 6]], dtype=float)
    X_test = np.array([[2, 3]], dtype=float)
    X_train_s, X_test_s, scaler = scale_features(X_train, X_test)
    assert X_train_s.shape == X_train.shape
    assert X_test_s.shape == X_test.shape
    assert abs(X_train_s.mean()) < 1e-10


def test_split_data():
    X = np.arange(100).reshape(50, 2)
    y = np.arange(50)
    X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2)
    assert len(X_train) == 40
    assert len(X_test) == 10
    assert len(y_train) == 40
    assert len(y_test) == 10
