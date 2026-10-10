import numpy as np

from animas.changepoint import binary_segmentation, pelt


def test_finds_planted_step():
    rng = np.random.default_rng(6)
    x = rng.normal(scale=0.3, size=240)
    x[128:] += 1.0
    cps = pelt(x)
    assert len(cps) == 1 and abs(cps[0] - 128) <= 2
    bs = binary_segmentation(x)
    assert bs and abs(bs[0][0] - 128) <= 2


def test_white_noise_has_no_change_points():
    for seed in range(5):
        x = np.random.default_rng(seed).normal(size=240)
        assert pelt(x) == []
        assert binary_segmentation(x) == []


def test_bh_rejects_small_p_only():
    from animas.analysis import bh_reject

    p = np.array([0.001, 0.2, 0.03, np.nan, 0.5, 0.004])
    rej = bh_reject(p, q=0.05)
    assert rej.tolist() == [True, False, True, False, False, True]
    assert not bh_reject(np.array([0.2, 0.3, np.nan])).any()
