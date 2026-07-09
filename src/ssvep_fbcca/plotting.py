from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_channel_window_heatmap(summary_df: pd.DataFrame, out_file):
    return plot_metric_heatmap(summary_df, out_file, metric="mean_accuracy", method="fbcca")


def plot_metric_heatmap(summary_df: pd.DataFrame, out_file, metric="mean_accuracy", method="fbcca"):
    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    d = summary_df[summary_df["method"] == method].copy()
    if d.empty:
        return None
    datasets = list(d["dataset"].dropna().unique()) if "dataset" in d.columns else [None]
    n = len(datasets)
    fig, axes = plt.subplots(1, n, figsize=(6 * n, 4.5), squeeze=False)
    for ax, dataset in zip(axes[0], datasets):
        dd = d if dataset is None else d[d["dataset"] == dataset]
        pivot = dd.pivot_table(index="channel_count", columns="window_s", values=metric, aggfunc="mean").sort_index(ascending=False)
        sns.heatmap(pivot, annot=True, fmt=".2f", cmap="viridis", vmin=0, vmax=1, ax=ax)
        ax.set_title(f"{method.upper()} {metric}" + (f"\n{dataset}" if dataset is not None else ""))
        ax.set_xlabel("Window length (s)")
        ax.set_ylabel("Channel count")
    plt.tight_layout()
    plt.savefig(out_file, dpi=180)
    plt.close()
    return out_file


def plot_subject_failure_rate_heatmap(summary_df: pd.DataFrame, out_file, method="fbcca"):
    return plot_metric_heatmap(summary_df, out_file, metric="subject_failure_rate", method=method)


def plot_channel_degradation(summary_df: pd.DataFrame, out_file):
    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    fbcca = summary_df[summary_df["method"] == "fbcca"].copy()
    if fbcca.empty:
        return None
    plt.figure(figsize=(7, 4.5))
    sns.lineplot(
        data=fbcca,
        x="channel_count",
        y="mean_accuracy",
        hue="window_s",
        style="dataset" if "dataset" in fbcca.columns else None,
        markers=True,
        dashes=False,
    )
    plt.gca().invert_xaxis()
    plt.ylim(0, 1)
    plt.title("FBCCA channel-count degradation")
    plt.xlabel("Channel count")
    plt.ylabel("Mean accuracy")
    plt.tight_layout()
    plt.savefig(out_file, dpi=180)
    plt.close()
    return out_file


def plot_per_subject_degradation(per_subject_df: pd.DataFrame, out_file, method="fbcca"):
    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    d = per_subject_df[per_subject_df["method"] == method].copy()
    if d.empty or "accuracy_drop_from_baseline" not in d.columns:
        return None
    plt.figure(figsize=(8, 4.8))
    sns.lineplot(
        data=d,
        x="channel_count",
        y="accuracy_drop_from_baseline",
        hue="window_s",
        units="subject",
        estimator=None,
        alpha=0.35,
    )
    plt.gca().invert_xaxis()
    plt.title("Per-subject FBCCA degradation from baseline")
    plt.xlabel("Channel count")
    plt.ylabel("Accuracy drop from baseline")
    plt.tight_layout()
    plt.savefig(out_file, dpi=180)
    plt.close()
    return out_file
