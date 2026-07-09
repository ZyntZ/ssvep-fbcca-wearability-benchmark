import numpy as np

from .validation import validate_freqs, validate_sfreq


def make_reference_signals(
    freqs,
    sfreq: float,
    n_times: int,
    n_harmonics: int = 3,
) -> dict[float, np.ndarray]:
    """Create sine/cosine SSVEP reference signals for each stimulation frequency.

    Returns a dict mapping frequency -> array with shape (2*n_harmonics, n_times).
    """
    freqs = validate_freqs(freqs)
    sfreq = validate_sfreq(sfreq)
    if n_times <= 0:
        raise ValueError("n_times must be positive.")
    if n_harmonics <= 0:
        raise ValueError("n_harmonics must be positive.")

    t = np.arange(n_times, dtype=float) / sfreq
    refs: dict[float, np.ndarray] = {}
    for f in freqs:
        rows = []
        for h in range(1, n_harmonics + 1):
            rows.append(np.sin(2 * np.pi * h * f * t))
            rows.append(np.cos(2 * np.pi * h * f * t))
        refs[float(f)] = np.vstack(rows)
    return refs
