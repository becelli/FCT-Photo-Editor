use crate::common::*;
use crate::transformations;
use std::thread;

pub fn grayscale(image: Vec<Rgb>) -> Vec<Hex> {
    let mut new_image: Vec<Hex> = vec![];
    image.iter().for_each(|pixel| {
        let gray_tone = rgb2gray(pixel[0], pixel[1], pixel[2]);
        let color = gray2hex(gray_tone);
        new_image.push(color);
    });
    new_image
}

pub fn negative(image: Vec<Rgb>) -> Vec<Hex> {
    let mut new_image: Vec<Hex> = vec![];
    image.iter().for_each(|pixel| {
        let r = 255 - pixel[0];
        let g = 255 - pixel[1];
        let b = 255 - pixel[2];
        let color = rgb2hex(r, g, b);
        new_image.push(color);
    });
    new_image
}

pub fn convolute(image: Vec<Rgb>, mask: &Vec<f32>, width: u32, height: u32) -> Vec<Hex> {
    let m_size = mask.len() as u32;
    let m_side = (m_size as f32).sqrt().round() as u32;
    let half = (m_side / 2) as u32;
    let mut new_image: Vec<Rgb> = vec![];

    for x in half..(width - half) {
        for y in half..(height - half) {
            let mut new_pixel = [0f32; 3];
            for i in 0..m_size {
                let x_: u32 = x + (i % m_side) - half;
                let y_: u32 = y + (i / m_side) - half;
                let aux_pixel = image[(y_ * width + x_) as usize];
                aux_pixel.iter().enumerate().for_each(|(ch, color)| {
                    new_pixel[ch] += *color as f32 * mask[i as usize];
                });
            }
            let pixel = [
                (new_pixel[0].round() as u8),
                (new_pixel[1].round() as u8),
                (new_pixel[2].round() as u8),
            ];
            new_image.push(pixel);
        }
    }
    let normalized = normalize(new_image);
    normalized
}

pub fn sobel(image: Vec<Rgb>, width: u32, height: u32) -> Vec<Hex> {
    #[rustfmt::skip]
    let kernel_x = vec![-0.25, 0.0, 0.25,
                        -0.50, 0.0, 0.50,
                        -0.25, 0.0, 0.25];
    #[rustfmt::skip]
    let kernel_y = vec![-0.25, -0.50, -0.25,
                        0.00,  0.00,  0.00,
                        0.25,  0.50,  0.25];
    let mut handlers = vec![];

    let clone = image.clone();
    handlers.push(thread::spawn(move || {
        convolute(clone, &kernel_x, width, height)
    }));

    let clone = image.clone();
    handlers.push(thread::spawn(move || {
        convolute(clone, &kernel_y, width, height)
    }));

    let mut images = vec![];
    for handler in handlers {
        images.push(handler.join().unwrap());
    }
    let mut magnitudes: Vec<f32> = vec![];
    images[0].iter().zip(images[1].iter()).for_each(|(x, y)| {
        let gray1 = hex2gray(*x) as f32;
        let gray2 = hex2gray(*y) as f32;
        let mag = (gray1.powi(2) + gray2.powi(2)).sqrt() as f32;
        magnitudes.push(mag);
    });
    let normalized = transformations::normalize_float(&magnitudes);
    normalized
}

pub fn median(image: Vec<Rgb>, distance: u32, width: u32, height: u32) -> Vec<Hex> {
    let m_size = (distance * 2 + 1).pow(2) as u32;
    let m_side = 2 * distance + 1;
    let half = (m_side / 2) as u32;
    let mut new_image: Vec<Hex> = vec![];

    for x in half..(width - half) {
        for y in half..(height - half) {
            let mut pixels: Vec<Rgb> = vec![[0u8; 3]; m_size as usize];
            for i in 0..m_size {
                let x_: u32 = x + (i % m_side) - half;
                let y_: u32 = y + (i / m_side) - half;
                let aux_pixel = image[(y_ * width + x_) as usize];
                pixels[i as usize] = aux_pixel;
            }

            pixels.sort_by(|a, b| {
                let a_ = rgb2hex(a[2], a[1], a[0]);
                let b_ = rgb2hex(b[2], b[1], b[0]);
                a_.partial_cmp(&b_).unwrap()
            });

            let new_pixel = rgb2hex(
                pixels[m_size as usize / 2][0],
                pixels[m_size as usize / 2][1],
                pixels[m_size as usize / 2][2],
            );
            new_image.push(new_pixel);
        }
    }
    new_image
}

