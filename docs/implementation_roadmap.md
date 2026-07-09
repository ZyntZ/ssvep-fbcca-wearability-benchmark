# Implementation roadmap

## v0.1: working code scaffold

- [x] CCA classifier
- [x] FBCCA classifier
- [x] channel-count ablation utility
- [x] window cropping utility
- [x] deployment-oriented metrics
- [x] CLI benchmark script
- [x] plots for channel/window summaries
- [x] tests for core functions

## v0.2: first real dataset run

- [ ] Install MOABB/MNE optional dependencies
- [ ] Choose one SSVEP dataset with verified metadata
- [ ] Replace provisional loader parameters with dataset-specific `sfreq`, channel names, and event timing
- [ ] Run CCA vs FBCCA for 8/6/4/2/1 channels and 1/2/3 s windows
- [ ] Save per-subject and summary tables
- [ ] Write a short pilot report

## v0.3: full wearability MVP

- [ ] Add three datasets spanning easier and harder acquisition conditions
- [ ] Add electrode-regime metadata only where documented by the dataset source
- [ ] Add per-dataset plots, not only pooled plots
- [ ] Add paired statistical comparison plan for CCA vs FBCCA and channel/window degradation
- [ ] Add reproducibility checklist to every generated report

## v1.0: citable release

- [ ] Freeze environment
- [ ] Add exact dataset versions/access dates
- [ ] Add Zenodo release DOI
- [ ] Publish `docs/wearability_readiness_report.md`
