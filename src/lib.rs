// Expose the pure Rust implementations for direct Rust usage
pub mod bloom_filter;
mod py_bloom_filter;

use pyo3::prelude::*;
use py_bloom_filter::BloomFilter;

/// The Python module definition.
#[pymodule]
fn kathir_bloom_filter(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<BloomFilter>()?;
    Ok(())
}


