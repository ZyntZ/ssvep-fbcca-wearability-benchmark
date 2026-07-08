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

It does **not** include benchmark results yet. Results must be generated from real open SSVEP datasets. No synthetic benchmark claims are made.

## Installation

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
