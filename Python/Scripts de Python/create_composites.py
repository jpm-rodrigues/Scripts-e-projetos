import os
from PIL import Image, ImageOps
import numpy as np

def adjust_levels(img, target_black=(0,0,0)):
    # Convert to numpy array
    arr = np.array(img).astype(float)
    
    # Find the black point (let's use the 1st percentile to be robust against noise)
    # We want to map the darkest parts to pure black (0,0,0)
    
    # Simple approach: subtract the minimum value found in the image
    # But we should do it per channel or global?
    # Usually global luminance is better to preserve color balance, but per-channel fixes color casts.
    # Let's try per-channel black point adjustment.
    
    for i in range(3): # R, G, B
        channel = arr[:,:,i]
        # Increase percentile to 15 to crush more shadows into black
        min_val = np.percentile(channel, 15) 
        # Shift so min_val becomes 0
        channel = (channel - min_val)
        # Rescale the remaining range to 0-255 to keep highlights bright
        # Avoid division by zero
        max_val = 255.0
        if np.max(channel) > 0:
            channel = channel * (255.0 / np.max(channel))
        
        channel = np.clip(channel, 0, 255)
        arr[:,:,i] = channel
        
    return Image.fromarray(arr.astype('uint8'))

def create_composites():
    base_dir = "/home/jpmr/Desktop/AI test/Rolê/Tecno Duro/Teste composição de fotos"
    output_dir = os.path.join(base_dir, "composites")
    os.makedirs(output_dir, exist_ok=True)
    
    bg_path = os.path.join(base_dir, "background")
    bg_orig = Image.open(bg_path).convert('RGB')
    
    # Target area
    # Based on previous analysis: x=236, width=514, height=422
    target_x = 236
    target_y = 0
    target_w = 514
    target_h = 422
    
    # List jpgs
    jpgs = sorted([f for f in os.listdir(base_dir) if f.lower().endswith('.jpg')])
    
    for f in jpgs:
        img_path = os.path.join(base_dir, f)
        img = Image.open(img_path).convert('RGB')
        
        # 1. Adjust levels
        img_adj = adjust_levels(img)
        
        # 2. Resize to fit in target area
        # We want to contain it, so we see the whole image
        # Or do we want to cover? "colocadas a direita" implies placing it there.
        # If the aspect ratio is different, we'll have black bars.
        # Since the background is black, that's perfect.
        
        img_adj.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
        
        # 3. Create composite
        comp = bg_orig.copy()
        
        # Center the image in the target area
        x_offset = target_x + (target_w - img_adj.width) // 2
        y_offset = target_y + (target_h - img_adj.height) // 2
        
        comp.paste(img_adj, (x_offset, y_offset))
        
        save_path = os.path.join(output_dir, f"comp_{f}")
        comp.save(save_path)
        print(f"Saved {save_path}")

if __name__ == "__main__":
    create_composites()
