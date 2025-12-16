class BloomFilter:
    capacity: int
    false_positive_rate: float
    bit_count: int
    hash_count: int
    
    def __init__(self, capacity: int, false_positive_rate: float) -> None: ...
    def insert(self, item: str) -> None: ...
    def might_contain(self, item: str) -> bool: ...

