import pandas as pd
import pytest
from ssvep_fbcca.metrics import accuracy, information_transfer_rate, summarize_subject_metrics


def test_accuracy():
    assert accuracy([0, 1, 1], [0, 0, 1]) == pytest.approx(2/3)


def test_itr_bounds():
    assert information_transfer_rate(4, 1.0, 1.0) > 0
    assert information_transfer_rate(4, 0.25, 1.0) >= 0


def test_summarize_subject_metrics():
    df = pd.DataFrame({
        'dataset': ['d','d','d'],
        'method': ['fbcca','fbcca','fbcca'],
        'window_s': [1,1,1],
        'channel_count': [2,2,2],
        'subject': [1,2,3],
        'accuracy': [0.8,0.6,0.9],
    })
    out = summarize_subject_metrics(df, usable_threshold=0.7)
    assert out.loc[0, 'n_subjects'] == 3
    assert out.loc[0, 'subject_failure_rate'] == pytest.approx(1/3)
