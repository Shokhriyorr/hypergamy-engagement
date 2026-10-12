import numpy as np
import pandas as pd
import pytest
from pathlib import Path

from src.analyze import cliffs_delta, holm_correction, permutation_test_short_vs_long
from src.main import main
from src.metrics import add_metrics, engagement_rate


def test_engagement_rate_basic():
    assert engagement_rate(80, 20, 1000) == 0.1


def test_engagement_rate_zero_views_is_nan():
    assert np.isnan(engagement_rate(5, 1, 0))


def test_add_metrics_columns():
    out = add_metrics(pd.DataFrame({"likes": [10], "comments": [5], "views": [1000]}))
    assert abs(out["er"].iloc[0] - 0.015) < 1e-12
    assert np.isfinite(out["log_er"].iloc[0])


def test_cliffs_delta_extremes():
    assert cliffs_delta([3, 4], [1, 2]) == 1.0
    assert cliffs_delta([1, 2], [3, 4]) == -1.0


def test_holm_monotone_and_bounded():
    adj = holm_correction([0.01, 0.04, 0.03])
    assert all(0 <= a <= 1 for a in adj)
    assert adj[0] == 0.03


def test_holm_empty_input():
    assert holm_correction([]) == []


def test_permutation_is_reproducible():
    df = pd.DataFrame({"platform": ["TikTok", "TikTok", "YouTube", "YouTube"],
                       "log_er": [-2.0, -1.5, -3.0, -2.8]})
    a = permutation_test_short_vs_long(df, ["TikTok"], ["YouTube"], 100, 42)
    b = permutation_test_short_vs_long(df, ["TikTok"], ["YouTube"], 100, 42)
    assert a == b
    assert a["n_short"] == 2 and a["n_long"] == 2


def test_permutation_rejects_empty_group():
    df = pd.DataFrame({"platform": ["TikTok"], "log_er": [-2.0]})
    with pytest.raises(ValueError, match="non-empty"):
        permutation_test_short_vs_long(df, ["TikTok"], ["YouTube"], 100, 42)


def test_full_pipeline_writes_outputs():
    result = main(["--config", "config.yaml"])
    assert result["n_loaded"] == 9
    assert result["n_analyzed"] > 0
    assert result["guardrails"]["complete_rate_ok"] is True
    assert result["guardrails"]["collection_api_error_rate"] is None
    assert (Path("results") / "results.json").exists()
    assert (Path("results") / "run_log.txt").exists()
