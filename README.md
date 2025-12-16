# kathir-bloom-filter

A super simple and fast Bloom filter implementation in Rust with Python bindings.

## Installation

```bash
pip install kathir-bloom-filter
```

## Usage

```python
from kathir_bloom_filter import BloomFilter

# Create a Bloom filter for ~1 million items with 1% false positive rate
bf = BloomFilter(capacity=1_000_000, false_positive_rate=0.01)

# Insert items (strings, ints, or any hashable type)
bf.insert("hello")
bf.insert(42)

# Check membership
"hello" in bf  # True
"world" in bf  # False (might incorrectly report True with probability = false_positive_rate)
```

## Performance

Benchmarked against other Python Bloom filter libraries on 1M random item insertions and queries with various item types and patterns (see https://github.com/kathirmeyyappan/bloom-filter-bench). 

Overall, we can see that for the simple cases, this bloom filter performs MUCH better than "standard" Python implementations and marginally better than some other libraries.

<img width="1390" height="589" alt="image" src="https://github.com/user-attachments/assets/c62f395d-9328-4adf-bb5a-e97790df675d" />


