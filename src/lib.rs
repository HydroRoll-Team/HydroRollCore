use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn process_rule_pack(rule_pack: &str) -> PyResult<String> {
    // 处理规则包的逻辑
    Ok(format!("Processed rule pack: {}", rule_pack))
}

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "LibCore")]
fn libcore(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(process_rule_pack, m)?)?;
    Ok(())
}