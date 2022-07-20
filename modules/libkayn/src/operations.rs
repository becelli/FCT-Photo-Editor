type Pixel = [u8; 3];
type ColorInt = u32;

pub fn get_color_integer_from_rgb(r: u8, g: u8, b: u8) -> ColorInt {
    (r as u32) << 16 | (g as u32) << 8 | (b as u32)
}

pub fn get_color_integer_from_gray(gray: u8) -> ColorInt {
    (gray as u32) << 16 | (gray as u32) << 8 | (gray as u32)
}

pub fn grayscale(image: Vec<Pixel>) -> Vec<ColorInt> {
    let mut new_image: Vec<ColorInt> = Vec::new();
    image.iter().for_each(|pixel| {
        let gray_tone =
            (((pixel[0] as f32) + (pixel[1] as f32) + (pixel[2] as f32)) / 3.0).round() as u8;
        let color = get_color_integer_from_gray(gray_tone);
        new_image.push(color);
    });
    new_image
}

pub fn negative(image: Vec<Pixel>) -> Vec<ColorInt> {
    let mut new_image: Vec<ColorInt> = Vec::new();
    image.iter().for_each(|pixel| {
        let r = 255 - pixel[2];
        let g = 255 - pixel[1];
        let b = 255 - pixel[0];
        let color = get_color_integer_from_rgb(r, g, b);
        new_image.push(color);
    });
    new_image
}

pub fn filter_nxn(image: Vec<Pixel>, filter: Vec<f32>, width: u32, height: u32) -> Vec<ColorInt> {
    let f_size = filter.len() as u32;
    let f_side = (f_size as f32).sqrt().round() as u32;
    let half = (f_side / 2) as u32;
    let mut new_image: Vec<ColorInt> = Vec::new();

    for x in half..(width - half) {
        for y in half..(height - half) {
            let mut new_pixel = [0f32; 3];
            for i in 0..f_size {
                let x_: u32 = x + (i % f_side) - half;
                let y_: u32 = y + (i / f_side) - half;
                let aux_pixel = image[(y_ * width + x_) as usize];
                aux_pixel.iter().rev().enumerate().for_each(|(ch, color)| {
                    new_pixel[ch] += *color as f32 * filter[i as usize];
                });
            }
            let color = get_color_integer_from_rgb(
                new_pixel[0] as u8,
                new_pixel[1] as u8,
                new_pixel[2] as u8,
            );
            new_image.push(color);
        }
    }
    new_image
}

pub fn median(image: Vec<Pixel>, distance: u32, width: u32, height: u32) -> Vec<ColorInt> {
    let f_size = (distance * 2 + 1).pow(2) as u32;
    let f_side = 2 * distance + 1;
    let half = (f_side / 2) as u32;
    let mut new_image: Vec<ColorInt> = Vec::new();

    for y in half..(height - half) {
        for x in half..(width - half) {
            let mut pixels: Vec<Pixel> = vec![[0u8; 3]; f_size as usize];
            for i in 0..f_size {
                let x_: u32 = x + (i % f_side) - half;
                let y_: u32 = y + (i / f_side) - half;
                let aux_pixel = image[(y_ * width + x_) as usize];
                pixels[i as usize] = aux_pixel;
            }

            pixels.sort_by(|a, b| {
                let a_ = get_color_integer_from_rgb(a[2], a[1], a[0]);
                let b_ = get_color_integer_from_rgb(b[2], b[1], b[0]);
                a_.partial_cmp(&b_).unwrap()
            });

            let new_pixel = get_color_integer_from_rgb(
                pixels[f_size as usize / 2][2],
                pixels[f_size as usize / 2][1],
                pixels[f_size as usize / 2][0],
            );
            new_image.push(new_pixel);
        }
    }
    new_image
}

