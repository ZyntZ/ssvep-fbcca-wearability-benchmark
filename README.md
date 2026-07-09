# SSVEP-FBCCA Wearability Benchmark

**Subtitle:** Systematic evaluation of FBCCA degradation across channels, windows, datasets, and electrode regimes for wearable SSVEP-BCI.

This repository is not “just another FBCCA implementation”. It is a reproducible benchmark scaffold for a deployment-oriented question:

> Under what combinations of channel count, decision-window length, and dataset/electrode conditions does Filter Bank Canonical Correlation Analysis (FBCCA) remain usable for SSVEP-BCI, and where does it fail?

## Why this exists

Steady-state visually evoked potential (SSVEP) brain-computer interfaces are moving from controlled lab EEG toward portable, wearable, low-channel, and dry-electrode systems. A single offline accuracy number on one clean dataset does not answer whether a classical baseline still works under wearable constraints.

The benchmark maps FBCCA degradation across:

- **channel count:** 8 / 6 / 4 / 2 / 1 channels
- **window length:** 1 s / 2 s / 3 s decision windows
- **dataset:** multiple open SSVEP datasets
- **electrode regime:** wet/dry or lab/wearable metadata, when available
- **subject tail risk:** not only mean accuracy, but worst-subject accuracy and subject failure rate

## Current status

This is an implementation scaffold. It includes:

- clean CCA and FBCCA implementations;
- channel-ablation utilities;
- window-sweep evaluation utilities;
- deployment-oriented metrics;
- reproducible command-line scripts;
- documentation templates;
- unit tests.

It does **not** include benchmark results yet. Results must be generated from real open SSVEP datasets. No synthetic benchmark claims are made.

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/ssvep-fbcca-wearability-benchmark.git
cd ssvep-fbcca-wearability-benchmark
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
```

For MOABB datasets:

```bash
pip install -e .[moabb]
```

## Minimal API example

```python
from ssvep_fbcca import CCAClassifier, FBCCAClassifier

freqs = [8, 10, 12, 15]
clf = FBCCAClassifier(
    sfreq=250,
    freqs=freqs,
    n_harmonics=3,
    filterbank=[(6, 14), (14, 22), (22, 30), (30, 38)],
)

clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
scores = clf.predict_scores(X_test)
```

Expected data shape is:

```text
X: (n_trials, n_channels, n_times)
y: integer labels aligned to the `freqs` list
```

## Reproduce a benchmark run

A dataset loader must return an array of epochs and labels. The default MOABB loader is implemented as a guarded optional dependency, because MOABB datasets and class names can change.

```bash
python scripts/run_wearability_benchmark.py \
  --dataset lee2019_ssvep \
  --windows 1 2 3 \
  --channel-counts 8 6 4 2 1 \
  --methods cca fbcca \
  --out results/demo_run
```

Outputs:

```text
results/demo_run/per_subject_results.csv
results/demo_run/window_channel_summary.csv
results/demo_run/channel_window_heatmap.png
results/demo_run/channel_degradation_curve.png
results/demo_run/wearability_readiness_report.md
```

## Metrics

The benchmark reports:

- mean accuracy;
- median subject accuracy;
- worst-subject accuracy;
- subject failure rate below a configurable usable threshold, default 70%;
- usable-subject rate;
- information transfer rate, when class count and trial timing assumptions are valid;
- per-subject degradation relative to full-channel / longest-window condition.

## Scientific scope

This project does not claim a new algorithm or state-of-the-art performance. It aims to provide a transparent deployment-readiness map for a standard SSVEP baseline.

See:

- `docs/method_note.md`
- `docs/limitations.md`
- `docs/reproducibility_checklist.md`
- `docs/dataset_selection.md`

## License

MIT. See `LICENSE`.


## What this benchmark will answer

1. How much accuracy is lost when reducing channels from 8 to 1?
2. Does FBCCA fail gradually or abruptly under low-channel constraints?
3. Which subjects fail first?
4. Does a longer window compensate for fewer channels?
5. Are degradation patterns consistent across datasets?

## Run from a config file

```bash
python scripts/run_wearability_benchmark.py --config configs/pilot_lee2019.yaml
```


## Current scientific warning

The repository can run as software, but scientific results require verified dataset-specific metadata: sampling frequency, channel names, stimulation frequencies, event timing, subject/session/run structure, and electrode regime. Do not report dry/wet comparisons unless the dataset source documents electrode type.