pub fn dynamic_compression(image: Vec<Rgb>, constant: f32, gamma: f32) -> Vec<Hex> {
    let mut compressed_img: Vec<Rgb> = vec![];
    image.iter().for_each(|pixel| {
        let r = (pixel[0] as f32).powf(gamma) * constant;
        let g = (pixel[1] as f32).powf(gamma) * constant;
        let b = (pixel[2] as f32).powf(gamma) * constant;
        let color = [r as u8, g as u8, b as u8];
        compressed_img.push(color);
    });

    let new_image = normalize(compressed_img);
    new_image
}

pub fn normalize(image: Vec<Rgb>) -> Vec<Hex> {
    let mut new_image: Vec<Hex> = vec![];
    let (min, max) = image
        .iter()
        .fold(([255u8; 3], [0u8; 3]), |(mut min, mut max), pixel| {
            if pixel[0] < min[0] {
                min[0] = pixel[0];
            }
            if pixel[1] < min[1] {
                min[1] = pixel[1];
            }
            if pixel[2] < min[2] {
                min[2] = pixel[2];
            }
            if pixel[0] > max[0] {
                max[0] = pixel[0];
            }
            if pixel[1] > max[1] {
                max[1] = pixel[1];
            }
            if pixel[2] > max[2] {
                max[2] = pixel[2];
            }
            (min, max)
        });

    image.iter().for_each(|pixel| {
        let r = 255.0 * (pixel[0] - min[0]) as f32 / (max[0] - min[0]) as f32;
        let g = 255.0 * (pixel[1] - min[1]) as f32 / (max[1] - min[1]) as f32;
        let b = 255.0 * (pixel[2] - min[2]) as f32 / (max[2] - min[2]) as f32;
        let color = rgb2hex(r as u8, g as u8, b as u8);
        new_image.push(color);
    });
    new_image
}

pub fn limiarize(image: Vec<Rgb>, limiar: u8) -> Vec<Hex> {
    let mut new_image: Vec<Hex> = vec![];
    image.iter().for_each(|pixel| {
        let mut new_pixel = pixel.clone();
        pixel.iter().enumerate().for_each(|(ch, color)| {
            if *color < limiar + 1 {
                new_pixel[ch] = 0;
            }
        });
        let color = rgb2hex(new_pixel[0], new_pixel[1], new_pixel[2]);
        new_image.push(color);
    });
    new_image
}

pub fn binarize(image: Vec<Rgb>, limiar: u8) -> Vec<Hex> {
    let mut new_image: Vec<Hex> = vec![];
    image.iter().for_each(|pixel| {
        let mut new_pixel = [0u8; 3];
        pixel.iter().enumerate().for_each(|(ch, color)| {
            if *color > limiar {
                new_pixel[ch] = 255;
            } else {
                new_pixel[ch] = 0;
            }
        });
        let color = rgb2hex(new_pixel[0], new_pixel[1], new_pixel[2]);
        new_image.push(color);
    });
    new_image
}

