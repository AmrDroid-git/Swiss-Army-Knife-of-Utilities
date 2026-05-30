import os
import sys
from PIL import Image

def split_image(image_path):
    if not os.path.exists(image_path):
        print(f"Error: The file '{image_path}' was not found.")
        return

    try:
        with Image.open(image_path) as img:
            width, height = img.size
            mid = width // 2
            
            # Define crop areas: (left, upper, right, lower)
            left_half = img.crop((0, 0, mid, height))
            right_half = img.crop((mid, 0, width, height))
            
            # Generate output filenames
            base, ext = os.path.splitext(image_path)
            left_name = f"{base}_part1{ext}"
            right_name = f"{base}_part2{ext}"
            
            # Save the results
            left_half.save(left_name)
            right_half.save(right_name)
            
            print(f"Done! Split into:\n- {left_name}\n- {right_name}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Check if the user provided an argument
    if len(sys.argv) < 2:
        print("Usage: python split_image.py <path_to_image>")
    else:
        # sys.argv[1] grabs the first argument passed after the script name
        split_image(sys.argv[1])