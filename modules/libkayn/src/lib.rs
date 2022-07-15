use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

mod operations;
mod transformations;

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
    Ok(operations::filter_nxn(image, filter, width, height))
}

#[pyfunction]
fn median(image: Vec<Pixel>, distance: u32, width: u32, height: u32) -> PyResult<Vec<ColorInt>> {
    Ok(operations::median(image, distance, width, height))
}

#[pyfunction]
fn dynamic_compression(image: Vec<Pixel>, constant: f32, gamma: f32) -> PyResult<Vec<ColorInt>> {
    Ok(operations::dynamic_compression(image, constant, gamma))
}

#[pyfunction]
fn normalize(image: Vec<Pixel>) -> PyResult<Vec<ColorInt>> {
    Ok(operations::normalize(image))
}

#[pyfunction]
fn limiarize(image: Vec<Pixel>, threshold: u8) -> PyResult<Vec<ColorInt>> {
    Ok(operations::limiarize(image, threshold))
}

#[pyfunction]
fn binarize(image: Vec<Pixel>, threshold: u8) -> PyResult<Vec<ColorInt>> {
    Ok(operations::binarize(image, threshold))
}
#[pyfunction]
fn equalize(image: Vec<Pixel>) -> PyResult<Vec<ColorInt>> {
    Ok(operations::equalize(image))
}
#[pyfunction]
fn gray_to_color_scale(image: Vec<Pixel>) -> PyResult<Vec<ColorInt>> {
    Ok(operations::gray_to_color_scale(image))
}
#[pyfunction]
fn noise_reduction_max(
    image: Vec<Pixel>,
    distance: u32,
    width: u32,
    height: u32,
) -> PyResult<Vec<ColorInt>> {
    Ok(operations::noise_reduction_max(
        image, distance, width, height,
    ))
}
#[pyfunction]
fn noise_reduction_min(
    image: Vec<Pixel>,
    distance: u32,
    width: u32,
    height: u32,
) -> PyResult<Vec<ColorInt>> {
    Ok(operations::noise_reduction_min(
        image, distance, width, height,
    ))
}
#[pyfunction]
fn noise_reduction_midpoint(
    image: Vec<Pixel>,
    distance: u32,
    width: u32,
    height: u32,
) -> PyResult<Vec<ColorInt>> {
    Ok(operations::noise_reduction_midpoint(
        image, distance, width, height,
    ))
}

#[pyfunction]
fn dct(image: Vec<Pixel>, width: u32, height: u32) -> PyResult<(Vec<ColorInt>, Vec<f32>)> {
    Ok(transformations::dct(image, width, height))
}

#[pyfunction]
fn idct(
    coefficients: Vec<f32>,
    width: u32,
    height: u32,
) -> PyResult<Vec<ColorInt>> {
    Ok(transformations::idct(
        coefficients, width, height,
    ))
}

#[pymodule]
fn libkayn(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(grayscale, m)?)?;
    m.add_function(wrap_pyfunction!(negative, m)?)?;
    m.add_function(wrap_pyfunction!(filter_nxn, m)?)?;
    m.add_function(wrap_pyfunction!(median, m)?)?;
    m.add_function(wrap_pyfunction!(dynamic_compression, m)?)?;
    m.add_function(wrap_pyfunction!(normalize, m)?)?;
    m.add_function(wrap_pyfunction!(limiarize, m)?)?;
    m.add_function(wrap_pyfunction!(binarize, m)?)?;
    m.add_function(wrap_pyfunction!(equalize, m)?)?;
    m.add_function(wrap_pyfunction!(gray_to_color_scale, m)?)?;
    m.add_function(wrap_pyfunction!(noise_reduction_max, m)?)?;
    m.add_function(wrap_pyfunction!(noise_reduction_min, m)?)?;
    m.add_function(wrap_pyfunction!(noise_reduction_midpoint, m)?)?;
    m.add_function(wrap_pyfunction!(dct, m)?)?;
    m.add_function(wrap_pyfunction!(idct, m)?)?;
    Ok(())
}
