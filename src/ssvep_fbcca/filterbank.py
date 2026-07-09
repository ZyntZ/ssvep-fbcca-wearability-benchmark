import numpy as np
from scipy.signal import butter, sosfiltfilt

from .validation import validate_epochs, validate_sfreq


def default_filterbank(freqs, n_bands: int = 5, bandwidth: float = 8.0, low_margin: float = 2.0):
    """Create simple SSVEP-oriented sub-bands around the stimulation frequency range.

    This is a pragmatic default, not a claim of optimality. Benchmark reports must document
    exact filter bands used.
    """
    freqs = np.asarray(freqs, dtype=float)
    f_min = max(1.0, float(np.min(freqs)) - low_margin)
    bands = []
    for i in range(n_bands):
        low = f_min + i * bandwidth
        high = low + bandwidth
        bands.append((low, high))
    return bands


def apply_filterbank(X, sfreq: float, filterbank, order: int = 4) -> list[np.ndarray]:
    """Apply band-pass filters to epochs.

    Parameters
    ----------
    X:
        Epoch array with shape (n_trials, n_channels, n_times).
    sfreq:
        Sampling frequency.
    filterbank:
        List of (low, high) Hz tuples.
    """
    X = validate_epochs(X)
    sfreq = validate_sfreq(sfreq)
    nyq = sfreq / 2.0
    filtered = []
    for low, high in filterbank:
        if low <= 0 or high <= low or high >= nyq:
            raise ValueError(f"Invalid filter band {(low, high)} for sfreq={sfreq}.")
        sos = butter(order, [low / nyq, high / nyq], btype="bandpass", output="sos")
        filtered.append(sosfiltfilt(sos, X, axis=-1))
    return filtered
