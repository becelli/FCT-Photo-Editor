use crate::common::{Rgb, Hex, rgb2hex, gray2hex};
use std::f32::consts::PI;
use std::thread;


// pub fn dct(image: Vec<Rgb>, width: u32, height: u32) -> (Vec<Hex>, Vec<f32>) {
//     let mut coeff: Vec<f32> = vec![];
//     let (mut ci, mut cj): (f32, f32);
//     for u in 0..width {
//         for v in 0..height {
//             ci = match u {
//                 0 => (1.0 / width as f32).sqrt(),
//                 _ => (2.0 / width as f32).sqrt(),
//             };
//             cj = match v {
//                 0 => (1.0 / height as f32).sqrt(),
//                 _ => (2.0 / height as f32).sqrt(),
//             };

//             let mut sum = 0.0;
//             for x in 0..width {
//                 for y in 0..height {
//                     let pixel = image[(y * width + x) as usize][0] as f32;
//                     let dctl = {
//                         pixel
//                             * ((2.0 * x as f32 + 1.0) * u as f32 * PI / (2.0 * width as f32)).cos()
//                             * ((2.0 * y as f32 + 1.0) * v as f32 * PI / (2.0 * height as f32)).cos()
//                     };
//                     sum += dctl;
//                 }
//             }
//             let value = sum * ci * cj;
//             coeff.push(value);
//         }
//     }
//     let normalized = normalize_float(&coeff);
//     (normalized, coeff)
// }

// pub fn idct(coef: Vec<f32>, width: u32, height: u32) -> Vec<Hex> {
//     let mut new_image: Vec<Hex> = vec![];
//     let (mut ci, mut cj): (f32, f32);
//     for x in 0..width {
//         for y in 0..height {
//             let mut sum = 0.0;

//             for u in 0..width {
//                 for v in 0..height {
//                     ci = match u {
//                         0 => (1.0 / width as f32).sqrt(),
//                         _ => (2.0 / width as f32).sqrt(),
//                     };
//                     cj = match v {
//                         0 => (1.0 / height as f32).sqrt(),
//                         _ => (2.0 / height as f32).sqrt(),
//                     };
//                     let dctl = {
//                         coef[(v * width + u) as usize]
//                             * ((2.0 * x as f32 + 1.0) * u as f32 * PI / (2.0 * width as f32)).cos()
//                             * ((2.0 * y as f32 + 1.0) * v as f32 * PI / (2.0 * height as f32)).cos()
//                     };
//                     sum += dctl * ci * cj;
//                 }
//             }
//             let color = rgb2hex(sum as u8, sum as u8, sum as u8);
//             new_image.push(color);
//         }
//     }
//     new_image
// }

pub fn normalize_float(transformed: &Vec<f32>) -> Vec<Hex> {
    let mut new_image: Vec<Hex> = vec![];
    let (min, max) =
        transformed
            .iter()
            .fold((std::f32::MAX, std::f32::MIN), |(mut min, mut max), &x| {
                if x < min {
                    min = x;
                }
                if x > max {
                    max = x;
                }
                (min, max)
            });
    transformed.iter().for_each(|pixel| {
        let c = (255.0 * (*pixel - min as f32) / (max - min as f32)) as u8;
        let color = gray2hex(c);
        new_image.push(color);
    });
    new_image
}

pub fn dct_multithread(image: Vec<Rgb>, width: u32, height: u32) -> (Vec<Hex>, Vec<f32>) {
    let mut coeff: Vec<f32> = vec![];
    let num_cpus = num_cpus::get() as u32;
    let mut handles = vec![];
    let mut i = 0;
    while i < num_cpus {
        let image_clone = image.clone(); // rust forces us to not do race conditions
        handles.push(thread::spawn(move || {
            let mut coeff_clone = vec![];
            let (mut ci, mut cj): (f32, f32);
            // Divide the image into chunks. Each chunk is a vector of pixels.
            for u in (i * width / num_cpus)..((i + 1) * width / num_cpus) {
                for v in 0..height {
                    ci = match u {
                        0 => (1.0 / width as f32).sqrt(),
                        _ => (2.0 / width as f32).sqrt(),
                    };
                    cj = match v {
                        0 => (1.0 / height as f32).sqrt(),
                        _ => (2.0 / height as f32).sqrt(),
                    };
                    let mut sum = 0.0;
                    for x in 0..width {
                        for y in 0..height {
                            let pixel = image_clone[(y * width + x) as usize][0] as f32;
                            let dctl = {
                                pixel
                                    * ((2.0 * x as f32 + 1.0) * u as f32 * PI
                                        / (2.0 * width as f32))
                                        .cos()
                                    * ((2.0 * y as f32 + 1.0) * v as f32 * PI
                                        / (2.0 * height as f32))
                                        .cos()
                            };
                            sum += dctl;
                        }
                    }
                    let value = sum * ci * cj;
                    coeff_clone.push(value);
                }
            }
            coeff_clone
        }));
        i += 1;
    }
    for h in handles {
        coeff.extend(h.join().unwrap());
    }
    let normalized = freq_normalize(&coeff);
    (normalized, coeff)
}

