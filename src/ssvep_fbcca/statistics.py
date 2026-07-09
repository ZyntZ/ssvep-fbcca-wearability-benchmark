import numpy as np
import pandas as pd
from scipy import stats


def bootstrap_ci(values, statistic="mean", n_boot=2000, ci=0.95, random_state=42):
    """Bootstrap confidence interval for a one-sample statistic."""
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        raise ValueError("No finite values for bootstrap_ci.")
    rng = np.random.default_rng(random_state)
    boots = []
    for _ in range(int(n_boot)):
        sample = rng.choice(x, size=x.size, replace=True)
        if statistic == "mean":
            boots.append(np.mean(sample))
        elif statistic == "median":
            boots.append(np.median(sample))
        else:
            raise ValueError("statistic must be 'mean' or 'median'.")
    alpha = 1 - ci
    return {
        "statistic": statistic,
        "estimate": float(np.mean(x) if statistic == "mean" else np.median(x)),
        "ci_low": float(np.quantile(boots, alpha / 2)),
        "ci_high": float(np.quantile(boots, 1 - alpha / 2)),
        "n": int(x.size),
        "n_boot": int(n_boot),
        "ci": float(ci),
    }


def benjamini_hochberg(p_values):
    """Benjamini-Hochberg FDR correction."""
    p = np.asarray(p_values, dtype=float)
    out = np.full_like(p, np.nan, dtype=float)
    finite = np.isfinite(p)
    if not finite.any():
        return out
    pf = p[finite]
    order = np.argsort(pf)
    ranked = pf[order]
    m = len(ranked)
    adjusted = ranked * m / np.arange(1, m + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.clip(adjusted, 0, 1)
    tmp = np.empty_like(adjusted)
    tmp[order] = adjusted
    out[finite] = tmp
    return out


def paired_degradation_tests(
    df: pd.DataFrame,
    method="fbcca",
    compare="channel",
    baseline_channel_count=None,
    target_channel_count=1,
    baseline_window_s=None,
    target_window_s=1.0,
):
    """Paired Wilcoxon tests for subject-level degradation.

    compare='channel': baseline max/selected channel at same window vs target_channel_count.
    compare='window': baseline max/selected window at same channel count vs target_window_s.
    """
    g = df[df["method"] == method].copy()
    if g.empty:
        return pd.DataFrame()
    rows = []
    group_cols = ["dataset", "split"]
    for keys, d in g.groupby(group_cols, dropna=False):
        dataset, split = keys
        if compare == "channel":
            windows = sorted(d["window_s"].unique()) if baseline_window_s is None else [baseline_window_s]
            for win in windows:
                dd = d[d["window_s"] == win]
                b_ch = dd["channel_count"].max() if baseline_channel_count is None else baseline_channel_count
                b = dd[dd["channel_count"] == b_ch].groupby("subject")["accuracy"].mean()
                t = dd[dd["channel_count"] == target_channel_count].groupby("subject")["accuracy"].mean()
                label = f"channel_{b_ch}_vs_{target_channel_count}_at_{win}s"
                rows.append(_paired_row(dataset, split, label, b, t))
        elif compare == "window":
            counts = sorted(d["channel_count"].unique()) if baseline_channel_count is None else [baseline_channel_count]
            for count in counts:
                dd = d[d["channel_count"] == count]
                b_win = dd["window_s"].max() if baseline_window_s is None else baseline_window_s
                b = dd[dd["window_s"] == b_win].groupby("subject")["accuracy"].mean()
                t = dd[dd["window_s"] == target_window_s].groupby("subject")["accuracy"].mean()
                label = f"window_{b_win}s_vs_{target_window_s}s_at_{count}ch"
                rows.append(_paired_row(dataset, split, label, b, t))
        else:
            raise ValueError("compare must be 'channel' or 'window'.")
    out = pd.DataFrame([r for r in rows if r is not None])
    if not out.empty:
        out["p_value_fdr"] = benjamini_hochberg(out["p_value"].to_numpy())
    return out


def _paired_row(dataset, split, comparison, baseline: pd.Series, target: pd.Series):
    common = baseline.index.intersection(target.index)
    if len(common) < 2:
        return None
    b = baseline.loc[common].to_numpy(dtype=float)
    t = target.loc[common].to_numpy(dtype=float)
    diff = b - t
    try:
        stat, p = stats.wilcoxon(diff, zero_method="wilcox", alternative="two-sided")
    except ValueError:
        stat, p = np.nan, np.nan
    ci = bootstrap_ci(diff, statistic="mean")
    return {
        "dataset": dataset,
        "split": split,
        "comparison": comparison,
        "test": "Wilcoxon signed-rank",
        "n_subjects": int(len(common)),
        "mean_accuracy_drop": float(np.mean(diff)),
        "median_accuracy_drop": float(np.median(diff)),
        "statistic": float(stat) if np.isfinite(stat) else np.nan,
        "p_value": float(p) if np.isfinite(p) else np.nan,
        "ci_low": ci["ci_low"],
        "ci_high": ci["ci_high"],
    }
