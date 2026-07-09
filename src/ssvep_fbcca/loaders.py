"""Dataset loaders for SSVEP wearability benchmarking.

The benchmark core does not depend on MOABB. MOABB support is optional and deliberately
thin, because dataset class names and availability should be checked at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass
class SubjectData:
    dataset: str
    subject: str | int
    X: np.ndarray
    y: np.ndarray
    sfreq: float
    freqs: list[float]
    channel_names: list[str]
    electrode_type: str | None = None
    notes: str | None = None


def load_npz_dataset(path: str, dataset_name: str = "custom_npz") -> list[SubjectData]:
    """Load a simple local NPZ dataset for reproducible experiments.

    Expected keys:
    - X: (n_trials, n_channels, n_times)
    - y: (n_trials,)
    - sfreq: scalar
    - freqs: array/list of stimulation frequencies
    - channel_names: array/list of strings

    Optional:
    - subject: scalar/string
    - electrode_type: wet/dry/unknown
    """
    data = np.load(path, allow_pickle=True)
    required = ["X", "y", "sfreq", "freqs", "channel_names"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"NPZ file is missing keys: {missing}")
    subject = data["subject"].item() if "subject" in data else "unknown"
    electrode_type = data["electrode_type"].item() if "electrode_type" in data else None
    return [
        SubjectData(
            dataset=dataset_name,
            subject=subject,
            X=data["X"],
            y=data["y"],
            sfreq=float(data["sfreq"]),
            freqs=[float(x) for x in data["freqs"]],
            channel_names=[str(x) for x in data["channel_names"]],
            electrode_type=electrode_type,
        )
    ]


def load_moabb_dataset(dataset_key: str, subjects=None) -> list[SubjectData]:
    """Load selected MOABB SSVEP datasets.

    This function is intentionally conservative. It supports a small mapping and fails loudly
    when MOABB is not installed or when a dataset does not expose the expected paradigm API.
    """
    try:
        from moabb.datasets import Kalunga2016, Lee2019_SSVEP, MAMEM1, MAMEM2, MAMEM3, Nakanishi2015
        from moabb.paradigms import SSVEP
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "MOABB/MNE are optional dependencies. Install with: pip install -e .[moabb]"
        ) from exc

    mapping: dict[str, Callable[[], object]] = {
        "nakanishi2015": Nakanishi2015,
        "lee2019_ssvep": Lee2019_SSVEP,
        "kalunga2016": Kalunga2016,
        "mamem1": MAMEM1,
        "mamem2": MAMEM2,
        "mamem3": MAMEM3,
    }
    key = dataset_key.lower()
    if key not in mapping:
        raise ValueError(f"Unknown MOABB dataset key {dataset_key!r}. Known: {sorted(mapping)}")

    dataset = mapping[key]()
    if subjects is None:
        subjects = dataset.subject_list[:3]  # safe default for a first run; user can override

    paradigm = SSVEP()
    X, y, metadata = paradigm.get_data(dataset=dataset, subjects=list(subjects))
    # MOABB usually returns X as (trials, channels, times), labels as frequencies/strings.
    ch_names = getattr(paradigm, "channels", None)
    if ch_names is None:
        ch_names = [f"ch{i}" for i in range(X.shape[1])]
    # Map labels to integer classes while preserving sorted frequency-like labels.
    unique_labels = sorted(set(y), key=lambda x: float(x) if str(x).replace('.', '', 1).isdigit() else str(x))
    label_to_int = {lab: i for i, lab in enumerate(unique_labels)}
    y_int = np.asarray([label_to_int[lab] for lab in y])
    try:
        freqs = [float(lab) for lab in unique_labels]
    except Exception:
        freqs = list(range(1, len(unique_labels) + 1))

    out = []
    for subj in sorted(metadata["subject"].unique()):
        idx = metadata["subject"].to_numpy() == subj
        out.append(
            SubjectData(
                dataset=key,
                subject=subj,
                X=X[idx],
                y=y_int[idx],
                sfreq=250.0,
                freqs=freqs,
                channel_names=list(ch_names),
                electrode_type=None,
                notes=(
                    "Provisional sfreq=250.0 used by the generic MOABB loader. "
                    "Before reporting scientific results, verify sampling frequency from "
                    "dataset/raw metadata or use a dataset-specific loader."
                ),
            )
        )
    return out