pub fn equalize(image: Vec<Rgb>) -> Vec<Hex> {
    let mut histogram: Vec<u32> = vec![0; 256];
    image.iter().for_each(|pixel| {
        let r = pixel[0] as u32;
        let g = pixel[1] as u32;
        let b = pixel[2] as u32;
        histogram[r as usize] += 1;
        histogram[g as usize] += 1;
        histogram[b as usize] += 1;
    });
    let mut sum: u32 = 0;
    let mut new_histogram: Vec<u32> = vec![0; 256];
    histogram.iter().enumerate().for_each(|(i, count)| {
        sum += *count;
        new_histogram[i] = sum;
    });
    let mut new_image: Vec<Hex> = vec![];
    image.iter().for_each(|pixel| {
        let (r, g, b) = (pixel[0] as u32, pixel[1] as u32, pixel[2] as u32);
        let new_r = (new_histogram[r as usize] * 255) / sum;
        let new_g = (new_histogram[g as usize] * 255) / sum;
        let new_b = (new_histogram[b as usize] * 255) / sum;
        let color = rgb2hex(new_r as u8, new_g as u8, new_b as u8);
        new_image.push(color);
    });
    new_image
}
pub fn gray_to_color_scale(image: Vec<Rgb>) -> Vec<Hex> {
    let mut new_image: Vec<Hex> = vec![];
    image.iter().for_each(|pixel| {
        let gray = rgb2gray(pixel[0], pixel[1], pixel[2]);
        let (r, g, b) = match gray {
            0..=63 => (0, 0, gray * 4),
            64..=127 => (0, (gray - 64) * 4, 255),
            128..=191 => (0, 255, 255 - (gray - 128) * 4),
            _ => ((gray - 192) * 4, 255, 0),
        };
        let color = rgb2hex(r, g, b);
        new_image.push(color);
    });
    new_image
}

pub fn noise_reduction_max(
    image: Vec<Rgb>,
    distance: u32,
    width: u32,
    height: u32,
) -> Vec<Hex> {
    let m_size = (distance * 2 + 1).pow(2) as u32;
    let m_side = 2 * distance + 1;
    let half = (m_side / 2) as u32;
    let mut new_image: Vec<Hex> = vec![];

    for x in half..(width - half) {
        for y in half..(height - half) {
            let mut pixels: Vec<Rgb> = vec![[0u8; 3]; m_size as usize];
            for i in 0..m_size {
                let x_: u32 = x + (i % m_side) - half;
                let y_: u32 = y + (i / m_side) - half;
                let aux_pixel = image[(y_ * width + x_) as usize];
                pixels[i as usize] = aux_pixel;
            }

            pixels.sort_by(|a, b| {
                let a_ = rgb2hex(a[0], a[1], a[2]);
                let b_ = rgb2hex(b[0], b[1], b[2]);
                a_.partial_cmp(&b_).unwrap()
            });

            let new_pixel = rgb2hex(
                pixels[m_size as usize - 1][0],
                pixels[m_size as usize - 1][1],
                pixels[m_size as usize - 1][2],
            );
            new_image.push(new_pixel);
        }
    }
    new_image
}

pub fn noise_reduction_min(
    image: Vec<Rgb>,
    distance: u32,
    width: u32,
    height: u32,
) -> Vec<Hex> {
    let m_size = (distance * 2 + 1).pow(2) as u32;
    let m_side = 2 * distance + 1;
    let half = (m_side / 2) as u32;
    let mut new_image: Vec<Hex> = vec![];

    for x in half..(width - half) {
        for y in half..(height - half) {
            let mut pixels: Vec<Rgb> = vec![[0u8; 3]; m_size as usize];
            for i in 0..m_size {
                let x_: u32 = x + (i % m_side) - half;
                let y_: u32 = y + (i / m_side) - half;
                let aux_pixel = image[(y_ * width + x_) as usize];
                pixels[i as usize] = aux_pixel;
            }

            pixels.sort_by(|a, b| {
                let a_ = rgb2hex(a[0], a[1], a[2]);
                let b_ = rgb2hex(b[0], b[1], b[2]);
                a_.partial_cmp(&b_).unwrap()
            });

            let new_pixel = rgb2hex(pixels[0][0], pixels[0][1], pixels[0][2]);
            new_image.push(new_pixel);
        }
    }
    new_image
}

