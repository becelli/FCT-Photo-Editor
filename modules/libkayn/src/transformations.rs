use std::f32::consts::PI;
type Pixel = [u8; 3];
use std::thread;
type ColorInt = u32;

pub fn get_color_integer_from_rgb(r: u8, g: u8, b: u8) -> ColorInt {
    (r as u32) << 16 | (g as u32) << 8 | (b as u32)
}

// pub fn dct(image: Vec<Pixel>, width: u32, height: u32) -> (Vec<ColorInt>, Vec<f32>) {
//     let mut coeff: Vec<f32> = Vec::new();
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
//     let normalized = normalize_cosine(&coeff);
//     (normalized, coeff)
// }

// pub fn idct(coef: Vec<f32>, width: u32, height: u32) -> Vec<ColorInt> {
//     let mut new_image: Vec<ColorInt> = Vec::new();
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
//             let color = get_color_integer_from_rgb(sum as u8, sum as u8, sum as u8);
//             new_image.push(color);
//         }
//     }
//     new_image
// }

pub fn normalize_cosine(transformed: &Vec<f32>) -> Vec<ColorInt> {
    let mut new_image: Vec<ColorInt> = Vec::new();
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
        let c = 255.0 * (*pixel - min as f32) / (max - min as f32);
        let color = get_color_integer_from_rgb(c as u8, c as u8, c as u8);
        new_image.push(color);
    });
    new_image
}

pub fn dct_multithread(image: Vec<Pixel>, width: u32, height: u32) -> (Vec<ColorInt>, Vec<f32>) {
    let mut coeff: Vec<f32> = Vec::new();
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
    let normalized = normalize_cosine(&coeff);
    (normalized, coeff)
}

pub fn idct_multithread(coeff: Vec<f32>, width: u32, height: u32) -> Vec<ColorInt> {
    let mut new_image: Vec<ColorInt> = Vec::new();
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
                    let color = get_color_integer_from_rgb(rounded, rounded, rounded);
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

pub fn resize_nearest_neighbor(
    image: Vec<Pixel>,
    width: u32,
    height: u32,
    new_width: u32,
    new_height: u32,
) -> Vec<ColorInt> {
    let mut new_image: Vec<ColorInt> = Vec::new();
    let x_ratio = width as f32 / new_width as f32;
    let y_ratio = height as f32 / new_height as f32;
    for j in 0..new_height {
        for i in 0..new_width {
            let x = (i as f32 * x_ratio) as u32;
            let y = (j as f32 * y_ratio) as u32;
            let color = image[(y * width + x) as usize];
            let value = get_color_integer_from_rgb(color[0], color[1], color[2]);
            new_image.push(value);
        }
    }
    new_image
}
