from PIL import Image
import os
import numpy as np

def analyze_background():
    base_dir = "/home/jpmr/Desktop/AI test/Rolê/Tecno Duro/Teste composição de fotos"
    bg_path = os.path.join(base_dir, "background")
    
    bg = Image.open(bg_path).convert('RGB')
    width, height = bg.size
    
    # Convert to numpy array for easier analysis
    arr = np.array(bg)
    
    # Check the rightmost column to see what "black" looks like
    right_col = arr[:, -1, :]
    avg_color = np.mean(right_col, axis=0)
    print(f"Average color of rightmost column: {avg_color}")
    
    # Find where the "black" area starts from the right
    # We'll scan the middle row
    mid_y = height // 2
    row = arr[mid_y, :, :]
    
    # Threshold for "blackness" - let's say variance from the rightmost pixel is small
    target_color = row[-1]
    print(f"Target black color (from middle-right pixel): {target_color}")
    
    # Scan from right to left
    split_x = width
    for x in range(width - 1, -1, -1):
        pixel = row[x]
        # Simple distance check
        dist = np.linalg.norm(pixel - target_color)
        if dist > 10: # Tolerance
            split_x = x + 1
            break
            
    print(f"Detected split point x: {split_x}")
    print(f"Black area width: {width - split_x}")
    
    return split_x, target_color

if __name__ == "__main__":
    analyze_background()
