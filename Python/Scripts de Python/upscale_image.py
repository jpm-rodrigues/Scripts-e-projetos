
import cv2
import sys
import os
import numpy as np

def upscale_image(input_path, output_path, scale=4):
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    print(f"Loading image from {input_path}...")
    img = cv2.imread(input_path)
    if img is None:
        print("Error: Failed to load image.")
        return

    h, w = img.shape[:2]
    new_dim = (w * scale, h * scale)
    
    print(f"Upscaling from {w}x{h} to {new_dim[0]}x{new_dim[1]} using Lanczos4 interpolation...")
    
    # Use Lanczos4 which is generally best for upscaling
    upscaled = cv2.resize(img, new_dim, interpolation=cv2.INTER_LANCZOS4)
    
    # Optional: Apply some sharpening to counter blur
    print("Applying sharpening filter...")
    # Create a sharpening kernel
    # Simple sharpening
    kernel = np.array([[-1,-1,-1], 
                       [-1, 9,-1], 
                       [-1,-1,-1]])
    
    # Apply the sharpening kernel
    sharpened = cv2.filter2D(upscaled, -1, kernel)
    
    # Mix original upscaled and sharpened to avoid too much noise? 
    # Let's just use the sharpened one but maybe blend it if it's too harsh.
    # For now, pure sharpened.
    
    print(f"Saving upscaled image to {output_path}...")
    cv2.imwrite(output_path, sharpened)
    print("Done!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python upscale_image.py <input_image> <output_image> [scale]")
    else:
        input_img = sys.argv[1]
        output_img = sys.argv[2]
        scale = int(sys.argv[3]) if len(sys.argv) > 3 else 4
        upscale_image(input_img, output_img, scale=scale)
