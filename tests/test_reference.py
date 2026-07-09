from ssvep_fbcca.reference import make_reference_signals


def test_reference_signals_shape():
    refs = make_reference_signals([8, 10], sfreq=250, n_times=500, n_harmonics=3)
    assert set(refs.keys()) == {8.0, 10.0}
    assert refs[8.0].shape == (6, 500)
