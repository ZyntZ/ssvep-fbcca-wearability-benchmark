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