pub fn dynamic_compression(image: Vec<Pixel>, constant: f32, gamma: f32) -> Vec<ColorInt> {
    let mut compressed_img: Vec<Pixel> = Vec::new();
    // Yes. The channels are not in the reverse order. When we normalize it
    // It will be in the right order.
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

pub fn normalize(image: Vec<Pixel>) -> Vec<ColorInt> {
    let mut new_image: Vec<ColorInt> = Vec::new();
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
        let b = 255.0 * (pixel[0] - min[0]) as f32 / (max[0] - min[0]) as f32;
        let g = 255.0 * (pixel[1] - min[1]) as f32 / (max[1] - min[1]) as f32;
        let r = 255.0 * (pixel[2] - min[2]) as f32 / (max[2] - min[2]) as f32;
        let color = get_color_integer_from_rgb(r as u8, g as u8, b as u8);
        new_image.push(color);
    });
    new_image
}

pub fn limiarize(image: Vec<Pixel>, limiar: u8) -> Vec<ColorInt> {
    let mut new_image: Vec<ColorInt> = Vec::new();
    image.iter().for_each(|pixel| {
        let mut new_pixel = pixel.clone();
        pixel.iter().enumerate().for_each(|(ch, color)| {
            if *color < limiar + 1 {
                new_pixel[ch] = 0;
            }
        });
        let color = get_color_integer_from_rgb(new_pixel[2], new_pixel[1], new_pixel[0]);
        new_image.push(color);
    });
    new_image
}

pub fn binarize(image: Vec<Pixel>, limiar: u8) -> Vec<ColorInt> {
    let mut new_image: Vec<ColorInt> = Vec::new();
    image.iter().for_each(|pixel| {
        let mut new_pixel = [0u8; 3];
        pixel.iter().enumerate().for_each(|(ch, color)| {
            if *color > limiar {
                new_pixel[ch] = 255;
            } else {
                new_pixel[ch] = 0;
            }
        });
        let color = get_color_integer_from_rgb(new_pixel[2], new_pixel[1], new_pixel[0]);
        new_image.push(color);
    });
    new_image
}

