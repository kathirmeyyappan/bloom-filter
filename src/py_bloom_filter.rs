use crate::bloom_filter::BloomFilter as RustBloomFilter;
use pyo3::prelude::*;

/// Python-exposed BloomFilter class.
#[pyclass]
pub struct BloomFilter {
    inner: RustBloomFilter,
    #[pyo3(get)]
    capacity: usize,
    #[pyo3(get)]
    false_positive_rate: f64,
}

#[pymethods]
impl BloomFilter {
    /// Create a new Bloom filter.
    ///
    /// # Arguments
    /// * `capacity` - Expected number of elements
    /// * `false_positive_rate` - Desired false positive probability (e.g., 0.01 for 1%)
    #[new]
    fn new(capacity: usize, false_positive_rate: f64) -> Self {
        Self {
            inner: RustBloomFilter::new(capacity, false_positive_rate),
            capacity,
            false_positive_rate,
        }
    }

    /// Add an item to the Bloom filter.
    fn insert(&mut self, item: String) {
        // TODO: make it so it's not just string
        self.inner.insert(&item)
    }

    /// Check if an item might be in the Bloom filter.
    fn might_contain(&self, item: String) -> bool {
        // TODO: make it so it's not just string
        self.inner.might_contain(&item)
    }

    /// Get the number of bits in the filter.
    #[getter]
    fn bit_count(&self) -> usize {
        self.inner.bit_count()
    }

    /// Get the number of hash functions used.
    #[getter]
    fn hash_count(&self) -> usize {
        self.inner.num_hashes
    }
}
