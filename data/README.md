# Data

Do not commit raw EEG datasets to this repository.

Use one of:

1. MOABB automatic dataset download, if licenses permit.
2. Local `.npz` files with the schema documented in `ssvep_fbcca.loaders.load_npz_dataset`.
3. External data storage with scripts that reproduce the download/preprocessing.

All benchmark outputs must document dataset source, access date, subject list, and channel list.
