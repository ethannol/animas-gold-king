"""Exploratory calendar-block pairs resampling, preserving original timestamps."""
import numpy as np
import pandas as pd


def calendar_block_sample(df, release, block_months, rng):
    """Resample occupied calendar blocks separately before/after release.

    All rows within a block travel together, including concentration/limit,
    censoring flag and discharge. Dates are not shifted: the model refits the
    original trend/season design. This is a pairs sensitivity, not a causal CI.
    """
    if block_months < 1:
        raise ValueError("block_months must be positive")
    pieces = []
    for pre in [True, False]:
        group = df.loc[(df.date < release) == pre]
        month = group.date.dt.year * 12 + group.date.dt.month
        blocks = ((month - month.min()) // block_months).to_numpy()
        ids = np.unique(blocks)
        if not len(ids):
            raise ValueError("both periods need observed blocks")
        for chosen in rng.choice(ids, len(ids), replace=True):
            pieces.append(group.iloc[np.flatnonzero(blocks == chosen)])
    return pd.concat(pieces, ignore_index=True).sort_values("date").reset_index(drop=True)
