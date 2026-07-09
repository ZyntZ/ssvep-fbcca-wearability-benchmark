import numpy as np
import pytest
from ssvep_fbcca import CCAClassifier, FBCCAClassifier


def make_tiny_data():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(8, 3, 250))
    y = np.array([0, 1, 0, 1, 0, 1, 0, 1])
    return X, y


def test_cca_predict_shape():
    X, y = make_tiny_data()
    clf = CCAClassifier(sfreq=250, freqs=[8, 10], n_harmonics=2).fit(X, y)
    pred = clf.predict(X[:2])
    assert pred.shape == (2,)


def test_fbcca_predict_shape():
    X, y = make_tiny_data()
    clf = FBCCAClassifier(
        sfreq=250,
        freqs=[8, 10],
        n_harmonics=2,
        filterbank=[(6, 14), (14, 30)],
    ).fit(X, y)
    pred = clf.predict(X[:2])
    assert pred.shape == (2,)


def test_nan_input_raises():
    X, y = make_tiny_data()
    X[0, 0, 0] = np.nan
    clf = CCAClassifier(sfreq=250, freqs=[8, 10])
    with pytest.raises(ValueError):
        clf.fit(X, y)
