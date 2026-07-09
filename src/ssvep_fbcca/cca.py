import numpy as np
from sklearn.cross_decomposition import CCA
from sklearn.base import BaseEstimator, ClassifierMixin

from .reference import make_reference_signals
from .validation import validate_epochs, validate_freqs, validate_labels, validate_sfreq


class CCAClassifier(BaseEstimator, ClassifierMixin):
    """Canonical correlation analysis baseline for SSVEP classification.

    Parameters
    ----------
    sfreq:
        Sampling frequency in Hz.
    freqs:
        Stimulation frequencies. Label 0 maps to freqs[0], label 1 to freqs[1], etc.
    n_harmonics:
        Number of sine/cosine harmonics in reference signals.
    """

    def __init__(self, sfreq: float, freqs, n_harmonics: int = 3):
        self.sfreq = sfreq
        self.freqs = freqs
        self.n_harmonics = n_harmonics

    def fit(self, X, y=None):
        X = validate_epochs(X)
        self.sfreq_ = validate_sfreq(self.sfreq)
        self.freqs_ = validate_freqs(self.freqs)
        if y is not None:
            validate_labels(y, X.shape[0])
        if self.n_harmonics <= 0:
            raise ValueError("n_harmonics must be positive.")
        self.n_times_ = X.shape[2]
        self.references_ = make_reference_signals(
            self.freqs_, self.sfreq_, self.n_times_, self.n_harmonics
        )
        self.classes_ = np.arange(len(self.freqs_))
        return self

    def _score_single_trial(self, trial: np.ndarray) -> np.ndarray:
        # trial: (n_channels, n_times). sklearn CCA expects samples x features.
        eeg = trial.T
        scores = []
        for f in self.freqs_:
            ref = self.references_[float(f)].T
            cca = CCA(n_components=1, max_iter=1000)
            try:
                U, V = cca.fit_transform(eeg, ref)
                corr = np.corrcoef(U[:, 0], V[:, 0])[0, 1]
                if not np.isfinite(corr):
                    corr = 0.0
            except Exception:
                corr = 0.0
            scores.append(float(corr))
        return np.asarray(scores)

    def predict_scores(self, X) -> np.ndarray:
        X = validate_epochs(X)
        if not hasattr(self, "references_"):
            raise RuntimeError("Classifier is not fitted. Call fit(X, y) first.")
        if X.shape[2] != self.n_times_:
            # Rebuild references for the new window length. This supports window sweeps.
            self.n_times_ = X.shape[2]
            self.references_ = make_reference_signals(
                self.freqs_, self.sfreq_, self.n_times_, self.n_harmonics
            )
        return np.vstack([self._score_single_trial(trial) for trial in X])

    def predict(self, X) -> np.ndarray:
        scores = self.predict_scores(X)
        return self.classes_[np.argmax(scores, axis=1)]