pub fn noise_reduction_midpoint(
    image: Vec<Rgb>,
    distance: u32,
    width: u32,
    height: u32,
) -> Vec<Hex> {
    let m_size = (distance * 2 + 1).pow(2) as u32;
    let m_side = 2 * distance + 1;
    let half = (m_side / 2) as u32;
    let mut new_image: Vec<Hex> = vec![];

    for x in half..(width - half) {
        for y in half..(height - half) {
            let mut pixels: Vec<Rgb> = vec![[0u8; 3]; m_size as usize];
            for i in 0..m_size {
                let x_: u32 = x + (i % m_side) - half;
                let y_: u32 = y + (i / m_side) - half;
                let aux_pixel = image[(y_ * width + x_) as usize];
                pixels[i as usize] = aux_pixel;
            }

            pixels.sort_by(|a, b| {
                let a_ = rgb2hex(a[0], a[1], a[2]);
                let b_ = rgb2hex(b[0], b[1], b[2]);
                a_.partial_cmp(&b_).unwrap()
            });

            let new_pixel = rgb2hex(
                pixels[0][0] / 2 + pixels[m_size as usize - 1][0] / 2,
                pixels[0][1] / 2 + pixels[m_size as usize - 1][1] / 2,
                pixels[0][2] / 2 + pixels[m_size as usize - 1][2] / 2,
            );
            new_image.push(new_pixel);
        }
    }
    new_image
}

pub fn otsu_thresholding(image: Vec<Rgb>, width: u32, height: u32) -> u8 {
    let max_gray_value = 255u8;
    let mut global_average = 0f32;
    let mut max_ni = 0f32;
    let mut limiar_candidate = 0u8;
    let mut gray_shade_frequency = [0f32; 256];
    let image_size = width * height as u32;
    image.iter().for_each(|pixel| {
        gray_shade_frequency[rgb2gray(pixel[0], pixel[1], pixel[2]) as usize] += 1.0;
    });
    for i in 0..=max_gray_value {
        gray_shade_frequency[i as usize] = gray_shade_frequency[i as usize] / (image_size as f32);
        global_average += gray_shade_frequency[i as usize] * i as f32;
    }
    //in this loop, i equals t from the OTSU threshold method
    for i in 0..=max_gray_value {
        let mut threshold_average = 0f32;
        let mut threshold_ratio = 0f32;
        for j in 0..=i {
            threshold_ratio += gray_shade_frequency[j as usize];
            threshold_average += gray_shade_frequency[j as usize] * j as f32;
        }
        let average_0: f32 = threshold_average / threshold_ratio;
        let complementary_threshold_ratio: f32 = 1.0 - threshold_ratio;
        let average_1: f32 = (global_average - threshold_average) / complementary_threshold_ratio;
        let threshold_std_deviation: f32 =
            threshold_ratio * complementary_threshold_ratio * (average_0 - average_1).powf(2.0);
        if threshold_std_deviation > max_ni {
            max_ni = threshold_std_deviation;
            limiar_candidate = i;
        }
    }
    limiar_candidate
}

pub fn equalize_hsl(image: Vec<Rgb>) -> Vec<Hex> {
    let mut histogram: Vec<u32> = vec![0; 241];
    let mut hsl_image: Vec<Rgb> = vec![];
    image.iter().for_each(|pixel| {
        let hsl_pixel: Rgb = rgb2hsl(*pixel);
        let l = hsl_pixel[2] as u8;
        histogram[l as usize] += 1;
        hsl_image.push(hsl_pixel);
    });
    let mut sum: u32 = 0;
    let mut new_histogram: Vec<u32> = vec![0; 241];
    histogram.iter().enumerate().for_each(|(i, count)| {
        sum += *count;
        new_histogram[i] = sum;
    });
    let mut equalized_image: Vec<Hex> = vec![];
    hsl_image.iter().for_each(|pixel| {
        let new_l = (new_histogram[pixel[2] as usize] * 240) / sum;
        let new_pixel: Hsl = [pixel[0] as u8, pixel[1] as u8, new_l as u8];
        let color: Hex = hsl2hex(new_pixel);
        equalized_image.push(color);
    });
    equalized_image
}

