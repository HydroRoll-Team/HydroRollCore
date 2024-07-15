use clap::builder::Str;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn process_rule_pack(rule_pack: &str) -> PyResult<String> {
    // 处理规则包的逻辑
    Ok(format!("Processed rule pack: {}", rule_pack))
}

#[pyclass]
struct Integer {
    inner: i32,
}

// A "tuple" struct
#[pyclass]
struct Number(i32);

// PyO3 supports custom discriminants in enums
#[pyclass]
enum HttpResponse {
    Ok = 200,
    NotFound = 404,
    Teapot = 418,
    // ...
}

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyString;

#[pyclass]
#[derive(Debug, Clone)]
enum RuleLoadType {
    DIR,
    NAME,
    FILE,
    CLASS,
}

#[pymethods]
impl RuleLoadType {
    #[staticmethod]
    fn from_str(s: &str) -> PyResult<Self> {
        match s {
            "dir" => Ok(RuleLoadType::DIR),
            "name" => Ok(RuleLoadType::NAME),
            "file" => Ok(RuleLoadType::FILE),
            "class" => Ok(RuleLoadType::CLASS),
            _ => Err(PyValueError::new_err("Invalid value for RuleLoadType")),
        }
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(match self {
            RuleLoadType::DIR => "dir",
            RuleLoadType::NAME => "name",
            RuleLoadType::FILE => "file",
            RuleLoadType::CLASS => "class",
        }
        .to_string())
    }
}

#[pymodule]
#[pyo3(name = "LibCore")]
fn libcore(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(process_rule_pack, m)?)?;
    m.add_class::<RuleLoadType>()?;
    Ok(())
}
