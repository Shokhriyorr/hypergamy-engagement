# Cross-Platform Engagement Analysis of Hypergamy Discourse (2026)

**Authors:** Tazhimuratov Shokhriyor , Yertis   
**Repository:** 
**License:** MIT
## Overview

This repository provides a reproducible pilot pipeline for comparing engagement rates of English-language videos discussing hypergamy across TikTok, Instagram Reels, and YouTube long-form, for the planned period 1 January–30 September 2026. The current code implements quantitative analysis; qualitative content coding and inter-rater reliability are planned components and are not implemented in this pipeline.

**Research Question (RQ2):** Is median log engagement rate higher for short-form videos (TikTok and Instagram Reels) than for YouTube long-form videos?

- **H0:** `Med(log-ER_short) - Med(log-ER_long) <= 0`.
- **H1:** `Med(log-ER_short) - Med(log-ER_long) > 0`.
- **Primary test:** one-sided permutation test of the difference in medians, α = 0.05, 5,000 permutations, seed = 42.
- **Engagement rate:** `ER = (likes + comments) / views`. Shares are excluded to keep the numerator comparable across platforms.

The design is observational and supports conclusions about association, not causation. The bundled nine-row dataset is synthetic and validates the pipeline only; its p-values are not evidence about real-world content.

## Planned benchmarks

| ID | Benchmark | Status / output |
|---|---|---|
| B1 | Pipeline smoke test on synthetic sample | Implemented; `results/run_log.txt`, `results/results.json` |
| B2 | Compare ER across TikTok, Reels, YouTube | Implemented; Kruskal–Wallis and Holm-adjusted pairwise tests |
| B3 | Compare short-form with YouTube long-form | Implemented; one-sided permutation test, median difference, Cliff's δ |
| B4 | Compare with a neutral-topic sample | Planned; neutral-topic dataset and analysis not included yet |
| B5 | Covariate-adjusted model (followers, duration, video age) | Planned; regression is not implemented in the current pipeline |
| B6 | Qualitative content coding and Cohen's κ | Planned; coding protocol and reliability analysis not included yet |

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
├── notebooks/
└── results/                 # generated files; not committed
```

## System requirements

- Docker 24+ (recommended), or Python 3.11 with pip.
- Internet is not required to run the bundled synthetic sample after dependencies are installed.
- Approximately 500 MB of free disk space; no GPU required.

## Quickstart

After replacing the repository URL below with the real URL, run these commands:

```bash
git clone https://github.com/<YOUR_USERNAME>/<YOUR_REPOSITORY>.git
cd <YOUR_REPOSITORY>
docker build -t hypergamy-engagement .
docker run --rm -v "$(pwd)/results:/app/results" hypergamy-engagement
```

The container runs the bundled sample and writes `results/run_log.txt` and `results/results.json`. This is four shell commands (the build and run are separate so failures are easier to diagnose).

### Run without Docker

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python src/main.py --config config.yaml
python -m pytest -q
```

Run commands from the repository root. Input and output paths in `config.yaml` are resolved relative to the repository root.

## Configuration

Edit `config.yaml` to change the input file, output directory, minimum views, platform groups, α, random seed, and number of permutations. Do not place API credentials in the config file. If data collection is added, use environment variables or a local `.env` file and never commit secrets.

## Data collection and ethics

The included data are synthetic. Any future real-data collection must use platform APIs or other sources permitted by their terms and applicable research ethics requirements. Document collection dates, API error rates, sampling rules, exclusions, anonymization, and rate-limit compliance. Do not collect or publish private personal information.

## Citation

If you use or adapt this repository, cite it as:

> Shah & Yertis. (2026). *Cross-Platform Engagement Analysis of Hypergamy Discourse (2026)* . GitHub  https://github.com/Shokhriyorr/hypergamy-engagement.

## License

Released under the MIT License. See `LICENSE`.