pub fn split_color_channel(image: Vec<Rgb>, channel: usize) -> Vec<Hex> {
    let mut new_image: Vec<Hex> = vec![];
    image.iter().for_each(|pixel| {
        let new_color = match channel {
            0 => [pixel[0], 0, 0],
            1 => [0, pixel[1], 0],
            2 => [0, 0, pixel[2]],
            _ => [0, 0, 0],
        };
        let new_pixel = rgb2hex(new_color[0], new_color[1], new_color[2]);
        new_image.push(new_pixel);
    });
    new_image
}

pub fn erosion(image: Vec<Rgb>, width: i32, height: i32) -> Vec<Hex> {
    let mask = vec![[0, 1, 0], [1, 1, 1], [0, 1, 0]];
    let mut new_image: Vec<Hex> = vec![0; image.len()];

    for x in 1..width - 1 {
        for y in 1..height - 1 {
            let mut to_remove = false;
            let pixel = image[(y * width + x) as usize];
            let color = rgb2gray(pixel[0], pixel[1], pixel[2]);
            if color > 0 {
                to_remove = true;
                for i in -1..=1 {
                    for j in -1..=1 {
                        if mask[(i + 1) as usize][(j + 1) as usize] == 1 {
                            let aux = image[((y + j) * width + x + i) as usize];
                            let gray = rgb2gray(aux[0], aux[1], aux[2]);
                            if gray == 0 {
                                to_remove = false;
                                break;
                            }
                        }
                    }
                }
            }
            if to_remove {
                new_image[(y * width + x) as usize] = 0xFFFFFFFF;
            }
        }
    }
    new_image
}

pub fn dilation(image: Vec<Rgb>, width: i32, height: i32) -> Vec<Hex> {
    let mask = vec![[0, 1, 0], [1, 1, 1], [0, 1, 0]];
    let mut new_image: Vec<Hex> = vec![0; image.len()];

    for x in 1..width - 1 {
        for y in 1..height - 1 {
            let pixel = image[(y * width + x) as usize];
            let color = rgb2gray(pixel[0], pixel[1], pixel[2]);
            if color > 0 {
                for i in -1..=1 {
                    for j in -1..=1 {
                        if mask[(i + 1) as usize][(j + 1) as usize] == 1 {
                            new_image[((y + j) * width + x + i) as usize] = 0xFFFFFFFF;
                        }
                    }
                }
            }
        }
    }
    new_image
}

//Too lazy to work with pixels, so i made this function to work with 0s and 1s
pub fn binarize_vector(image: Vec<Rgb>, width: u32, height: u32) -> Vec<bool> {
    let mut border_vector: Vec<bool> = vec![false; (width * height) as usize];
    for x in 0..width {
        for y in 0..height {
            if !(x == 0 || y == 0 || x == width-1 || y == height-1){
                let pixel = image[(y * width + x) as usize];
                if pixel[0] != 0 || pixel[1] != 0 || pixel[2] != 0 {
                    border_vector[(y * width + x) as usize] = true;
                }   
            }
        }
    }
    border_vector
}

pub fn count_neighbors(p: &Vec<bool>) -> u8 {
    let mut total_neighbors: u8 = 0;
    for i in 1..9 {
        if p[i as usize] {
            total_neighbors += 1;
        }
    }
    total_neighbors
}

pub fn transitions(p: &Vec<bool>) -> u8 {
    let mut total_transitions: u8 = 0;
    for i in 1..8 {
        if !p[i as usize] && p[(i + 1) as usize] {
            total_transitions += 1;
        }
    }
    if !p[8] && p[1] {
        total_transitions += 1;
    }
    total_transitions
}

