import numpy as np
import pandas as pd

from .channel_ablation import apply_channel_subset, make_channel_subsets
from .cca import CCAClassifier
from .fbcca import FBCCAClassifier
from .metrics import accuracy, information_transfer_rate


def crop_window(X, sfreq: float, window_s: float):
    n_times = int(round(float(window_s) * float(sfreq)))
    if n_times <= 0:
        raise ValueError("window_s too short for sampling frequency.")
    if n_times > X.shape[-1]:
        raise ValueError(f"Requested {window_s}s window exceeds epoch length.")
    return X[..., :n_times]


def make_classifier(method: str, sfreq: float, freqs, filterbank=None, n_harmonics: int = 3):
    method = method.lower()
    if method == "cca":
        return CCAClassifier(sfreq=sfreq, freqs=freqs, n_harmonics=n_harmonics)
    if method == "fbcca":
        return FBCCAClassifier(sfreq=sfreq, freqs=freqs, n_harmonics=n_harmonics, filterbank=filterbank)
    raise ValueError(f"Unknown method: {method}")


def make_stratified_split(y, train_fraction: float = 0.5, random_state: int = 42):
    y = np.asarray(y)
    rng = np.random.default_rng(random_state)
    train_idx = []
    test_idx = []
    for cls in np.unique(y):
        idx = np.where(y == cls)[0]
        rng.shuffle(idx)
        n_train = max(1, int(round(train_fraction * len(idx))))
        if n_train >= len(idx):
            n_train = len(idx) - 1
        train_idx.extend(idx[:n_train])
        test_idx.extend(idx[n_train:])
    train_idx = np.asarray(train_idx)
    test_idx = np.asarray(test_idx)
    if len(test_idx) == 0:
        raise ValueError("No test samples after split; dataset has too few trials per class.")
    return train_idx, test_idx


def make_group_split(groups, test_group=None):
    groups = np.asarray(groups)
    unique = sorted(pd.unique(groups))
    if len(unique) < 2:
        raise ValueError("Group split requires at least two groups.")
    if test_group is None:
        test_group = unique[-1]
    test_idx = np.where(groups == test_group)[0]
    train_idx = np.where(groups != test_group)[0]
    if len(train_idx) == 0 or len(test_idx) == 0:
        raise ValueError("Invalid group split produced empty train or test set.")
    return train_idx, test_idx


def evaluate_subject(
    X,
    y,
    sfreq: float,
    freqs,
    subject,
    dataset: str,
    channel_names,
    windows=(1.0, 2.0, 3.0),
    channel_counts=(8, 6, 4, 2, 1),
    methods=("cca", "fbcca"),
    filterbank=None,
    train_fraction: float = 0.5,
    random_state: int = 42,
    split: str = "stratified_pilot",
    groups=None,
    channel_policy: str = "occipital_first",
    n_random_subsets: int = 20,
    n_harmonics: int = 3,
):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    rows = []
    if split == "stratified_pilot":
        train_idx, test_idx = make_stratified_split(y, train_fraction, random_state)
    elif split in {"leave_one_group_out", "cross_session", "leave_one_run_out"}:
        if groups is None:
            raise ValueError(f"split={split} requires groups/session/run labels.")
        train_idx, test_idx = make_group_split(groups)
    else:
        raise ValueError("Unknown split. Use stratified_pilot, leave_one_group_out, cross_session, or leave_one_run_out.")
    valid_counts = [c for c in channel_counts if c <= len(channel_names)]
    for window_s in windows:
        Xw = crop_window(X, sfreq, window_s)
        for count in valid_counts:
            subsets = make_channel_subsets(channel_names, count, policy=channel_policy, n_random=n_random_subsets, random_state=random_state)
            for subset_id, selected in enumerate(subsets):
                Xc = apply_channel_subset(Xw, channel_names, selected)
                X_train, y_train = Xc[train_idx], y[train_idx]
                X_test, y_test = Xc[test_idx], y[test_idx]
                for method in methods:
                    clf = make_classifier(method, sfreq=sfreq, freqs=freqs, filterbank=filterbank, n_harmonics=n_harmonics)
                    clf.fit(X_train, y_train)
                    pred = clf.predict(X_test)
                    acc = accuracy(y_test, pred)
                    itr = information_transfer_rate(len(freqs), acc, float(window_s))
                    rows.append(dict(
                        dataset=dataset, subject=subject, method=method, split=split,
                        window_s=float(window_s), channel_count=int(count), channel_policy=channel_policy,
                        subset_id=int(subset_id), channels=";".join(selected), n_train=int(len(train_idx)),
                        n_test=int(len(test_idx)), accuracy=acc, itr_bits_min=itr, n_harmonics=int(n_harmonics),
                    ))
    return pd.DataFrame(rows)
