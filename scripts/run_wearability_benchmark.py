#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from ssvep_fbcca.evaluation import evaluate_subject
from ssvep_fbcca.loaders import load_moabb_dataset, load_npz_dataset
from ssvep_fbcca.metrics import compute_degradation, summarize_subject_metrics
from ssvep_fbcca.plotting import (
    plot_channel_degradation,
    plot_channel_window_heatmap,
    plot_per_subject_degradation,
    plot_subject_failure_rate_heatmap,
)
from ssvep_fbcca.statistics import paired_degradation_tests


def parse_args():
    p = argparse.ArgumentParser(description="Run SSVEP-FBCCA wearability benchmark")
    p.add_argument("--config", default=None, help="YAML config file. CLI args override config.")
    p.add_argument("--dataset", default=None, help="MOABB dataset key or path to .npz")
    p.add_argument("--dataset-type", choices=["moabb", "npz"], default=None)
    p.add_argument("--subjects", nargs="*", default=None, help="Optional subject IDs for MOABB")
    p.add_argument("--windows", nargs="+", type=float, default=None)
    p.add_argument("--channel-counts", nargs="+", type=int, default=None)
    p.add_argument("--methods", nargs="+", default=None)
    p.add_argument("--split", default=None, choices=["stratified_pilot", "leave_one_group_out", "cross_session", "leave_one_run_out"])
    p.add_argument("--channel-policy", default=None, choices=["occipital_first", "random_subsets", "all_combinations_if_small"])
    p.add_argument("--n-random-subsets", type=int, default=None)
    p.add_argument("--usable-threshold", type=float, default=None)
    p.add_argument("--max-failure-rate", type=float, default=None)
    p.add_argument("--out", default=None)
    return p.parse_args()


def merge_config(args):
    cfg = {}
    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
    defaults = {
        "dataset_type": "moabb",
        "windows": [1.0, 2.0, 3.0],
        "channel_counts": [8, 6, 4, 2, 1],
        "methods": ["cca", "fbcca"],
        "split": "stratified_pilot",
        "channel_policy": "occipital_first",
        "n_random_subsets": 20,
        "usable_threshold": 0.70,
        "max_failure_rate": 0.20,
        "out": "results/run",
    }
    cfg = {**defaults, **cfg}
    for cli_name, cfg_name in [
        ("dataset", "dataset"), ("dataset_type", "dataset_type"), ("windows", "windows"),
        ("channel_counts", "channel_counts"), ("methods", "methods"), ("split", "split"),
        ("channel_policy", "channel_policy"), ("n_random_subsets", "n_random_subsets"),
        ("usable_threshold", "usable_threshold"), ("max_failure_rate", "max_failure_rate"),
        ("out", "out"),
    ]:
        val = getattr(args, cli_name)
        if val is not None:
            cfg[cfg_name] = val
    if not cfg.get("dataset"):
        raise ValueError("Dataset must be provided via --dataset or config file.")
    return cfg


def main():
    args = parse_args()
    cfg = merge_config(args)
    out = Path(cfg["out"])
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    (out / "reports").mkdir(parents=True, exist_ok=True)

    if cfg["dataset_type"] == "npz":
        subjects = load_npz_dataset(cfg["dataset"], dataset_name=Path(cfg["dataset"]).stem)
    else:
        subject_ids = None
        if args.subjects:
            subject_ids = [int(s) if str(s).isdigit() else s for s in args.subjects]
        subjects = load_moabb_dataset(cfg["dataset"], subjects=subject_ids)

    rows = []
    for sd in subjects:
        df = evaluate_subject(
            X=sd.X,
            y=sd.y,
            sfreq=sd.sfreq,
            freqs=sd.freqs,
            subject=sd.subject,
            dataset=sd.dataset,
            channel_names=sd.channel_names,
            windows=cfg["windows"],
            channel_counts=cfg["channel_counts"],
            methods=cfg["methods"],
            split=cfg["split"],
            channel_policy=cfg["channel_policy"],
            n_random_subsets=cfg["n_random_subsets"],
        )
        df["electrode_type"] = sd.electrode_type if sd.electrode_type is not None else "unknown"
        df["dataset_notes"] = sd.notes
        rows.append(df)

    per_subject = pd.concat(rows, ignore_index=True)
    per_subject = compute_degradation(per_subject, usable_threshold=cfg["usable_threshold"])
    per_subject.to_csv(out / "tables" / "per_subject_results.csv", index=False)
    per_subject.to_csv(out / "tables" / "per_subject_degradation.csv", index=False)

    summary = summarize_subject_metrics(
        per_subject,
        usable_threshold=cfg["usable_threshold"],
        max_failure_rate=cfg["max_failure_rate"],
    )
    summary.to_csv(out / "tables" / "condition_summary.csv", index=False)
    summary.to_csv(out / "tables" / "window_channel_summary.csv", index=False)

    stats_channel = paired_degradation_tests(per_subject, compare="channel")
    stats_window = paired_degradation_tests(per_subject, compare="window")
    stats_all = pd.concat([stats_channel, stats_window], ignore_index=True)
    stats_all.to_csv(out / "tables" / "statistical_tests.csv", index=False)

    plot_channel_window_heatmap(summary, out / "figures" / "fbcca_channel_window_heatmap_by_dataset.png")
    plot_subject_failure_rate_heatmap(summary, out / "figures" / "subject_failure_rate_heatmap.png")
    plot_channel_degradation(summary, out / "figures" / "channel_degradation_curve_by_window.png")
    plot_per_subject_degradation(per_subject, out / "figures" / "per_subject_degradation_spaghetti.png")

    report = out / "reports" / "wearability_readiness_report.md"
    report.write_text(
        "# Wearability readiness report\n\n"
        "This report is generated from benchmark outputs. It should be interpreted only after "
        "checking dataset metadata, split strategy, channel policy, and ITR assumptions.\n\n"
        f"- Dataset input: `{cfg['dataset']}`\n"
        f"- Dataset type: `{cfg['dataset_type']}`\n"
        f"- Split: `{cfg['split']}`\n"
        f"- Windows: {cfg['windows']}\n"
        f"- Channel counts: {cfg['channel_counts']}\n"
        f"- Channel policy: `{cfg['channel_policy']}`\n"
        f"- Methods: {cfg['methods']}\n"
        f"- Usable threshold: {cfg['usable_threshold']}\n"
        f"- Max failure rate for 'usable' label: {cfg['max_failure_rate']}\n\n"
        "Key files:\n"
        "- `tables/per_subject_degradation.csv`\n"
        "- `tables/condition_summary.csv`\n"
        "- `tables/statistical_tests.csv`\n"
        "- `figures/subject_failure_rate_heatmap.png`\n\n"
        "No clinical claims are made. Wearability labels are engineering summaries.\n",
        encoding="utf-8",
    )
    print(f"Wrote benchmark outputs to {out}")


if __name__ == "__main__":
    main()
