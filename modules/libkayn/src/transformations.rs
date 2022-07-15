use std::f32::consts::PI;
type Pixel = [u8; 3];

type ColorInt = u32;

pub fn get_color_integer_from_rgb(r: u8, g: u8, b: u8) -> ColorInt {
    (r as u32) << 16 | (g as u32) << 8 | (b as u32)
}

pub fn dct(image: Vec<Pixel>, width: u32, height: u32) -> (Vec<ColorInt>, Vec<f32>) {
    let mut coeff: Vec<f32> = Vec::new();
    let (mut ci, mut cj): (f32, f32);
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

            let mut sum = 0.0;
            for x in 0..width {
                for y in 0..height {
                    let pixel = image[(y * width + x) as usize][0] as f32;
                    let dctl = {
                        pixel
                            * ((2.0 * x as f32 + 1.0) * u as f32 * PI / (2.0 * width as f32)).cos()
                            * ((2.0 * y as f32 + 1.0) * v as f32 * PI / (2.0 * height as f32)).cos()
                    };
                    sum += dctl;
                }
            }
            let value = sum * ci * cj;
            coeff.push(value);
        }
    }
    let normalized = normalize_cosine(&coeff);
    (normalized, coeff)
}

pub fn normalize_cosine(transformed: &Vec<f32>) -> Vec<ColorInt> {
    let mut new_image: Vec<ColorInt> = Vec::new();
    let (min, max) = transformed
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

pub fn idct(coef: Vec<f32>, width: u32, height: u32) -> Vec<ColorInt> {
    let mut new_image: Vec<ColorInt> = Vec::new();
    let (mut ci, mut cj): (f32, f32);
    for x in 0..width {
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
                        coef[(v * width + u) as usize]
                            * ((2.0 * x as f32 + 1.0) * u as f32 * PI / (2.0 * width as f32)).cos()
                            * ((2.0 * y as f32 + 1.0) * v as f32 * PI / (2.0 * height as f32)).cos()
                    };
                    sum += dctl * ci * cj;
                }
            }
            let color = get_color_integer_from_rgb(sum as u8, sum as u8, sum as u8);
            new_image.push(color);
        }
    }
    new_image
}
