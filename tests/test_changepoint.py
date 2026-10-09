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
