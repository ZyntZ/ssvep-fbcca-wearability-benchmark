import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin

from .cca import CCAClassifier
from .filterbank import apply_filterbank, default_filterbank
from .validation import validate_epochs, validate_freqs, validate_labels, validate_sfreq


def default_fbcca_weights(n_bands: int, a: float = 1.25, b: float = 0.25) -> np.ndarray:
    """Common FBCCA sub-band weighting: w_m = m^{-a} + b, m starts at 1."""
    if n_bands <= 0:
        raise ValueError("n_bands must be positive.")
    m = np.arange(1, n_bands + 1, dtype=float)
    return np.power(m, -a) + b


class FBCCAClassifier(BaseEstimator, ClassifierMixin):
    """Filter Bank Canonical Correlation Analysis for SSVEP classification.

    The classifier applies several band-pass filters, computes CCA scores in each sub-band,
    then combines squared correlations with sub-band weights.
    """

    def __init__(
        self,
        sfreq: float,
        freqs,
        n_harmonics: int = 3,
        filterbank=None,
        weights=None,
        filter_order: int = 4,
    ):
        self.sfreq = sfreq
        self.freqs = freqs
        self.n_harmonics = n_harmonics
        self.filterbank = filterbank
        self.weights = weights
        self.filter_order = filter_order

    def fit(self, X, y=None):
        X = validate_epochs(X)
        self.sfreq_ = validate_sfreq(self.sfreq)
        self.freqs_ = validate_freqs(self.freqs)
        if y is not None:
            validate_labels(y, X.shape[0])
        if self.n_harmonics <= 0:
            raise ValueError("n_harmonics must be positive.")
        if self.filterbank is None:
            self.filterbank_ = default_filterbank(self.freqs_)
        else:
            self.filterbank_ = list(self.filterbank)
        if self.weights is None:
            self.weights_ = default_fbcca_weights(len(self.filterbank_))
        else:
            self.weights_ = np.asarray(self.weights, dtype=float)
            if len(self.weights_) != len(self.filterbank_):
                raise ValueError("weights length must match filterbank length.")
        self.classes_ = np.arange(len(self.freqs_))
        return self

    def predict_scores(self, X) -> np.ndarray:
        X = validate_epochs(X)
        if not hasattr(self, "filterbank_"):
            raise RuntimeError("Classifier is not fitted. Call fit(X, y) first.")
        X_bands = apply_filterbank(X, self.sfreq_, self.filterbank_, order=self.filter_order)
        combined = np.zeros((X.shape[0], len(self.freqs_)), dtype=float)
        for band_idx, X_band in enumerate(X_bands):
            cca = CCAClassifier(
                sfreq=self.sfreq_,
                freqs=self.freqs_,
                n_harmonics=self.n_harmonics,
            )
            cca.fit(X_band)
            scores = cca.predict_scores(X_band)
            combined += self.weights_[band_idx] * np.square(scores)
        return combined

    def predict(self, X) -> np.ndarray:
        scores = self.predict_scores(X)
        return self.classes_[np.argmax(scores, axis=1)]
