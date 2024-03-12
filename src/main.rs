#![allow(unused)]
fn main() {
    use pyo3::prelude::*;

    #[pymodule]
    fn parent_module(py: Python<'_>, m: &PyModule) -> PyResult<()> {
        register_child_module(py, m)?;
        Ok(())
    }

    fn register_child_module(py: Python<'_>, parent_module: &PyModule) -> PyResult<()> {
        let child_module = PyModule::new(py, "child_module")?;
        child_module.add_function(wrap_pyfunction!(func, child_module)?)?;
        parent_module.add_submodule(child_module)?;
        Ok(())
    }

    #[pyfunction]
    fn func() -> String {
        "func".to_string()
    }

    Python::with_gil(|py| {
        use pyo3::types::IntoPyDict;
        use pyo3::wrap_pymodule;
        let parent_module = wrap_pymodule!(parent_module)(py);
        let ctx = [("parent_module", parent_module)].into_py_dict(py);

        py.run(
            "assert parent_module.child_module.func() == 'func'",
            None,
            Some(&ctx),
        )
        .unwrap();
    })
}
