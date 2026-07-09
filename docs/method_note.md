# Method note: FBCCA wearability-readiness benchmark for SSVEP-BCI

## Research question

Under what combinations of channel count, window length, and dataset/electrode conditions does FBCCA remain above a usable performance threshold for SSVEP-BCI, and where does it fail?

## Why FBCCA

Filter Bank Canonical Correlation Analysis (FBCCA) is a classical unsupervised SSVEP decoder. It compares EEG windows against sine/cosine reference signals at stimulation frequencies and harmonics across multiple frequency sub-bands.

This benchmark does not claim FBCCA is optimal. It treats FBCCA as a transparent baseline whose degradation under wearable constraints should be measured explicitly.

## Benchmark axes

- **Window length:** 1 s / 2 s / 3 s
- **Channel count:** 8 / 6 / 4 / 2 / 1
- **Dataset:** multiple open SSVEP datasets
- **Electrode regime:** wet/dry/lab/wearable when metadata are available
- **Method:** CCA vs FBCCA

## Metrics

- Mean accuracy
- Median subject accuracy
- Worst-subject accuracy
- Subject failure rate below a usable threshold, default 70%
- Usable-subject rate
- Information transfer rate, only when class count and trial timing assumptions are valid

## Statistical reporting plan

For each dataset and method, report paired per-subject comparisons across channel-count and window conditions where the same subjects are available. Avoid causal language: these are benchmark associations under dataset-specific conditions, not estimates of clinical effectiveness.

If formal comparisons are added, use paired tests or mixed-effects models with subject as a repeated factor. Correct for multiple comparisons across windows and channel counts.
