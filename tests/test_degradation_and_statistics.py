import pandas as pd
import pytest

from ssvep_fbcca.metrics import compute_degradation, label_wearability_condition
from ssvep_fbcca.statistics import benjamini_hochberg, bootstrap_ci, paired_degradation_tests


def test_compute_degradation_adds_expected_columns():
    df = pd.DataFrame({
        "dataset": ["d", "d"],
        "subject": [1, 1],
        "method": ["fbcca", "fbcca"],
        "split": ["stratified_pilot", "stratified_pilot"],
        "window_s": [3.0, 1.0],
        "channel_count": [8, 1],
        "accuracy": [0.9, 0.6],
        "itr_bits_min": [10.0, 5.0],
    })
    out = compute_degradation(df, usable_threshold=0.7)
    low = out[out["channel_count"] == 1].iloc[0]
    assert low["accuracy_drop_from_baseline"] == pytest.approx(0.3)
    assert bool(low["usable_status_changed"]) is True


def test_label_wearability_condition():
    assert label_wearability_condition(0.8, 0.1) == "usable"
    assert label_wearability_condition(0.8, 0.4) == "borderline_tail_risk"
    assert label_wearability_condition(0.6, 0.1) == "not_usable"


def test_benjamini_hochberg_monotonic_bounds():
    adj = benjamini_hochberg([0.01, 0.02, 0.5])
    assert (adj >= 0).all() and (adj <= 1).all()


def test_bootstrap_ci_returns_bounds():
    ci = bootstrap_ci([1, 2, 3, 4], n_boot=100, random_state=0)
    assert ci["ci_low"] <= ci["estimate"] <= ci["ci_high"]


def test_paired_degradation_tests_runs():
    rows = []
    for s in [1, 2, 3]:
        rows.append({"dataset":"d", "subject":s, "method":"fbcca", "split":"stratified_pilot", "window_s":1.0, "channel_count":8, "accuracy":0.9})
        rows.append({"dataset":"d", "subject":s, "method":"fbcca", "split":"stratified_pilot", "window_s":1.0, "channel_count":1, "accuracy":0.6})
    out = paired_degradation_tests(pd.DataFrame(rows), compare="channel", target_channel_count=1)
    assert out.shape[0] == 1
    assert "p_value_fdr" in out.columns
