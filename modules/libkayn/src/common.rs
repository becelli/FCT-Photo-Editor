pub type Hex = u32;
pub type Rgb = [u8; 3];
pub type Rgba = [u8; 4];
pub type Hsl = [u8; 3];
pub type Image = Vec<Vec<Rgba>>;
// pub type DCTCoefficients = Vec<Vec<f32>>;
pub type Gray = u8;

pub fn rgb2hex(r: u8, g: u8, b: u8) -> Hex {
    (r as u32) << 16 | (g as u32) << 8 | (b as u32)
}

pub fn rgb2gray(r: u8, g: u8, b: u8) -> Gray {
    ((r as u16 + g as u16 + b as u16) / 3) as Gray
}

pub fn rgb2hsl(pixel: Rgb) -> Hsl {
    /*
    Convert to microsoft's hsl
    where h is 0-239, s is 0-240, l is 0-240
    and the rgb values are 0-255
    */
    let (r, g, b) = (
        pixel[0] as f32 / 255.0,
        pixel[1] as f32 / 255.0,
        pixel[2] as f32 / 255.0,
    );
    let mx = f32::max(r, f32::max(g, b)) as f32;
    let mn = f32::min(r, f32::min(g, b)) as f32;
    let mut h: f32;
    let mut s: f32 = 0.0;
    let l: f32 = (mx + mn) / 2.0;

    let d: f32 = mx - mn;
    if d == 0.0 {
        h = 0.0;
    } else if mx == r {
        h = ((g - b) / d) % 6.0;
    } else if mx == g {
        h = (b - r) / d + 2.0;
    } else {
        h = (r - g) / d + 4.0;
    }
    h = h * 40.0;

    if h < 0.0 {
        h += 240.0;
    }
    if d != 0.0 {
        s = d / (1.0 - (2.0 * l - 1.0).abs());
    }
    let hsl: Hsl = [h as u8, (s * 240.0) as u8, (l * 240.0) as u8];
    hsl
}

pub fn hsl2hex(pixel: Hsl) -> Hex {
    /*
    Convert from HSL to RGB
    where h is 0-239, s is 0-240, l is 0-240
    and the rgb values are 0-255
    */
    let (mut r, mut g, mut b): (f32, f32, f32);
    let (h, s, l) = (
        pixel[0] as f32,
        pixel[1] as f32 / 240.0,
        pixel[2] as f32 / 240.0,
    );

    let c: f32 = (1.0 - (2.0 * l - 1.0).abs()) * s as f32;
    let x: f32 = c * (1.0 - ((h / 40.0) % 2.0 - 1.0).abs()) as f32;
    let m: f32 = l - c / 2.0;

    (r, g, b) = match h {
        h if h < 40.0 => (c, x, 0.0),
        h if h < 80.0 => (x, c, 0.0),
        h if h < 120.0 => (0.0, c, x),
        h if h < 160.0 => (0.0, x, c),
        h if h < 200.0 => (x, 0.0, c),
        _ => (c, 0.0, x),
    };

    (r, g, b) = ((r + m) * 255.0, (g + m) * 255.0, (b + m) * 255.0);
    let value: Hex = rgb2hex(r as u8, g as u8, b as u8);
    value
}
