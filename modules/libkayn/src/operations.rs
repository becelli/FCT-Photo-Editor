use crate::common::*;
use crate::transformations;
use std::thread;

pub fn grayscale(image: Image) -> Image {
    let width = image.len();
    let height = image[0].len();
    let mut new_image = vec![vec![Rgba::default(); height]; width];

    for x in 0..width {
        for y in 0..height {
            let [r, g, b, a] = image[x][y];
            let gray = rgb2gray(r, g, b);
            let new_pixel = [gray, gray, gray, a];
            new_image[x][y] = new_pixel;
        }
    }
    new_image
}

pub fn negative(image: Image) -> Image {
    let width = image.len();
    let height = image[0].len();
    let mut new_image = vec![vec![Rgba::default(); height]; width];

    for x in 0..width {
        for y in 0..height {
            let [r, g, b, a] = image[x][y];
            let new_pixel = [255 - r, 255 - g, 255 - b, a];
            new_image[x][y] = new_pixel;
        }
    }
    new_image
}

pub fn convolute(image: Image, mask: &Vec<f32>) -> Image {
    let m_size = mask.len() as u32;
    let m_side = (m_size as f32).sqrt().round() as u32;
    let half = (m_side / 2) as u32;

    let width = image.len();
    let height = image[0].len();
    let mut new_image: Image = vec![vec![Rgba::default(); height]; width];

    for x in half..(width as u32 - half) {
        for y in half..(height as u32 - half) {
            let mut new_pixel = [0f32; 4];
            for i in 0..m_size {
                let x_ = (x + (i % m_side) - half) as usize;
                let y_ = (y + (i / m_side) - half) as usize;
                let aux_pixel = image[x_][y_];
                for j in 0..3 {
                    new_pixel[j] += aux_pixel[j] as f32 * mask[i as usize];
                }
            }
            let pixel = [
                (new_pixel[0].round() as u8),
                (new_pixel[1].round() as u8),
                (new_pixel[2].round() as u8),
                255,
            ];
            new_image[x as usize][y as usize] = pixel;
        }
    }
    normalize(new_image)
}

pub fn sobel(image: Image) -> Image {
    #[rustfmt::skip]
    let kernel_x = vec![-0.25, 0.0, 0.25,
                        -0.50, 0.0, 0.50,
                        -0.25, 0.0, 0.25];
    #[rustfmt::skip]
    let kernel_y = vec![-0.25, -0.50, -0.25,
                        0.00,  0.00,  0.00,
                        0.25,  0.50,  0.25];

    let images = thread::scope(|s| {
        let sobelx = s.spawn(|| convolute(image.clone(), &kernel_x));
        let sobely = s.spawn(|| convolute(image.clone(), &kernel_y));
        [sobelx.join().unwrap(), sobely.join().unwrap()]
    });

    let mut magnitudes: Vec<Vec<f32>> = vec![vec![0.0; image[0].len()]; image.len()];
    let width = images[0].len();
    let height = images[0][0].len();
    for x in 0..width {
        for y in 0..height {
            let [r1, g1, b1, _] = images[0][x][y];
            let [r2, g2, b2, _] = images[1][x][y];
            let gray1 = rgb2gray(r1, g1, b1);
            let gray2 = rgb2gray(r2, g2, b2);
            let magnitude = (gray1 as f32).hypot(gray2 as f32);
            magnitudes[x][y] = magnitude;
        }
    }
    transformations::normalize_float(&magnitudes)
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

pub fn dynamic_compression(image: Image, constant: f32, gamma: f32) -> Image {
    let width = image.len();
    let height = image[0].len();
    let mut new_image = vec![vec![Rgba::default(); height]; width];

    let compress = |x: u8| {
        let x = x as f32;
        let c = constant;
        let g = gamma;
        let y = c * x.powf(g);
        y as u8
    };
    for x in 0..width {
        for y in 0..height {
            let [r, g, b, a] = image[x][y];
            let new_pixel = [compress(r), compress(g), compress(b), a];
            new_image[x][y] = new_pixel;
        }
    }
    normalize(new_image)
}

pub fn normalize(image: Image) -> Image {
    let width = image.len();
    let height = image[0].len();
    let mut new_image = vec![vec![Rgba::default(); height]; width];

    let (min, max) =
        image
            .iter()
            .flatten()
            .fold(([255u8; 3], [0u8; 3]), |(mut min, mut max), pixel| {
                for i in 0..3 {
                    if pixel[i] < min[i] {
                        min[i] = pixel[i];
                    } else if pixel[i] > max[i] {
                        max[i] = pixel[i];
                    }
                }
                (min, max)
            });

    let norm = |v: [u8; 4], i| {
        let diff = (v[i] - min[i]) as f32;
        let range = (max[i] - min[i]) as f32;
        let norm = (diff / range) * 255.0;
        let rounded = norm.round() as u8;
        rounded
    };

    for x in 0..width {
        for y in 0..height {
            let pixel = image[x][y];
            let a = pixel[3];
            let (r, g, b) = (norm(pixel, 0), norm(pixel, 1), norm(pixel, 2));
            let new_pixel = [r, g, b, a];
            new_image[x][y] = new_pixel;
        }
    }
    new_image
}

pub fn limiarize(image: Image, limiar: u8) -> Image {
    let width = image.len();
    let height = image[0].len();
    let mut new_image = image.clone();

    for x in 0..width {
        for y in 0..height {
            for i in 0..3 {
                if image[x][y][i] < limiar {
                    new_image[x][y][i] = 0;
                }
            }
        }
    }
    new_image
}

pub fn binarize(image: Image, limiar: u8) -> Image {
    let width = image.len();
    let height = image[0].len();
    let mut new_image = vec![vec![Rgba::default(); height]; width];

    for x in 0..width {
        for y in 0..height {
            for i in 0..3 {
                new_image[x][y][i] = if image[x][y][i] < limiar { 0 } else { 255 };
            }
            new_image[x][y][3] = image[x][y][3];
        }
    }

    new_image
}

pub fn equalize(image: Image) -> Image {
    let width = image.len();
    let height = image[0].len();

    let mut histogram: Vec<u32> = vec![0; 256];
    image.iter().for_each(|row| {
        row.iter().for_each(|pixel| {
            let r = pixel[0] as usize;
            let g = pixel[1] as usize;
            let b = pixel[2] as usize;
            histogram[r] += 1;
            histogram[g] += 1;
            histogram[b] += 1;
        })
    });

    let mut sum: u32 = 0;
    let mut new_histogram: Vec<u32> = vec![0; 256];

    histogram.iter().enumerate().for_each(|(i, count)| {
        sum += *count;
        new_histogram[i] = sum;
    });

    let mut new_image = vec![vec![Rgba::default(); height]; width];
    for x in 0..width {
        for y in 0..height {
            let pixel = image[x][y];
            let [r, g, b, a] = pixel;
            let new_r = (new_histogram[r as usize] * 255) / sum;
            let new_g = (new_histogram[g as usize] * 255) / sum;
            let new_b = (new_histogram[b as usize] * 255) / sum;
            let new_pixel = [new_r as u8, new_g as u8, new_b as u8, a];
            new_image[x][y] = new_pixel;
        }
    }

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

pub fn noise_reduction_max(image: Vec<Rgb>, distance: u32, width: u32, height: u32) -> Vec<Hex> {
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

pub fn noise_reduction_min(image: Vec<Rgb>, distance: u32, width: u32, height: u32) -> Vec<Hex> {
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
            if !(x == 0 || y == 0 || x == width - 1 || y == height - 1) {
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
