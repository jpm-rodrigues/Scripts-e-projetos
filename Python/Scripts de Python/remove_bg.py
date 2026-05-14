
import cv2
import numpy as np
import sys

def remove_background(input_path, output_path):
    # Load the image
    img = cv2.imread(input_path)
    if img is None:
        print(f"Error: Could not load image from {input_path}")
        return

    # Convert to BGRA (adds alpha channel)
    img_bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    # Strategy 1: Assume background is light/white (common for documents)
    # Convert to grayscale to check brightness
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Create a mask: pixels that are very light (background)
    # Adjust threshold as needed. 240 is usually safe for white backgrounds.
    # If the background is a solid color (e.g. blue), this needs a different approach.
    
    # improved strategy: floodFill from corners to identify background
    # Create a mask for floodFill
    h, w = img.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    
    # We will flood fill from (0,0) and other corners slightly to find the background
    # Use a lo_diff and up_diff to tolerate small JPEG/anti-aliasing noise
    flood_flags = 4 | cv2.FLOODFILL_FIXED_RANGE | cv2.FLOODFILL_MASK_ONLY | (255 << 8)
    
    # Check corners
    corners = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1)]
    
    # We'll use a copy for floodfilling to separate "background" identification
    # But actually, we need to mark these pixels in the alpha channel.
    
    # Let's perform floodFill on a temporary mask to identify background pixels
    # We assume the background touches the corners.
    
    # Initial mask is all 0.
    # We want 1s where background is.
    
    # Note: openCV floodFill updates the image or mask. 
    # With FLOODFILL_MASK_ONLY, it updates the mask (which is 2 pixels larger)
    
    # Tolerance for background color variation
    diff = (30, 30, 30) 
    
    processed_mask = np.zeros((h+2, w+2), np.uint8)
    
    # Floodfill from variable locations if corners match
    mean_corner_color = np.mean([img[0,0], img[0, w-1], img[h-1, 0], img[h-1, w-1]], axis=0)
    
    start_points = [(0,0), (w-1,0), (0, h-1), (w-1, h-1), (w//2, 0), (w//2, h-1), (0, h//2), (w-1, h//2)]
    
    for x, y in start_points:
         # Check if this point has been filled yet in the mask (mask[y+1, x+1])
         if processed_mask[y+1, x+1] == 0:
             # Basic check: is it close to the "mean" corner color? Or just consistent with itself?
             # For safety, just fill.
             cv2.floodFill(img, processed_mask, (x, y), (0,0,0), diff, diff, flood_flags)

    # processed_mask now has 255 where the background is (shifted by 1 pixel)
    # Resize/crop mask to image size
    bg_mask = processed_mask[1:-1, 1:-1]
    
    # Where bg_mask is 255, set alpha to 0
    img_bgra[bg_mask == 255, 3] = 0
    
    cv2.imwrite(output_path, img_bgra)
    print(f"Saved background-removed image to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python remove_bg.py <input> <output>")
    else:
        remove_background(sys.argv[1], sys.argv[2])
