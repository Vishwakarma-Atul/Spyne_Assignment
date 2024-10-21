import os
from PIL import Image, ImageFilter

class Spyne:

    def create_background(self, wall_img, floor_img, floor_start_height=300):
        """
        Create a new image by pasting a wall image and a floor image together.
        
        Args:
            wall_img (PIL.Image): The wall image to be used.
            floor_img (PIL.Image): The floor image to be used.
            floor_start_height (int, optional): The height at which the floor image should be pasted onto the wall image. Defaults to 300.
        
        Returns:
            PIL.Image: The resulting image with the wall and floor combined.
        """
        # Create a new image with the same size as the wall
        result = Image.new('RGBA', wall_img.size, (0, 0, 0, 0))

        # Paste the floor starting from the floor_start_height on the wall
        result.paste(wall_img, (0, 0), wall_img)
        result.paste(floor_img, (0, floor_start_height), floor_img)

        return result


    def crop_to_car(self, car_image):
        """
        Crops the provided car image to the bounding box of the non-transparent area.
        
        Args:
            car_image (PIL.Image): The car image to be cropped.
        
        Returns:
            PIL.Image: The cropped car image.
        """
        # Get the alpha channel
        alpha = car_image.split()[-1]
        
        # Find the bounding box of the non-transparent area
        bbox = alpha.getbbox()
        cropped_car = car_image.crop(bbox)
        
        return cropped_car


    def process_car(self, car, mask):
        """
        Processes the provided car image by applying a mask to it and cropping it to the bounding box of the non-transparent area.
        
        Args:
            car (PIL.Image): The car image to be processed.
            mask (PIL.Image): The mask image to be applied to the car.
        
        Returns:
            PIL.Image: The processed car image with the mask applied and cropped to the bounding box.
        """

        mask = mask.convert('L')

        # Remove noise from mask
        mask = mask.filter(ImageFilter.MedianFilter(size=5))
        mask = mask.filter(ImageFilter.SMOOTH_MORE)

        car.putalpha(mask)
        
        return self.crop_to_car(car)


    def car_on_floor(self, car, background, car_xy=(0.5, 0.8), car_zoom=1.25, crop_xy = (0.5, 0.65), crop=1.25):
        """
        Pastes a car image onto a background image, with the car positioned on the floor and scaled to a specified size.
        
        Args:
            car (PIL.Image): The car image to be pasted onto the background.
            background (PIL.Image): The background image onto which the car will be pasted.
            car_xy (tuple, optional): A tuple of (x, y) coordinates specifying the position of the car on the floor, where x and y are between 0 and 1. Defaults to (0.5, 0.8).
            car_zoom (float, optional): The zoom factor to be applied to the car image. Defaults to 1.25.
            crop_xy (tuple, optional): A tuple of (x, y) coordinates specifying the center point of the cropped region of the background, where x and y are between 0 and 1. Defaults to (0.5, 0.65).
            crop (float, optional): The crop factor to be applied to the background image. Defaults to 1.25.
        
        Returns:
            PIL.Image: The resulting image with the car pasted onto the background.
        """
        # Get background dimensions
        bg_w, bg_h = background.size

        # Crop the region of the background (crop effect)
        x_center = int(bg_w*crop_xy[0])
        y_center = int(bg_h*crop_xy[1])
        _w = bg_w//crop//2
        _h = bg_h//crop//2

        left = max(0, x_center-_w)
        top = max(0, y_center-_h)
        right = min(bg_w, x_center+_w)
        bottom =  min(bg_h, y_center+_h)

        result = background.crop((left, top, right, bottom))
        
        # car_size_scaled = int(car.width*car_zoom), int(car.height*car_zoom)
        ## hardcoding car size and preserving aspect ratio.
        _h = 600
        _w = int(car.width/car.height*_h)
        car_size_scaled = int(_w*car_zoom), int(_h*car_zoom)
        
        car = car.resize(car_size_scaled, Image.LANCZOS)
        
        car_w, car_h = car.size    
        result_w, result_h = result.size
        
        # Calculate position for the car to sit on the floor
        car_x = (result_w - car_w) // 2  # Center horizontally on the floor
        car_y = int((result_h - car_h)*car_xy[1])

        # Paste the car onto the background
        result.paste(car, (car_x, car_y), car)  # Using 'car' as mask to keep transparency

        return result


    def process_image(self, car_image_path: str, mask_path: str, floor_path: str, wall_path:str, shadow_mask_path: str):
        """
        Processes an image by loading the necessary images, creating a background, processing the car, and placing the car on the floor.
        
        Args:
            car_image_path (str): The file path to the car image.
            mask_path (str): The file path to the car mask image.
            floor_path (str): The file path to the floor image.
            wall_path (str): The file path to the wall image.
            shadow_mask_path (str): The file path to the shadow mask image.
        
        Returns:
            PIL.Image: The resulting image with the car pasted onto the background.
        """
        # Load images
        car = Image.open(car_image_path)
        mask = Image.open(mask_path)
        floor = Image.open(floor_path)
        wall = Image.open(wall_path)
        # shadow_mask = Image.open(shadow_mask_path)
        
        background = self.create_background(wall, floor)
        car_processed = self.process_car(car, mask)
        car_with_new_bg = self.car_on_floor(car_processed, background)
        
        return car_with_new_bg


def main(data: list[dict]):
    spyne = Spyne()
    for i, each in enumerate(data):
        result = spyne.process_image(
            each['car'],
            each['mask'],
            each['floor'],
            each['wall'],
            each['shadow_mask']
        )
        print(f"Processed {each['car']} image")
        # Save the result
        name =  each['car'].split('/')[-1].split('.')[0]
        os.makedirs('result', exist_ok=True)
        result.save(f"result/{name}.png", format='PNG')

if __name__ == "__main__":
    data = [
        {
            'car': 'images/1.jpeg',
            'mask': 'car_masks/1.png',
            'floor': 'floor.png',
            'wall': 'wall.png',
            'shadow_mask': 'shadow_masks/1.png'
        },
        {
            'car': 'images/2.jpeg',
            'mask': 'car_masks/2.png',
            'floor': 'floor.png',
            'wall': 'wall.png',
            'shadow_mask': 'shadow_masks/2.png'
        },
        {
            'car': 'images/3.jpeg',
            'mask': 'car_masks/3.png',
            'floor': 'floor.png',
            'wall': 'wall.png',
            'shadow_mask': 'shadow_masks/3.png'
        },
        {
            'car': 'images/4.jpeg',
            'mask': 'car_masks/4.png',
            'floor': 'floor.png',
            'wall': 'wall.png',
            'shadow_mask': 'shadow_masks/4.png'
        },
        {
            'car': 'images/5.jpeg',
            'mask': 'car_masks/5.png',
            'floor': 'floor.png',
            'wall': 'wall.png',
            'shadow_mask': 'shadow_masks/5.png'
        },
        {
            'car': 'images/6.jpeg',
            'mask': 'car_masks/6.png',
            'floor': 'floor.png',
            'wall': 'wall.png',
            'shadow_mask': 'shadow_masks/6.png'
        },
        # Add more image sets here
    ]
    main(data)
    print("All images processed!")
