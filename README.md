# MTHESIS

Master's Thesis codebase — data preprocessing, classification, evaluation and
visualisation utilities.

## Project structure

```
MTHESIS/
├── src/
│   ├── data/           # Data loading and preprocessing
│   ├── models/         # Classifier wrappers
│   ├── evaluation/     # Metrics and reporting
│   └── visualization/  # Plotting helpers
├── tests/              # Unit tests (pytest)
├── notebooks/          # Jupyter notebooks for exploration
├── data/
│   ├── raw/            # Original, immutable data
│   └── processed/      # Cleaned / transformed data
├── requirements.txt
└── setup.py
```

## Setup

```bash
pip install -r requirements.txt
pip install -e .
```

## Running tests

```bash
pytest
```

## Usage

```python
from data.preprocessing import load_dataset, fill_missing, scale_features, split_data
from models.classifier import Classifier
from evaluation.metrics import compute_metrics

df = load_dataset("data/raw/dataset.csv")
df = fill_missing(df)

X = df.drop(columns=["label"]).values
y = df["label"].values

X_train, X_test, y_train, y_test = split_data(X, y)
X_train, X_test, _ = scale_features(X_train, X_test)

clf = Classifier("random_forest", n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

metrics = compute_metrics(y_test, clf.predict(X_test))
print(metrics)
```