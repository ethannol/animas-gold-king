import numpy as np
import pandas as pd

from animas.uncertainty import calendar_block_sample


def test_calendar_resampling_preserves_measurement_pairs_and_periods():
    dates = pd.date_range("2009-01-01", periods=48, freq="MS")
    original = pd.DataFrame({"date": dates, "value": np.arange(48), "q": np.arange(48)+10})
    result = calendar_block_sample(original, pd.Timestamp("2011-01-01"), 12, np.random.default_rng(4))
    assert len(result) == 48
    assert (result.q - result.value == 10).all()
    assert (result.date < "2011-01-01").sum() == 24
    assert set(result.date) <= set(original.date)
