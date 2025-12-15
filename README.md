# kathir-bloom-filter

Rust-based Bloom filter library with Python bindings built using **maturin** and **pyo3**.

## Development

- **Build wheel**:
  - `maturin build`
- **Develop in-place**:
  - `maturin develop`

After installation (e.g. `maturin develop`), you can use in Python:

```python
import kathir_bloom_filter

print(kathir_bloom_filter.add(1, 2))
```


