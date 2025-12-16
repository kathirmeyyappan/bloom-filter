from typing import Hashable


class BloomFilter:
    """Probabilistic set membership structure implemented as a Bloom filter."""

    capacity: int
    """Expected maximum number of distinct items the filter is sized for."""

    false_positive_rate: float
    """Target false positive probability used when sizing the filter (e.g. 0.01 for 1%)."""

    bit_count: int
    """Total number of bits allocated in the underlying bit array."""

    hash_count: int
    """Number of hash functions used per item when setting / checking bits."""
    
    def __init__(self, capacity: int, false_positive_rate: float) -> None:
        """Create a Bloom filter for up to `capacity` items and a desired false positive rate."""
        ...

    def insert(self, item: str | int | Hashable) -> None:
        """Insert an item into the filter; item must be hashable if not a str or int."""
        ...

    def might_contain(self, item: str | int | Hashable) -> bool:
        """Return True if the item might be in the set, False if it is definitely not."""
        ...

    def __contains__(self, item: str | int | Hashable) -> bool:
        """Alias for might_contain; enables use of `item in bloom_filter`. NOTE: still has false positive rate."""
        ...

