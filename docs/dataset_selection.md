# Dataset selection plan

The MVP should use three real open SSVEP datasets spanning different acquisition conditions. Candidate sources include MOABB-supported SSVEP datasets such as Nakanishi2015, Lee2019_SSVEP, Kalunga2016, and MAMEM datasets.

Selection criteria:

1. Publicly accessible data.
2. Clear SSVEP stimulation frequencies.
3. Channel names available.
4. Enough subjects for subject-level reporting.
5. Enough trials per class to support train/test splitting.
6. Metadata on acquisition device/electrode regime when possible.

The repository must not claim wet/dry electrode comparisons unless dataset metadata explicitly support that label.

For the first reproducible release, one dataset is acceptable if results are clearly labeled as a pilot. The full wearability claim requires multiple datasets.
