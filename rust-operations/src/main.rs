// Open image file in memory
use std::{io::{Read}, path::Path};
use std::fs::File;

use image::{DynamicImage};
struct Bedit {
    img: DynamicImage,
}
#[allow(dead_code)]
impl Bedit {
    pub fn get_dimensions(&self) -> (u32, u32) {
        (self.img.width(), self.img.height())
    }
    pub fn get_pixel(&self, x: u32, y: u32) -> image::Rgb<u8> {
        self.img.as_rgb8().unwrap().get_pixel(x, y).to_owned()
    }
    pub fn set_pixel(&mut self, x: u32, y: u32, pixel: image::Rgb<u8>) {
        self.img.as_mut_rgb8().unwrap().put_pixel(x, y, pixel);
    }
    pub fn save(&self, path: &Path) {
        self.img.save(path).unwrap();
    }
    pub fn load(path: &Path) -> Bedit {
        Bedit {
            img: image::open(path).unwrap(),
        }
    }
    pub fn grayscale(&mut self) -> DynamicImage {
        let mut new_img = image::ImageBuffer::new(self.img.width(), self.img.height());
        for x in 0..self.img.width() {
            for y in 0..self.img.height() {
                let pixel = self.img.as_rgb8().unwrap().get_pixel(x, y);
                let gray = (pixel[0] as f32 + pixel[1] as f32 + pixel[2] as f32) / 3.0;
                let new_pixel = image::Rgb([gray as u8, gray as u8, gray as u8]);
                new_img.put_pixel(x, y, new_pixel);
            }
        }
        DynamicImage::ImageRgb8(new_img)
    }
    pub fn filter3x3(&mut self, filter: &[f32; 9]) -> DynamicImage {
        let (width, height) = self.get_dimensions();
        let mut new_img = image::ImageBuffer::new(width, height);
        
        for x in 1..width - 1 {
            for y in 1..height - 1 {
                let mut new_pixel = [0.0f32; 3];
                for i in 0..9 {
                    let x_ = x + (i % 3) - 1;
                    let y_ = y + (i / 3) - 1;
                    let pixel_ = self.get_pixel(x_, y_);
                    new_pixel[0] += pixel_[0] as f32 * filter[i as usize];
                    new_pixel[1] += pixel_[1] as f32 * filter[i as usize];
                    new_pixel[2] += pixel_[2] as f32 * filter[i as usize];
                }
                let new_pixel = image::Rgb([new_pixel[0].round() as u8, new_pixel[1].round() as u8, new_pixel[2].round() as u8]);
                new_img.put_pixel(x, y, new_pixel);
            }
        }
        DynamicImage::ImageRgb8(new_img)
    }
    fn mean_filter(&mut self) -> DynamicImage {
        let filter = &[1.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0];
        self.filter3x3(filter)
    }
    pub fn median(&mut self, filter: &[f32; 9]) -> DynamicImage {
        
        let (width, height) = self.get_dimensions();
        let mut new_img = image::ImageBuffer::new(width, height);
        
        for x in 1..width - 1 {
            for y in 1..height - 1 {
                let mut new_pixel = [0.0f32; 3];
                for i in 0..9 {
                    let x_ = x + (i % 3) - 1;
                    let y_ = y + (i / 3) - 1;
                    let pixel_ = self.get_pixel(x_, y_);
                    new_pixel[0] += pixel_[0] as f32 * filter[i as usize];
                    new_pixel[1] += pixel_[1] as f32 * filter[i as usize];
                    new_pixel[2] += pixel_[2] as f32 * filter[i as usize];
                }
                let new_pixel = image::Rgb([new_pixel[0].round() as u8, new_pixel[1].round() as u8, new_pixel[2].round() as u8]);
                new_img.put_pixel(x, y, new_pixel);
            }
        }
        DynamicImage::ImageRgb8(new_img)
    fn sobel_filter(&mut self) -> DynamicImage {
        let filterx = [-1.0 / 4.0, 0.0, 1.0 / 4.0,
                                 -2.0 / 4.0, 0.0, 2.0 / 4.0,
                                 -1.0 / 4.0, 0.0, 1.0 / 4.0];
        let filtery = [-1.0 / 4.0, -2.0 / 4.0, -1.0 / 4.0,
                                  0.0, 0.0, 0.0,
                                  1.0 / 4.0,  2.0 / 4.0,  1.0 / 4.0];
        let sobel_x = self.filter3x3(&filterx);
        let sobel_y = self.filter3x3(&filtery);

        let mut sobel = DynamicImage::new_rgb8(self.img.width(), self.img.height());
        
        for x in 0..self.img.width() {
            for y in 0..self.img.height() {

                let sobel_x_ = sobel_x.as_rgb8().unwrap().get_pixel(x, y);
                let sobel_y_ = sobel_y.as_rgb8().unwrap().get_pixel(x, y);
                
                let mut new_pixel = image::Rgb([0, 0, 0]);
                for z in 0..3 {
                    let magnitude = (sobel_x_[z] as f32 * sobel_x_[z] as f32 + sobel_y_[z] as f32 * sobel_y_[z] as f32).sqrt();
                    new_pixel[z] = magnitude as u8;
                }
                sobel.as_mut_rgb8().unwrap().put_pixel(x, y, new_pixel);
            }
        }   
        sobel
    }
}

fn main() {
    let path = Path::new("./../resources/lena.jpg");
    let image = read_image(path).expect("Could not open image");
    let mut bedit = Bedit { img: image };
    let grayscale = bedit.grayscale();
    grayscale.save(&Path::new("grayscale.png")).expect("Could not save image");
    bedit.sobel_filter();
    
}
pub fn read_image(path: &Path) -> image::ImageResult<image::DynamicImage> {
    let mut file = File::open(path)?;
    let mut buf = vec![];
    file.read_to_end(&mut buf)?;
    Ok(image::load_from_memory(&buf)?)
}