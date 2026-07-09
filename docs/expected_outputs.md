# Expected outputs

## `per_subject_results.csv` / `per_subject_degradation.csv`

- dataset
- subject
- method
- split
- window_s
- channel_count
- channel_policy
- subset_id
- channels
- n_train
- n_test
- accuracy
- itr_bits_min
- baseline_accuracy
- accuracy_drop_from_baseline
- relative_accuracy_drop
- itr_drop_from_baseline
- usable_status_changed
- electrode_type

## `condition_summary.csv`

- dataset
- method
- split
- window_s
- channel_count
- channel_policy
- n_subjects
- mean_accuracy
- median_accuracy
- worst_subject_accuracy
- subject_failure_rate
- usable_subject_rate
- wearability_condition_label

## `statistical_tests.csv`

- dataset
- split
- comparison
- test
- n_subjects
- mean_accuracy_drop
- median_accuracy_drop
- statistic
- p_value
- p_value_fdr
- ci_low
- ci_high

P-values are secondary. The primary results are degradation effect sizes and confidence intervals.
