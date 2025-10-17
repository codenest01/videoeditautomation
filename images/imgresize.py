import os
import glob
from PIL import Image
from multiprocessing import Pool, cpu_count
from functools import partial
import time

# --- Configuration ---
# Your main folder where images are located
INPUT_DIR = r"C:\Users\Mr_robot\Desktop\Image_resize" 

# The folder to save the resized images. It will be created if it doesn't exist.
OUTPUT_DIR = os.path.join(INPUT_DIR, "resized_images")

# The new size for the images (width, height)
# *** UPDATED SIZE HERE ***
NEW_SIZE = (1280, 720) 

# --- Resizing Function (MODIFIED) ---

def resize_image(image_path, output_dir, new_size):
    """
    Loads a single image, scales it to cover the new size while maintaining 
    aspect ratio, crops the excess, and saves it.
    """
    try:
        # 1. Open the image
        img = Image.open(image_path)
        original_width, original_height = img.size
        target_width, target_height = new_size

        # Calculate target aspect ratio
        target_aspect_ratio = target_width / target_height

        # Get the original file name and extension
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)

        # --- New Cropping Logic ---

        # 2. Determine the best scale factor
        # The scale must be large enough so that *both* dimensions meet or exceed the target.
        # This prevents "zooming out" and maintains the aspect ratio.
        scale_w = target_width / original_width
        scale_h = target_height / original_height
        
        # Use the larger scale factor (to ensure the smaller dimension covers the target)
        scale_factor = max(scale_w, scale_h)

        # Calculate the new dimensions after scaling
        new_w = int(original_width * scale_factor)
        new_h = int(original_height * scale_factor)

        # 3. Resize the image (intermediate step)
        # Use Image.LANCZOS for high-quality resampling
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # 4. Calculate the crop box (center crop)
        # We now have an image that is bigger than (1280, 720) in at least one dimension.
        # We need to find the coordinates for a centered crop.
        
        # Calculate the top-left coordinate for the crop box
        left = (new_w - target_width) // 2
        top = (new_h - target_height) // 2
        
        # Calculate the bottom-right coordinate for the crop box
        right = left + target_width
        bottom = top + target_height

        # Ensure we have whole numbers for the crop box
        crop_box = (left, top, right, bottom)
        
        # 5. Crop the image
        resized_img = img.crop(crop_box)
        
        # --- End New Cropping Logic ---

        # 6. Save the resized and cropped image
        output_path = os.path.join(output_dir, f"{name}_cropped{ext}") 
        
        # Determine the save format based on the original extension
        save_format = 'JPEG' if ext.lower() in ['.jpg', '.jpeg'] else ext[1:].upper()
        
        # For JPEGs, set a reasonable quality (95 is high quality)
        if save_format == 'JPEG':
            resized_img.save(output_path, format=save_format, quality=95)
        else:
            resized_img.save(output_path, format=save_format)
        
        return f"SUCCESS: {filename}"

    except Exception as e:
        return f"FAILURE: {image_path} - Error: {e}"

# --- Main Execution (Unchanged) ---

if __name__ == '__main__':
    start_time = time.time()
    
    # 1. Create the output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 2. Find all image files
    image_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(glob.glob(os.path.join(INPUT_DIR, f"**/*.{ext}"), recursive=True))
        image_paths.extend(glob.glob(os.path.join(INPUT_DIR, f"**/*.{ext.upper()}"), recursive=True))

    if not image_paths:
        print(f"No images found in: {INPUT_DIR}")
    else:
        print(f"Found {len(image_paths)} images to process.")
        
        # 3. Prepare the function for multiprocessing
        worker_func = partial(resize_image, output_dir=OUTPUT_DIR, new_size=NEW_SIZE)
        
        # 4. Create a Pool of worker processes
        num_processes = cpu_count()
        print(f"Starting multiprocessing pool with {num_processes} processes...")
        
        with Pool(processes=num_processes) as pool:
            # Use pool.imap_unordered for immediate result printing, or pool.map for simpler block
            results = pool.map(worker_func, image_paths) 

        # 5. Report results
        total_time = time.time() - start_time
        successful_count = sum(1 for res in results if res.startswith("SUCCESS"))
        
        print("\n--- Summary ---")
        print(f"Total Images Found: {len(image_paths)}")
        print(f"Images Successfully Resized: {successful_count}")
        print(f"Resized images saved to: {OUTPUT_DIR}")
        print(f"All images are resized to {NEW_SIZE[0]}x{NEW_SIZE[1]} pixels using a **center-crop** method.")
        print(f"Total time taken: {total_time:.2f} seconds 🚀")