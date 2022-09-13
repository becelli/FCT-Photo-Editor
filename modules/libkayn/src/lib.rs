use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

mod common;
mod operations;
mod transformations;
use common::{Hex, Image, Rgb};

#[pyfunction]
fn grayscale(image: Image) -> PyResult<Image> {
    Ok(operations::grayscale(image))
}

#[pyfunction]
fn negative(image: Image) -> PyResult<Image> {
    Ok(operations::negative(image))
}

#[pyfunction]
fn convolute(image: Image, mask: Vec<f32>) -> PyResult<Image> {
    Ok(operations::convolute(image, &mask))
}
#[pyfunction]
fn sobel(image: Image) -> PyResult<Image> {
    Ok(operations::sobel(image))
}
#[pyfunction]
fn median(image: Vec<Rgb>, distance: u32, width: u32, height: u32) -> PyResult<Vec<Hex>> {
    Ok(operations::median(image, distance, width, height))
}

#[pyfunction]
fn dynamic_compression(image: Image, constant: f32, gamma: f32) -> PyResult<Image> {
    Ok(operations::dynamic_compression(image, constant, gamma))
}

#[pyfunction]
fn normalize(image: Image) -> PyResult<Image> {
    Ok(operations::normalize(image))
}

#[pyfunction]
fn limiarize(image: Image, threshold: u8) -> PyResult<Image> {
    Ok(operations::limiarize(image, threshold))
}

#[pyfunction]
fn binarize(image: Image, threshold: u8) -> PyResult<Image> {
    Ok(operations::binarize(image, threshold))
}
#[pyfunction]
fn equalize(image: Image) -> PyResult<Image> {
    Ok(operations::equalize(image))
}
#[pyfunction]
fn gray_to_color_scale(image: Vec<Rgb>) -> PyResult<Vec<Hex>> {
    Ok(operations::gray_to_color_scale(image))
}
#[pyfunction]
fn noise_reduction_max(
    image: Vec<Rgb>,
    distance: u32,
    width: u32,
    height: u32,
) -> PyResult<Vec<Hex>> {
    Ok(operations::noise_reduction_max(
        image, distance, width, height,
    ))
}
#[pyfunction]
fn noise_reduction_min(
    image: Vec<Rgb>,
    distance: u32,
    width: u32,
    height: u32,
) -> PyResult<Vec<Hex>> {
    Ok(operations::noise_reduction_min(
        image, distance, width, height,
    ))
}
#[pyfunction]
fn noise_reduction_midpoint(
    image: Vec<Rgb>,
    distance: u32,
    width: u32,
    height: u32,
) -> PyResult<Vec<Hex>> {
    Ok(operations::noise_reduction_midpoint(
        image, distance, width, height,
    ))
}
#[pyfunction]
fn otsu_threshold(image: Vec<Rgb>, width: u32, height: u32) -> PyResult<u8> {
    Ok(operations::otsu_thresholding(image, width, height))
}

#[pyfunction]
fn dct(image: Vec<Rgb>, width: u32, height: u32) -> PyResult<(Vec<Hex>, Vec<f32>)> {
    Ok(transformations::dct_multithread(image, width, height))
}

#[pyfunction]
fn idct(coefficients: Vec<f32>, width: u32, height: u32) -> PyResult<Vec<Hex>> {
    Ok(transformations::idct_multithread(
        coefficients,
        width,
        height,
    ))
}

#[pyfunction]
fn resize_nn(
    image: Vec<Rgb>,
    width: u32,
    height: u32,
    new_width: u32,
    new_height: u32,
) -> PyResult<Vec<Hex>> {
    Ok(transformations::resize_nearest_neighbor(
        image, width, height, new_width, new_height,
    ))
}
#[pyfunction]
fn freq_lowpass(
    image: Vec<f32>,
    width: u32,
    height: u32,
    radius: u32,
) -> PyResult<(Vec<Hex>, Vec<f32>)> {
    Ok(transformations::freq_lowpass(image, width, height, radius))
}
#[pyfunction]
fn freq_highpass(
    image: Vec<f32>,
    width: u32,
    height: u32,
    radius: u32,
) -> PyResult<(Vec<Hex>, Vec<f32>)> {
    Ok(transformations::freq_highpass(image, width, height, radius))
}
#[pyfunction]
fn freq_normalize(image: Vec<f32>) -> PyResult<Vec<Hex>> {
    Ok(transformations::freq_normalize(&image))
}

#[pyfunction]
fn equalize_hsl(image: Vec<Rgb>) -> PyResult<Vec<Hex>> {
    Ok(operations::equalize_hsl(image))
}
#[pyfunction]
fn split_color_channel(image: Vec<Rgb>, channel: usize) -> PyResult<Vec<Hex>> {
    Ok(operations::split_color_channel(image, channel))
}

#[pyfunction]
fn erosion(image: Vec<Rgb>, width: u32, height: u32) -> PyResult<Vec<Hex>> {
    Ok(operations::erosion(image, width as i32, height as i32))
}

#[pyfunction]
fn dilation(image: Vec<Rgb>, width: u32, height: u32) -> PyResult<Vec<Hex>> {
    Ok(operations::dilation(image, width as i32, height as i32))
}

#[pyfunction]
fn zhang_suen_thinning(image: Vec<Rgb>, width: u32, height: u32) -> PyResult<Vec<Hex>> {
    Ok(operations::zhang_suen_thinning(
        image,
        width as u32,
        height as u32,
    ))
}

#[pymodule]
fn libkayn(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(grayscale, m)?)?;
    m.add_function(wrap_pyfunction!(negative, m)?)?;
    m.add_function(wrap_pyfunction!(convolute, m)?)?;
    m.add_function(wrap_pyfunction!(sobel, m)?)?;
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
    m.add_function(wrap_pyfunction!(otsu_threshold, m)?)?;
    m.add_function(wrap_pyfunction!(dct, m)?)?;
    m.add_function(wrap_pyfunction!(idct, m)?)?;
    m.add_function(wrap_pyfunction!(resize_nn, m)?)?;
    m.add_function(wrap_pyfunction!(freq_lowpass, m)?)?;
    m.add_function(wrap_pyfunction!(freq_highpass, m)?)?;
    m.add_function(wrap_pyfunction!(freq_normalize, m)?)?;
    m.add_function(wrap_pyfunction!(equalize_hsl, m)?)?;
    m.add_function(wrap_pyfunction!(split_color_channel, m)?)?;
    m.add_function(wrap_pyfunction!(erosion, m)?)?;
    m.add_function(wrap_pyfunction!(dilation, m)?)?;
    m.add_function(wrap_pyfunction!(zhang_suen_thinning, m)?)?;
    Ok(())
}
