# Cross-Platform Engagement Analysis of Hypergamy Discourse (2026)

**Authors:** Tazhimuratov Shokhriyor; Yertis  
**Repository:** https://github.com/Shokhriyorr/hypergamy-engagement  
**License:** MIT

## Overview

This repository contains a reproducible quantitative pilot pipeline for comparing engagement rates of English-language videos discussing hypergamy across TikTok, Instagram Reels, and YouTube long-form. The planned observation period is 1 January–30 September 2026.

The current code implements quantitative analysis. Qualitative content coding, inter-rater reliability, a neutral-topic comparison, and covariate-adjusted regression are planned extensions and are not implemented in this pipeline.

**Research Question (RQ2):** Is median log engagement rate higher for short-form videos (TikTok and Instagram Reels) than for YouTube long-form videos?

Let \(\Delta = \operatorname{Med}(\log ER_{short}) - \operatorname{Med}(\log ER_{long})\).

- **H0:** \(\Delta \leq 0\).
- **H1:** \(\Delta > 0\).
- **Primary test:** one-sided permutation test of the difference in medians, α = 0.05, 5,000 permutations, seed = 42.
- **Engagement rate:** \(ER = (likes + comments) / views\). Shares are excluded to keep the numerator comparable across platforms.

The design is observational and supports conclusions about association, not causation. The bundled nine-row dataset is synthetic and validates the pipeline only; its p-values are not evidence about real-world content.

## Benchmarks and implementation status

| ID | Benchmark | Status |
|---|---|---|
| B1 | Pipeline smoke test on synthetic sample | Implemented; writes `results/run_log.txt` and `results/results.json` |
| B2 | Compare engagement across TikTok, Reels, and YouTube | Implemented; Kruskal–Wallis and Holm-adjusted pairwise Mann–Whitney tests |
| B3 | Compare short-form with YouTube long-form | Implemented; one-sided permutation test, median difference, and Cliff's δ |
| B4 | Compare with a neutral-topic sample | Planned; dataset and analysis are not included |
| B5 | Covariate-adjusted model (followers, duration, video age) | Planned; regression is not implemented |
| B6 | Qualitative content coding and Cohen's κ | Planned; coding protocol and reliability analysis are not included |

## Repository structure

```text
hypergamy-engagement/
├── README.md
├── LICENSE
├── .gitignore
├── Dockerfile
├── requirements.txt
├── config.yaml
├── data/sample/sample.csv
├── src/
│   ├── main.py
│   ├── metrics.py
│   └── analyze.py
├── tests/test_metrics.py
├── docs/methodology_card.md
└── results/                 # generated outputs; not committed
```

## System requirements

- Docker 24+ (recommended), or Python 3.11 with pip.
- Internet is not required to run the bundled synthetic sample after dependencies are installed.
- Approximately 500 MB of free disk space; no GPU required.

## Quickstart (Docker)

Run these commands from the terminal:

```bash
git clone https://github.com/Shokhriyorr/hypergamy-engagement.git
cd hypergamy-engagement
docker build -t hypergamy-engagement . && docker run --rm -v "$(pwd)/results:/app/results" hypergamy-engagement
```

The container runs the bundled sample and writes `results/run_log.txt` and `results/results.json`. The build and run are joined in the third command; if you prefer to diagnose them separately, run `docker build -t hypergamy-engagement .` and then `docker run --rm -v "$(pwd)/results:/app/results" hypergamy-engagement`.

### Run without Docker

From the repository root:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python src/main.py --config config.yaml
python -m pytest -q
```

Input and output paths in `config.yaml` are resolved relative to the repository root.

## Configuration

Edit `config.yaml` to change the input file, output directory, minimum views, platform groups, α, random seed, and number of permutations. Hashtags in the configuration are collection/search criteria; the current analysis does not estimate a hashtag effect. Do not place API credentials in the config file. If data collection is added, use environment variables or a local `.env` file and never commit secrets.

## Data collection, quality checks, and ethics

The included data are synthetic. The offline pipeline checks completeness of required fields, removes duplicate `video_id` values, and excludes invalid engagement-count rows. API error rate cannot be measured from the bundled offline dataset and must be recorded during data collection. Cohen's κ requires independently coded annotations and is not calculated by the current quantitative pipeline.

Any future real-data collection must use platform APIs or other sources permitted by their terms and applicable research ethics requirements. Document collection dates, API error rates, sampling rules, exclusions, anonymization, and rate-limit compliance. Do not collect or publish private personal information.

## Citation

If you use or adapt this repository, cite it as:

> Tazhimuratov, S., & Yertis. (2026). *Cross-Platform Engagement Analysis of Hypergamy Discourse (2026).* GitHub. https://github.com/Shokhriyorr/hypergamy-engagement

## License

Released under the MIT License. See `LICENSE`.
