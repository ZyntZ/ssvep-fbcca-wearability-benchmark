import numpy as np


def validate_epochs(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=float)
    if X.ndim != 3:
        raise ValueError("X must have shape (n_trials, n_channels, n_times).")
    if X.shape[0] == 0 or X.shape[1] == 0 or X.shape[2] == 0:
        raise ValueError("X dimensions must be non-zero.")
    if not np.isfinite(X).all():
        raise ValueError("X contains NaN or infinite values.")
    return X


def validate_labels(y, n_trials: int | None = None) -> np.ndarray:
    y = np.asarray(y)
    if y.ndim != 1:
        raise ValueError("y must be a 1D label vector.")
    if n_trials is not None and len(y) != n_trials:
        raise ValueError("len(y) must match X.shape[0].")
    if not np.isfinite(y.astype(float)).all():
        raise ValueError("y contains NaN or infinite values.")
    return y


def validate_sfreq(sfreq: float) -> float:
    sfreq = float(sfreq)
    if sfreq <= 0:
        raise ValueError("sfreq must be positive.")
    return sfreq


def validate_freqs(freqs) -> np.ndarray:
    freqs = np.asarray(freqs, dtype=float)
    if freqs.ndim != 1 or len(freqs) == 0:
        raise ValueError("freqs must be a non-empty 1D array/list.")
    if np.any(freqs <= 0):
        raise ValueError("All frequencies must be positive.")
    return freqs
