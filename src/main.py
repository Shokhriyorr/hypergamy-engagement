"""Reproducible engagement-analysis pipeline for the sample and research dataset."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analyze import kruskal_by_platform, pairwise_tests, permutation_test_short_vs_long
from src.metrics import REQUIRED_COLUMNS, add_metrics


def resolve_path(value, base=ROOT):
    """Resolve relative paths from the repository root, not the caller's cwd."""
    path = Path(value)
    return path if path.is_absolute() else base / path


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        raise ValueError("Configuration must be a YAML mapping")
    return cfg


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the engagement analysis pipeline")
    parser.add_argument("--config", default="config.yaml", help="Path to YAML config (default: config.yaml)")
    args = parser.parse_args(argv)

    config_path = resolve_path(args.config, Path.cwd())
    if not config_path.exists():
        config_path = resolve_path(args.config)
    cfg = load_config(config_path)
    seed = int(cfg["experiment"]["seed"])
    out_dir = resolve_path(cfg["data"]["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    input_path = resolve_path(cfg["data"]["input_path"])
    if not input_path.exists():
        raise FileNotFoundError(f"Input dataset not found: {input_path}")
    df = pd.read_csv(input_path)
    n_loaded = len(df)
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    if df.empty:
        raise ValueError("Input dataset contains no rows")

    complete_rate = float(df[REQUIRED_COLUMNS].notna().all(axis=1).mean())
    duplicate_count = int(df.duplicated(subset="video_id").sum())
    df = df.drop_duplicates(subset="video_id", keep="first").copy()
    for col in ("views", "likes", "comments"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    valid_counts = df[["views", "likes", "comments"]].notna().all(axis=1)
    nonnegative_counts = (df[["views", "likes", "comments"]] >= 0).all(axis=1)
    valid_rows = valid_counts & nonnegative_counts & (df["views"] > 0)
    invalid_metric_rows = int((~valid_rows).sum())
    df = df.loc[valid_rows].copy()
    df = df[df["views"] >= int(cfg["data"]["min_views"])].copy()
    if df.empty:
        raise ValueError("No valid rows remain after data validation and min_views filtering")

    df = add_metrics(df)
    df = df[df["log_er"].notna()].copy()
    if df.empty:
        raise ValueError("No rows have a positive engagement rate; log-ER cannot be analyzed")

    platforms_cfg = cfg["platforms"]
    present = set(df["platform"].dropna().astype(str))
    short_present = present.intersection(platforms_cfg["short_form"])
    long_present = present.intersection(platforms_cfg["long_form"])
    if not short_present or not long_present:
        raise ValueError("Dataset must contain at least one configured short-form and one long-form platform")

    summary = df.groupby("platform")["er"].agg(["count", "median", "mean"]).round(6).to_dict("index")
    max_error_rate = float(cfg.get("collection", {}).get("max_error_rate", 0.05))
    min_complete_rate = float(cfg.get("guardrails", {}).get("min_complete_rate", 0.95))
    guardrails = {
        "complete_rate": complete_rate,
        "min_complete_rate": min_complete_rate,
        "complete_rate_ok": complete_rate >= min_complete_rate,
        "duplicate_video_ids_removed": duplicate_count,
        "duplicate_guardrail_ok": duplicate_count == 0,
        "invalid_metric_rows_removed": invalid_metric_rows,
        "valid_metrics_guardrail_ok": invalid_metric_rows == 0,
        "collection_api_error_rate": None,
        "collection_api_error_rate_note": "Not measured by this offline analysis script; record it during API collection.",
        "collection_max_error_rate": max_error_rate,
        "annotator_agreement_cohens_kappa": None,
        "annotator_agreement_note": "Not measured by this quantitative pipeline; calculate from the coded content-analysis sample.",
    }
    results = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dataset": str(input_path.relative_to(ROOT)) if input_path.is_relative_to(ROOT) else str(input_path),
        "seed": seed,
        "n_loaded": n_loaded,
        "n_analyzed": int(len(df)),
        "guardrails": guardrails,
        "er_definition": "(likes + comments) / views",
        "er_summary_by_platform": summary,
        "kruskal_wallis": kruskal_by_platform(df),
        "pairwise": pairwise_tests(df),
        "permutation_short_vs_long": permutation_test_short_vs_long(
            df, platforms_cfg["short_form"], platforms_cfg["long_form"],
            int(cfg["experiment"]["n_permutations"]), seed,
        ),
    }
    alpha = float(cfg["experiment"]["alpha"])
    p_perm = results["permutation_short_vs_long"]["p_value_one_sided"]
    results["alpha"] = alpha
    results["decision_H0"] = "reject" if p_perm < alpha else "fail to reject"
    results["interpretation_note"] = "Synthetic sample data validates code only; do not interpret its p-values as evidence about real-world content."

    (out_dir / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    pm = results["permutation_short_vs_long"]
    kw = results["kruskal_wallis"]
    with (out_dir / "run_log.txt").open("w", encoding="utf-8") as f:
        f.write("=== Hypergamy engagement pipeline ===\n")
        f.write(f"Time (UTC): {results['timestamp_utc']}\n")
        f.write(f"Dataset: {results['dataset']}\n")
        f.write(f"Rows loaded / analyzed: {n_loaded} / {len(df)}\n")
        f.write(f"Complete-case rate: {complete_rate:.3f} (minimum {min_complete_rate:.3f}) -> {'OK' if guardrails['complete_rate_ok'] else 'FAIL'}\n")
        f.write(f"Duplicate video IDs removed: {duplicate_count}\n")
        f.write(f"Invalid metric rows removed: {invalid_metric_rows}\n")
        f.write("API error rate: NOT MEASURED (offline pipeline)\n")
        f.write("Cohen's kappa: NOT MEASURED (requires independently coded annotations)\n")
        f.write(f"Kruskal-Wallis: H={kw['H']:.4f}, p={kw['p_value']:.4f}\n")
        for row in results["pairwise"]:
            f.write(f"  {row['pair']}: p_holm={row['p_holm']:.4f}, Cliff's delta={row['cliffs_delta']:.3f}\n")
        f.write(f"Permutation test (short > long): median delta log-ER={pm['median_diff_log_er']:.4f}, p={pm['p_value_one_sided']:.4f}\n")
        f.write(f"Decision at alpha={alpha}: {results['decision_H0']}\n")
        f.write("WARNING: bundled data are synthetic; this run validates the pipeline only.\n")
    print(f"Done. Analyzed {len(df)} rows. See {out_dir / 'run_log.txt'} and {out_dir / 'results.json'}")
    return results


if __name__ == "__main__":
    main()
