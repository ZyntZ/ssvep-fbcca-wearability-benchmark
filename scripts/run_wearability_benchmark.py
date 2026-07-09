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

