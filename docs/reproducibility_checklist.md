# Reproducibility checklist

Before publishing a result, verify:

- [ ] Dataset source, version, and access date are documented.
- [ ] Subject IDs included/excluded are listed.
- [ ] Channel names and selected channel subsets are stored.
- [ ] Sampling frequency is verified from metadata, not guessed.
- [ ] Window start/end relative to stimulus onset is documented.
- [ ] Train/test split avoids leakage across trials, sessions, or subjects.
- [ ] Filter bands and FBCCA weights are reported.
- [ ] Random seeds are fixed for split generation.
- [ ] Per-subject results are saved, not only aggregate metrics.
- [ ] Limitations are included in the report.
