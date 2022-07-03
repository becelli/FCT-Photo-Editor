use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

mod operations;
type Pixel = [u8; 3];
type ColorInt = u32;
#[pyfunction]
fn grayscale(image: Vec<Pixel>) -> PyResult<Vec<ColorInt>> {
    Ok(operations::grayscale(image as Vec<Pixel>))
}

#[pyfunction]
fn negative(image: Vec<Pixel>) -> PyResult<Vec<ColorInt>> {
    Ok(operations::negative(image as Vec<Pixel>))
}

#[pyfunction]
fn filter_nxn(
    image: Vec<Pixel>,
    filter: Vec<f32>,
    width: u32,
    height: u32,
) -> PyResult<Vec<ColorInt>> {
    Ok(operations::_filter_nxn(
        image as Vec<Pixel>,
        filter,
        width,
        height,
    ))
}

#[pyfunction]
fn median(image: Vec<Pixel>, distance: u32, width: u32, height: u32) -> PyResult<Vec<ColorInt>> {
    Ok(operations::median(image, distance, width, height))
}

#[pymodule]
fn libkayn(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(grayscale, m)?)?;
    m.add_function(wrap_pyfunction!(negative, m)?)?;
    m.add_function(wrap_pyfunction!(filter_nxn, m)?)?;
    m.add_function(wrap_pyfunction!(median, m)?)?;

    Ok(())
}