pub fn idct_multithread(coeff: Vec<f32>, width: u32, height: u32) -> Vec<Hex> {
    let mut new_image: Vec<Hex> = vec![];
    let num_cpus = num_cpus::get() as u32;
    let mut handles = vec![];
    let mut i = 0;
    while i < num_cpus {
        let coeff_clone = coeff.clone();
        handles.push(thread::spawn(move || {
            let mut new_image_clone = vec![];
            let (mut ci, mut cj): (f32, f32);
            for x in (i * width / num_cpus)..((i + 1) * width / num_cpus) {
                for y in 0..height {
                    let mut sum = 0.0;

                    for u in 0..width {
                        for v in 0..height {
                            ci = match u {
                                0 => (1.0 / width as f32).sqrt(),
                                _ => (2.0 / width as f32).sqrt(),
                            };
                            cj = match v {
                                0 => (1.0 / height as f32).sqrt(),
                                _ => (2.0 / height as f32).sqrt(),
                            };
                            let dctl = {
                                coeff_clone[(v * width + u) as usize]
                                    * ((2.0 * x as f32 + 1.0) * u as f32 * PI
                                        / (2.0 * width as f32))
                                        .cos()
                                    * ((2.0 * y as f32 + 1.0) * v as f32 * PI
                                        / (2.0 * height as f32))
                                        .cos()
                            };
                            sum += dctl * ci * cj;
                        }
                    }
                    let rounded = sum.round() as u8;
                    let color = rgb2hex(rounded, rounded, rounded);
                    new_image_clone.push(color);
                }
            }
            new_image_clone
        }));
        i += 1;
    }
    for h in handles {
        new_image.extend(h.join().unwrap());
    }
    new_image
}

pub fn freq_lowpass(
    coeff: Vec<f32>,
    width: u32,
    height: u32,
    radius: u32,
) -> (Vec<Hex>, Vec<f32>) {
    let mut new_coeff: Vec<f32> = vec![];
    for y in 0..height {
        for x in 0..width {
            if ((x * x + y * y) as f32).sqrt() <= radius as f32 {
                new_coeff.push(coeff[(y * width + x) as usize]);
            } else {
                new_coeff.push(0.0);
            }
        }
    }
    let normalized = freq_normalize(&new_coeff);
    (normalized, new_coeff)
}

pub fn freq_highpass(
    coeff: Vec<f32>,
    width: u32,
    height: u32,
    radius: u32,
) -> (Vec<Hex>, Vec<f32>) {
    let mut new_coeff: Vec<f32> = vec![];
    for y in 0..height {
        for x in 0..width {
            if ((x * x + y * y) as f32).sqrt() > radius as f32 {
                new_coeff.push(coeff[(y * width + x) as usize]);
            } else {
                new_coeff.push(0.0);
            }
        }
    }
    let normalized = freq_normalize(&new_coeff);
    (normalized, new_coeff)
}

pub fn freq_normalize(coeff: &Vec<f32>) -> Vec<Hex> {
    let mut new_coeff: Vec<f32> = vec![];
    for i in 0..coeff.len() {
        if coeff[i].abs() > 255.0 {
            new_coeff.push(255.0);
        } else {
            new_coeff.push(coeff[i].abs());
        }
    }
    let normalized = normalize_float(&new_coeff);
    normalized
}

pub fn resize_nearest_neighbor(
    image: Vec<Rgb>,
    width: u32,
    height: u32,
    new_width: u32,
    new_height: u32,
) -> Vec<Hex> {
    let mut new_image: Vec<Hex> = vec![];
    let x_ratio = width as f32 / new_width as f32;
    let y_ratio = height as f32 / new_height as f32;
    for j in 0..new_height {
        for i in 0..new_width {
            let x = (i as f32 * x_ratio) as u32;
            let y = (j as f32 * y_ratio) as u32;
            let color = image[(y * width + x) as usize];
            let value = rgb2hex(color[0], color[1], color[2]);
            new_image.push(value);
        }
    }
    new_image
}
