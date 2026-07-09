import numpy as np
from ssvep_fbcca.channel_ablation import select_channels_by_count


def test_select_channels_by_count_prefers_occipital():
    X = np.zeros((5, 4, 100))
    Xc, selected = select_channels_by_count(X, ['Fz', 'O2', 'Oz', 'Pz'], 2)
    assert Xc.shape == (5, 2, 100)
    assert selected == ['Oz', 'O2']
