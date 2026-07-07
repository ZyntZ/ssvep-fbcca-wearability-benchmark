# SSVEP-FBCCA Wearability Benchmark

**Subtitle:** Systematic evaluation of FBCCA degradation across channels, windows, datasets, and electrode regimes for wearable SSVEP-BCI.

This repository is not “just another FBCCA implementation”. It is a reproducible benchmark scaffold for a deployment-oriented question:

> Under what combinations of channel count, decision-window length, and dataset/electrode conditions does Filter Bank Canonical Correlation Analysis (FBCCA) remain usable for SSVEP-BCI, and where does it fail?

## Why this exists

Steady-state visually evoked potential (SSVEP) brain-computer interfaces are moving from controlled lab EEG toward portable, wearable, low-channel, and dry-electrode systems. A single offline accuracy number on one clean dataset does not answer whether a classical baseline still works under wearable constraints.
