# Limitations

- This repository is a benchmark scaffold and baseline implementation, not a new SSVEP algorithm.
- No clinical or medical-device claims are made.
- Results depend on dataset selection, preprocessing, stimulus timing, label definitions, and channel availability.
- Channel ablation is a proxy for wearable constraints. It does not fully reproduce dry-electrode impedance, motion artifacts, headset fit, or real-time latency.
- Electrode type comparisons are only valid when dataset metadata are reliable and preprocessing is harmonized.
- Information transfer rate is reported only under explicit assumptions about class count and trial timing. It should not be compared across studies without checking these assumptions.
- Subject-level results describe decoder behavior on specific datasets. They should not be interpreted causally.
- The default train/test split is an MVP. Final reports should use dataset-aware splits (session/run/subject-independent) when metadata permit.
