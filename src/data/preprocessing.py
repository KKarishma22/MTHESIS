"""Data preprocessing utilities."""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split


def load_dataset(filepath: str) -> pd.DataFrame:
    """Load a dataset from a CSV file.

    Args:
        filepath: Path to the CSV file.

    Returns:
        Loaded DataFrame.
    """
    return pd.read_csv(filepath)


def drop_missing(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """Drop columns whose missing-value ratio exceeds *threshold*.

    Args:
        df: Input DataFrame.
        threshold: Maximum fraction of missing values allowed (0–1).

    Returns:
        DataFrame with high-missing columns removed.
    """
    missing_ratio = df.isnull().mean()
    return df.loc[:, missing_ratio < threshold]


def fill_missing(df: pd.DataFrame, strategy: str = "mean") -> pd.DataFrame:
    """Fill missing values in numeric columns.

    Args:
        df: Input DataFrame.
        strategy: One of ``"mean"``, ``"median"``, or ``"mode"``.

    Returns:
        DataFrame with missing values filled.
    """
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if strategy == "mean":
            df[col] = df[col].fillna(df[col].mean())
        elif strategy == "median":
            df[col] = df[col].fillna(df[col].median())
        elif strategy == "mode":
            df[col] = df[col].fillna(df[col].mode()[0])
        else:
            raise ValueError(f"Unknown strategy: {strategy!r}")
    return df


def encode_labels(series: pd.Series) -> tuple[np.ndarray, LabelEncoder]:
    """Encode a categorical series as integers.

    Args:
        series: Categorical pandas Series.

    Returns:
        Tuple of (encoded array, fitted LabelEncoder).
    """
    encoder = LabelEncoder()
    encoded = encoder.fit_transform(series)
    return encoded, encoder


def scale_features(
    X_train: np.ndarray, X_test: np.ndarray
) -> tuple[np.ndarray, np.ndarray, StandardScaler]:
    """Standardise features using statistics from the training set.

    Args:
        X_train: Training feature matrix.
        X_test: Test feature matrix.

    Returns:
        Tuple of (scaled X_train, scaled X_test, fitted StandardScaler).
    """
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled, scaler


def split_data(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Split data into training and test sets.

    Args:
        X: Feature matrix.
        y: Target vector.
        test_size: Fraction of data to use for testing.
        random_state: Random seed for reproducibility.

    Returns:
        Tuple of (X_train, X_test, y_train, y_test).
    """
    return train_test_split(X, y, test_size=test_size, random_state=random_state)
