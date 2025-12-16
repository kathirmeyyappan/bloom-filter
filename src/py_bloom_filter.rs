use crate::bloom_filter::BloomFilter as RustBloomFilter;
use pyo3::prelude::*;
use pyo3::types::PyAny;
use pyo3::Bound;

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
    ///
    /// From Python, this accepts:
    /// - strings
    /// - integers
    /// - any other hashable object (via Python's built-in `hash`)
    fn insert(&mut self, item: &Bound<'_, PyAny>) -> PyResult<()> {
        // handle py strings as is
        if let Ok(s) = item.extract::<String>() {
            self.inner.insert(&s);
            return Ok(());
        }

        // handle py integers as i64
        if let Ok(i) = item.extract::<i64>() {
            self.inner.insert(&i);
            return Ok(());
        }

        // arbitrary py objects will be hashed into ints before being passed in
        let h = item.hash()?; // isize
        self.inner.insert(&h);
        Ok(())
    }

    /// Check if an item might be in the Bloom filter.
    fn might_contain(&self, item: &Bound<'_, PyAny>) -> PyResult<bool> {
        // handle py strings as is
        if let Ok(s) = item.extract::<String>() {
            return Ok(self.inner.might_contain(&s));
        }

        // handle py integers as i64
        if let Ok(i) = item.extract::<i64>() {
            return Ok(self.inner.might_contain(&i));
        }

        // arbitrary py objects will be hashed into ints before being passed in
        let h = item.hash()?;
        Ok(self.inner.might_contain(&h))
    }

    /// Support Python's `in` operator: `item in bloom_filter`.
    fn __contains__(&self, item: &Bound<'_, PyAny>) -> PyResult<bool> {
        self.might_contain(item)
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
