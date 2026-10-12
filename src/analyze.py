"""Statistical tests and effect sizes for engagement-rate comparisons."""
import itertools
import numpy as np
from scipy import stats


def cliffs_delta(x, y) -> float:
    """Cliff's delta: P(x > y) - P(x < y)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size == 0 or y.size == 0:
        raise ValueError("Cliff's delta requires non-empty groups")
    diff = x[:, None] - y[None, :]
    return float(np.sign(diff).sum() / (len(x) * len(y)))


def holm_correction(pvals):
    """Holm-Bonferroni adjusted p-values in original input order."""
    p = np.asarray(pvals, dtype=float)
    if p.size == 0:
        return []
    if np.any(~np.isfinite(p)) or np.any((p < 0) | (p > 1)):
        raise ValueError("p-values must be finite and in [0, 1]")
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p[idx])
        adj[idx] = min(1.0, running)
    return adj.tolist()


def _groups(df, value_col):
    groups = {str(k): g[value_col].dropna().to_numpy(dtype=float) for k, g in df.groupby("platform")}
    groups = {k: v for k, v in groups.items() if len(v) > 0}
    return groups


def kruskal_by_platform(df, value_col="log_er"):
    groups = _groups(df, value_col)
    if len(groups) < 2:
        raise ValueError("Kruskal-Wallis requires at least two non-empty platform groups")
    h, p = stats.kruskal(*groups.values())
    return {"H": float(h), "p_value": float(p), "n_per_group": {k: int(len(v)) for k, v in groups.items()}}


def pairwise_tests(df, value_col="log_er"):
    groups = _groups(df, value_col)
    if len(groups) < 2:
        raise ValueError("Pairwise tests require at least two non-empty platform groups")
    pairs = list(itertools.combinations(sorted(groups), 2))
    raw = []
    for a, b in pairs:
        _, p = stats.mannwhitneyu(groups[a], groups[b], alternative="two-sided", method="auto")
        raw.append(float(p))
    adjusted = holm_correction(raw)
    return [{"pair": f"{a} vs {b}", "p_raw": raw[i], "p_holm": adjusted[i],
             "cliffs_delta": cliffs_delta(groups[a], groups[b])}
            for i, (a, b) in enumerate(pairs)]


def permutation_test_short_vs_long(df, short, long_, n_perm, seed, value_col="log_er"):
    """One-sided pooled permutation test using median(short) - median(long).

    The pooled permutation null assumes exchangeability/equal distributions;
    it is not an exact test of the composite null that the median difference
    is non-positive under arbitrary differences in distribution shape/spread.
    """
    if n_perm < 1:
        raise ValueError("n_perm must be at least 1")
    s = df[df["platform"].isin(short)][value_col].dropna().to_numpy(dtype=float)
    l = df[df["platform"].isin(long_)][value_col].dropna().to_numpy(dtype=float)
    if s.size == 0 or l.size == 0:
        raise ValueError("Permutation test requires non-empty short-form and long-form groups")
    observed = float(np.median(s) - np.median(l))
    pooled = np.concatenate([s, l])
    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(n_perm):
        permuted = rng.permutation(pooled)
        statistic = np.median(permuted[:len(s)]) - np.median(permuted[len(s):])
        if statistic >= observed:
            count += 1
    return {"median_diff_log_er": observed, "p_value_one_sided": float((count + 1) / (n_perm + 1)),
            "cliffs_delta_short_vs_long": cliffs_delta(s, l), "n_short": int(s.size), "n_long": int(l.size)}
