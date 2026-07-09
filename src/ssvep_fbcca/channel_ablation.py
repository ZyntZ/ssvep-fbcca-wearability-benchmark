import itertools
import numpy as np

DEFAULT_OCCIPITAL_ORDER = [
    "Oz", "O1", "O2", "POz", "PO3", "PO4", "PO7", "PO8", "Pz", "P3", "P4"
]


def select_channels_by_count(X, channel_names, count: int, preferred_order=None):
    """Backward-compatible occipital-first channel selector."""
    X = np.asarray(X)
    selected = make_channel_subsets(
        channel_names=channel_names,
        count=count,
        policy="occipital_first",
        preferred_order=preferred_order,
        n_random=1,
        random_state=0,
    )[0]
    indices = [list(channel_names).index(ch) for ch in selected]
    return X[:, indices, :], selected


def make_channel_subsets(
    channel_names,
    count: int,
    policy: str = "occipital_first",
    preferred_order=None,
    n_random: int = 20,
    random_state: int = 42,
    max_combinations: int = 200,
):
    """Create channel subsets for channel-count degradation and sensitivity analyses.

    Policies: occipital_first, random_subsets, all_combinations_if_small.
    """
    channel_names = list(channel_names)
    if count <= 0 or count > len(channel_names):
        raise ValueError("count must be between 1 and number of available channels.")
    if preferred_order is None:
        preferred_order = DEFAULT_OCCIPITAL_ORDER
    policy = policy.lower()

    if policy == "occipital_first":
        selected = [ch for ch in preferred_order if ch in channel_names]
        selected += [ch for ch in channel_names if ch not in selected]
        return [selected[:count]]

    if policy == "all_combinations_if_small":
        combos = list(itertools.combinations(channel_names, count))
        if len(combos) <= max_combinations:
            return [list(c) for c in combos]
        policy = "random_subsets"

    if policy == "random_subsets":
        rng = np.random.default_rng(random_state)
        seen = set()
        subsets = []
        attempts = 0
        max_attempts = max(100, n_random * 20)
        while len(subsets) < n_random and attempts < max_attempts:
            attempts += 1
            choice = tuple(sorted(rng.choice(channel_names, size=count, replace=False).tolist()))
            if choice not in seen:
                seen.add(choice)
                subsets.append(list(choice))
        if not subsets:
            raise RuntimeError("Could not generate random channel subsets.")
        return subsets

    raise ValueError(
        "Unknown channel policy. Use occipital_first, random_subsets, or all_combinations_if_small."
    )


def apply_channel_subset(X, channel_names, selected):
    X = np.asarray(X)
    channel_names = list(channel_names)
    indices = [channel_names.index(ch) for ch in selected]
    return X[:, indices, :]