pub fn equalize(image: Vec<Pixel>) -> Vec<ColorInt> {
    let mut histogram: Vec<u32> = vec![0; 256];
    image.iter().for_each(|pixel| {
        let r = pixel[2] as u32;
        let g = pixel[1] as u32;
        let b = pixel[0] as u32;
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
    let mut new_image: Vec<ColorInt> = Vec::new();
    image.iter().for_each(|pixel| {
        let (r, g, b) = (pixel[2] as u32, pixel[1] as u32, pixel[0] as u32);
        let new_r = (new_histogram[r as usize] * 255) / sum;
        let new_g = (new_histogram[g as usize] * 255) / sum;
        let new_b = (new_histogram[b as usize] * 255) / sum;
        let color = get_color_integer_from_rgb(new_r as u8, new_g as u8, new_b as u8);
        new_image.push(color);
    });
    new_image
}
pub fn gray_to_color_scale(image: Vec<Pixel>) -> Vec<ColorInt> {
    let mut new_image: Vec<ColorInt> = Vec::new();
    image.iter().for_each(|pixel| {
        let gray = ((pixel[0] as u16 + pixel[1] as u16 + pixel[2] as u16) / 3) as u8;
        let (r, g, b) = match gray {
            0..=63 => (0, 0, gray * 4),
            64..=127 => (0, (gray - 64) * 4, 255),
            128..=191 => (0, 255, 255 - (gray - 128) * 4),
            _ => ((gray - 192) * 4, 255, 0),
        };
        let color = get_color_integer_from_rgb(r, g, b);
        new_image.push(color);
    });
    new_image
}

pub fn noise_reduction_max(
    image: Vec<Pixel>,
    distance: u32,
    width: u32,
    height: u32,
) -> Vec<ColorInt> {
    let f_size = (distance * 2 + 1).pow(2) as u32;
    let f_side = 2 * distance + 1;
    let half = (f_side / 2) as u32;
    let mut new_image: Vec<ColorInt> = Vec::new();

    for y in half..(height - half) {
        for x in half..(width - half) {
            let mut pixels: Vec<Pixel> = vec![[0u8; 3]; f_size as usize];
            for i in 0..f_size {
                let x_: u32 = x + (i % f_side) - half;
                let y_: u32 = y + (i / f_side) - half;
                let aux_pixel = image[(y_ * width + x_) as usize];
                pixels[i as usize] = aux_pixel;
            }

            pixels.sort_by(|a, b| {
                let a_ = get_color_integer_from_rgb(a[2], a[1], a[0]);
                let b_ = get_color_integer_from_rgb(b[2], b[1], b[0]);
                a_.partial_cmp(&b_).unwrap()
            });

            let new_pixel = get_color_integer_from_rgb(
                pixels[f_size as usize - 1][2],
                pixels[f_size as usize - 1][1],
                pixels[f_size as usize - 1][0],
            );
            new_image.push(new_pixel);
        }
    }
    new_image
}

pub fn noise_reduction_min(
    image: Vec<Pixel>,
    distance: u32,
    width: u32,
    height: u32,
) -> Vec<ColorInt> {
    let f_size = (distance * 2 + 1).pow(2) as u32;
    let f_side = 2 * distance + 1;
    let half = (f_side / 2) as u32;
    let mut new_image: Vec<ColorInt> = Vec::new();

    for y in half..(height - half) {
        for x in half..(width - half) {
            let mut pixels: Vec<Pixel> = vec![[0u8; 3]; f_size as usize];
            for i in 0..f_size {
                let x_: u32 = x + (i % f_side) - half;
                let y_: u32 = y + (i / f_side) - half;
                let aux_pixel = image[(y_ * width + x_) as usize];
                pixels[i as usize] = aux_pixel;
            }

            pixels.sort_by(|a, b| {
                let a_ = get_color_integer_from_rgb(a[2], a[1], a[0]);
                let b_ = get_color_integer_from_rgb(b[2], b[1], b[0]);
                a_.partial_cmp(&b_).unwrap()
            });

            let new_pixel = get_color_integer_from_rgb(pixels[0][2], pixels[0][1], pixels[0][0]);
            new_image.push(new_pixel);
        }
    }
    new_image
}

pub fn noise_reduction_midpoint(
    image: Vec<Pixel>,
    distance: u32,
    width: u32,
    height: u32,
) -> Vec<ColorInt> {
    let f_size = (distance * 2 + 1).pow(2) as u32;
    let f_side = 2 * distance + 1;
    let half = (f_side / 2) as u32;
    let mut new_image: Vec<ColorInt> = Vec::new();

    for y in half..(height - half) {
        for x in half..(width - half) {
            let mut pixels: Vec<Pixel> = vec![[0u8; 3]; f_size as usize];
            for i in 0..f_size {
                let x_: u32 = x + (i % f_side) - half;
                let y_: u32 = y + (i / f_side) - half;
                let aux_pixel = image[(y_ * width + x_) as usize];
                pixels[i as usize] = aux_pixel;
            }

            pixels.sort_by(|a, b| {
                let a_ = get_color_integer_from_rgb(a[2], a[1], a[0]);
                let b_ = get_color_integer_from_rgb(b[2], b[1], b[0]);
                a_.partial_cmp(&b_).unwrap()
            });

            let new_pixel = get_color_integer_from_rgb(
                pixels[0][2] / 2 + pixels[f_size as usize - 1][2] / 2,
                pixels[0][1] / 2 + pixels[f_size as usize - 1][1] / 2,
                pixels[0][0] / 2 + pixels[f_size as usize - 1][0] / 2,
            );
            new_image.push(new_pixel);
        }
    }
    new_image
}

pub fn otsu_thresholding(image: Vec<Pixel>, width: u32, height: u32) -> u8 {
    let max_gray_value = 255 as u8;
    let mut global_average = 0 as f32;
    let mut max_ni = 0 as f32;
    let mut limiar_candidate = 0 as u8;
    let mut gray_shade_frequency: [f32; 256] = [0.0; 256];
    let image_size = width * height as u32;
    image.iter().for_each(|pixel| {
        gray_shade_frequency
            [((pixel[0] as u32 + pixel[1] as u32 + pixel[2] as u32) / 3) as usize] += 1.0;
    });
    for i in 0..=max_gray_value {
        gray_shade_frequency[i as usize] = gray_shade_frequency[i as usize] / (image_size as f32);
        global_average += gray_shade_frequency[i as usize] * i as f32;
    }
    //in this loop, i equals t from the OTSU threshold method
    for i in 0..=max_gray_value {
        let mut threshold_average = 0 as f32;
        let mut threshold_ratio = 0 as f32;
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
