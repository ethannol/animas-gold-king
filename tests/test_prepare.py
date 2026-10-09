import numpy as np
import pandas as pd
import pytest

from animas.prepare import attach_discharge


def _samples():
    return pd.DataFrame({
        "gauge": ["G1", "G1", "G1", "G2"],
        "date": pd.to_datetime(["2015-01-01", "2015-01-01", "2015-01-03", "2015-01-01"]),
        "value": [1.0, 2.0, 3.0, 4.0],
    })


def test_join_preserves_rows_and_handles_missing_days(tmp_path, monkeypatch):
    monkeypatch.setenv("CAIRN_CHECKS", str(tmp_path / "checks.jsonl"))
    daily = pd.DataFrame({
        "gauge": ["G1", "G1", "G2"],
        "date": pd.to_datetime(["2015-01-01", "2015-01-02", "2015-01-01"]),
        "q_cfs": [10.0, 11.0, 20.0], "q_approval": "Approved", "q_qualifier": "",
    })
    out = attach_discharge(_samples(), daily)
    assert len(out) == 4
    assert out["q_cfs"].tolist()[:2] == [10.0, 10.0]
    assert np.isnan(out["q_cfs"].iloc[2]) and not out["has_q"].iloc[2]
    assert out["q_cfs"].iloc[3] == 20.0


def test_duplicate_discharge_day_is_refused(tmp_path, monkeypatch):
    monkeypatch.setenv("CAIRN_CHECKS", str(tmp_path / "checks.jsonl"))
    daily = pd.DataFrame({
        "gauge": ["G1", "G1", "G2"],
        "date": pd.to_datetime(["2015-01-01", "2015-01-01", "2015-01-01"]),
        "q_cfs": [10.0, 11.0, 20.0], "q_approval": "Approved", "q_qualifier": "",
    })
    with pytest.raises(ValueError):
        attach_discharge(_samples(), daily)
