import numpy as np
import pandas as pd


def accuracy(y_true, y_pred) -> float:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if y_true.shape != y_pred.shape:
        raise ValueError("y_true and y_pred must have the same shape.")
    if y_true.size == 0:
        raise ValueError("Cannot compute accuracy on empty arrays.")
    return float(np.mean(y_true == y_pred))


def information_transfer_rate(n_classes: int, accuracy_value: float, trial_seconds: float) -> float:
    """Compute bits/min for a synchronous BCI selection task."""
    if n_classes < 2:
        raise ValueError("n_classes must be >= 2.")
    if trial_seconds <= 0:
        raise ValueError("trial_seconds must be positive.")
    p = float(accuracy_value)
    if p < 0 or p > 1:
        raise ValueError("accuracy must be in [0, 1].")
    if p <= 0:
        bits = np.log2(n_classes) + np.log2(1 / (n_classes - 1))
    elif p >= 1:
        bits = np.log2(n_classes)
    else:
        bits = (
            np.log2(n_classes)
            + p * np.log2(p)
            + (1 - p) * np.log2((1 - p) / (n_classes - 1))
        )
    return float(max(0.0, bits * 60.0 / trial_seconds))


def label_wearability_condition(
    mean_accuracy: float,
    subject_failure_rate: float,
    usable_threshold: float = 0.70,
    max_failure_rate: float = 0.20,
) -> str:
    """Engineering label, not a clinical/regulatory threshold."""
    if mean_accuracy >= usable_threshold and subject_failure_rate <= max_failure_rate:
        return "usable"
    if mean_accuracy >= usable_threshold and subject_failure_rate > max_failure_rate:
        return "borderline_tail_risk"
    return "not_usable"


def summarize_subject_metrics(
    df: pd.DataFrame,
    usable_threshold: float = 0.70,
    max_failure_rate: float = 0.20,
    group_cols=None,
) -> pd.DataFrame:
    df = df.copy()
    if group_cols is None:
        # Keep older per-subject tables readable while making new benchmark outputs explicit.
        if "split" not in df.columns:
            df["split"] = "unspecified"
        if "channel_policy" not in df.columns:
            df["channel_policy"] = "unspecified"
        group_cols = ["dataset", "method", "split", "window_s", "channel_count", "channel_policy"]
    required = set(group_cols + ["subject", "accuracy"])
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    rows = []
    for keys, g in df.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        subject_acc = g.groupby("subject")["accuracy"].mean()
        failure_rate = float(np.mean(subject_acc < usable_threshold))
        mean_acc = float(subject_acc.mean())
        row = dict(zip(group_cols, keys))
        row.update(
            n_subjects=int(subject_acc.shape[0]),
            mean_accuracy=mean_acc,
            median_accuracy=float(subject_acc.median()),
            worst_subject_accuracy=float(subject_acc.min()),
            best_subject_accuracy=float(subject_acc.max()),
            subject_failure_rate=failure_rate,
            usable_subject_rate=float(np.mean(subject_acc >= usable_threshold)),
            usable_threshold=float(usable_threshold),
            max_failure_rate=float(max_failure_rate),
            wearability_condition_label=label_wearability_condition(
                mean_acc, failure_rate, usable_threshold, max_failure_rate
            ),
        )
        rows.append(row)
    return pd.DataFrame(rows)


def compute_degradation(
    df: pd.DataFrame,
    baseline_channel_count: int | None = None,
    baseline_window_s: float | None = None,
    usable_threshold: float = 0.70,
) -> pd.DataFrame:
    """Add degradation columns relative to max-channel/max-window baseline per subject/method."""
    required = {"dataset", "subject", "method", "split", "window_s", "channel_count", "accuracy"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    out = df.copy()
    if "itr_bits_min" not in out.columns:
        out["itr_bits_min"] = np.nan
    key_cols = ["dataset", "subject", "method", "split"]
    base_rows = []
    for keys, g in out.groupby(key_cols, dropna=False):
        b_ch = g["channel_count"].max() if baseline_channel_count is None else baseline_channel_count
        b_win = g["window_s"].max() if baseline_window_s is None else baseline_window_s
        b = g[(g["channel_count"] == b_ch) & (g["window_s"] == b_win)]
        if b.empty:
            continue
        row = dict(zip(key_cols, keys if isinstance(keys, tuple) else (keys,)))
        row.update(
            baseline_accuracy=float(b["accuracy"].mean()),
            baseline_itr_bits_min=float(b["itr_bits_min"].mean()) if b["itr_bits_min"].notna().any() else np.nan,
        )
        base_rows.append(row)
    if not base_rows:
        out["baseline_accuracy"] = np.nan
        out["accuracy_drop_from_baseline"] = np.nan
        out["relative_accuracy_drop"] = np.nan
        out["itr_drop_from_baseline"] = np.nan
        out["usable_status_changed"] = pd.NA
        return out
    base = pd.DataFrame(base_rows)
    out = out.merge(base, on=key_cols, how="left")
    out["accuracy_drop_from_baseline"] = out["baseline_accuracy"] - out["accuracy"]
    out["relative_accuracy_drop"] = out["accuracy_drop_from_baseline"] / out["baseline_accuracy"]
    out["itr_drop_from_baseline"] = out["baseline_itr_bits_min"] - out["itr_bits_min"]
    out["usable_status_changed"] = (out["baseline_accuracy"] >= usable_threshold) & (out["accuracy"] < usable_threshold)
    return out