pub fn zhang_suen_step_1(image_borders: &Vec<bool>, width: u32, height: u32) -> Vec<bool> {
    let mut marked_to_be_erased: Vec<bool> = vec![];
    for x in 0..width {
        for y in 0..height {
            let temp_position: u32 = x * height + y;
            let mut p: Vec<bool> = vec![];
            p.push(image_borders[temp_position as usize]);
            if p[0] {
                p.push(image_borders[(temp_position - width) as usize]);
                p.push(image_borders[(temp_position - width + 1) as usize]);
                p.push(image_borders[(temp_position + 1) as usize]);
                p.push(image_borders[(temp_position + width + 1) as usize]);
                p.push(image_borders[(temp_position + width) as usize]);
                p.push(image_borders[(temp_position + width - 1) as usize]);
                p.push(image_borders[(temp_position - 1) as usize]);
                p.push(image_borders[(temp_position - width - 1) as usize]);
                let num_neighbors = count_neighbors(&p);
                let num_transitions = transitions(&p);
                let neighbors_246 = p[1] && p[3] && p[5];
                let neighbors_468 = p[3] && p[5] && p[7];
                if (num_neighbors >= 2)
                    && (num_neighbors <= 6)
                    && (num_transitions == 1)
                    && (!neighbors_246)
                    && (!neighbors_468)
                {
                    marked_to_be_erased.push(true);
                } else {
                    marked_to_be_erased.push(false);
                }
            } else {
                marked_to_be_erased.push(false);
            }
        }
    }
    marked_to_be_erased
}

pub fn zhang_suen_step_2(image_borders: &Vec<bool>, width: u32, height: u32) -> Vec<bool> {
    let mut marked_to_be_erased: Vec<bool> = vec![];
    for x in 0..width {
        for y in 0..height {
            let temp_position: u32 = x * height + y;
            let mut p: Vec<bool> = vec![];
            p.push(image_borders[temp_position as usize]);
            if p[0] {
                p.push(image_borders[(temp_position - width) as usize]);
                p.push(image_borders[(temp_position - width + 1) as usize]);
                p.push(image_borders[(temp_position + 1) as usize]);
                p.push(image_borders[(temp_position + width + 1) as usize]);
                p.push(image_borders[(temp_position + width) as usize]);
                p.push(image_borders[(temp_position + width - 1) as usize]);
                p.push(image_borders[(temp_position - 1) as usize]);
                p.push(image_borders[(temp_position - width - 1) as usize]);
                let num_neighbors = count_neighbors(&p);
                let num_transitions = transitions(&p);
                let neighbors_248 = p[1] && p[3] && p[7];
                let neighbors_268 = p[1] && p[5] && p[7];
                if (num_neighbors >= 2)
                    && (num_neighbors <= 6)
                    && (num_transitions == 1)
                    && (!neighbors_248)
                    && (!neighbors_268)
                {
                    marked_to_be_erased.push(true);
                } else {
                    marked_to_be_erased.push(false);
                }
            } else {
                marked_to_be_erased.push(false);
            }
        }
    }
    marked_to_be_erased
}

pub fn zhang_suen_thinning(image: Vec<Rgb>, width: u32, height: u32) -> Vec<Hex> {
    let mut binary_image = binarize_vector(image, width, height);

    loop {
        let mut has_changed: bool = false;
        
        let marked_to_be_erased = zhang_suen_step_1(&binary_image, width, height);
        for x in 0..width {
            for y in 0..height {
                let temp_position = (y * width + x) as usize;
                if marked_to_be_erased[temp_position] {
                    binary_image[temp_position] = false;
                    has_changed = true;
                }
            }
        }

        //Apply the second step of zhang suen method
        let marked_to_be_erased = zhang_suen_step_2(&binary_image, width, height);
        for x in 0..width {
            for y in 0..height {
                let temp_position = (y * width + x) as usize;
                if marked_to_be_erased[temp_position] {
                    binary_image[temp_position] = false;
                    has_changed = true;
                }
            }
        }

        if !has_changed {
            break;
        }
    }
    let mut new_image: Vec<Hex> = vec![];
    binary_image.iter().for_each(|pixel| {
        let color = match pixel {
            true => 0xFFFFFFFF,
            false => 0xFF000000,
        };
        new_image.push(color);
    });
    new_image
}
