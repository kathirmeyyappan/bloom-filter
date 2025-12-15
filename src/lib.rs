use pyo3::prelude::*;

/// A simple example function exposed to Python.
#[pyfunction]
fn add(a: i32, b: i32) -> i32 {
    a + b
}

/// The Python module definition.
#[pymodule]
fn kathir_bloom_filter(py: Python<'_>, m: &PyModule) -> PyResult<()> {
    pyo3::prepare_freethreaded_python();
    m.add_function(wrap_pyfunction!(add, m)?)?;
    Ok(())
}


