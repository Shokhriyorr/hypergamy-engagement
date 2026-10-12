"""Comparable engagement metrics across platforms.

ER = (likes + comments) / views. Shares are excluded because a comparable
public share count is not available for all platforms in this study.
"""
import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ["video_id", "platform", "views", "likes", "comments"]


def engagement_rate(likes, comments, views):
    """Return ER; values with non-positive views produce NaN."""
    likes = np.asarray(likes, dtype=float)
    comments = np.asarray(comments, dtype=float)
    views = np.asarray(views, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(views > 0, (likes + comments) / views, np.nan)


def add_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with ER and natural-log ER; zero ER has undefined log-ER."""
    out = df.copy()
    out["er"] = engagement_rate(out["likes"], out["comments"], out["views"])
    out["log_er"] = np.log(out["er"].where(out["er"] > 0))
    return out
