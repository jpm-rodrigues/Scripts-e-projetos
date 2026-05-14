import os
from PIL import Image
import sys

def inspect_images():
    base_dir = "/home/jpmr/Desktop/AI test/Rolê/Tecno Duro/Teste composição de fotos"
    bg_path = os.path.join(base_dir, "background")
    
    try:
        bg = Image.open(bg_path)
        print(f"Background: {bg.format}, Size: {bg.size}, Mode: {bg.mode}")
    except Exception as e:
        print(f"Error opening background: {e}")
        return

    # Check one jpg
    jpg_files = [f for f in os.listdir(base_dir) if f.lower().endswith('.jpg')]
    if jpg_files:
        first_jpg = os.path.join(base_dir, jpg_files[0])
        try:
            img = Image.open(first_jpg)
            print(f"Sample JPG: {img.format}, Size: {img.size}, Mode: {img.mode}")
        except Exception as e:
            print(f"Error opening jpg: {e}")

if __name__ == "__main__":
    inspect_images()
