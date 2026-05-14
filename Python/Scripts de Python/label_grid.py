from PIL import Image, ImageDraw, ImageFont, ImageFile
import os

ImageFile.LOAD_TRUNCATED_IMAGES = True

def label_image(image_path, output_path, rows=3, cols=3):
    try:
        img = Image.open(image_path)
        
        # Handle transparency: Keep RGBA if present, otherwise convert to RGB
        if img.mode not in ('RGBA', 'RGB'):
            img = img.convert('RGB')
            
        w, h = img.size
        draw = ImageDraw.Draw(img)

        cell_w = w / cols
        cell_h = h / rows

        # Dynamic sizing
        # Use image width for consistent size across different grid types (2x2 vs 3x3)
        # 3x3 cell is w/3. Previous logic was 0.08 * (w/3) ~= 0.026 * w.
        # We'll use 0.027 * w to keep it similar to the 3x3 look.
        radius = w * 0.027
        margin_x = radius * 1.5 
        margin_y = radius * 1.5 
        font_size = int(radius * 1.2)

        try:
            # Attempt to use a bold font, fallback to default if not found
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
            ]
            font = None
            for fp in font_paths:
                if os.path.exists(fp):
                    font = ImageFont.truetype(fp, font_size)
                    break
            if font is None:
                 print("Bold font not found, using default.")
                 font = ImageFont.load_default()

        except IOError:
            print("Font error, using default.")
            font = ImageFont.load_default()

        labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c
                if idx >= len(labels):
                    break
                
                label = labels[idx]
                
                # Cell top-left coordinates
                cell_x = c * cell_w
                cell_y = r * cell_h
                
                # Circle center (Bottom Left)
                center_x = cell_x + margin_x
                center_y = (cell_y + cell_h) - margin_y

                # Check for transparency at the center of where the label would be
                if img.mode == 'RGBA':
                    # Sample a few points around the label area to ensure we don't label empty space
                    # We'll check the center and maybe a bit around it.
                    # Simple check: Pixel at center_x, center_y
                    try:
                        # Ensure coordinates are within bounds
                        check_x = min(int(center_x), w - 1)
                        check_y = min(int(center_y), h - 1)
                        pixel = img.getpixel((check_x, check_y))
                        if pixel[3] < 10: # Alpha channel is the 4th element (index 3)
                             print(f"Skipping label {label} at ({r},{c}) due to transparency.")
                             continue
                    except Exception as e:
                        print(f"Could not check transparency for {label}: {e}")

                
                # Draw circle (bounding box)
                bbox = [
                    center_x - radius, 
                    center_y - radius, 
                    center_x + radius, 
                    center_y + radius
                ]
                draw.ellipse(bbox, fill="white", outline="white")
                
                # Draw text
                try:
                     # Use anchor="mm" for middle-middle alignment if available (Pillow >= 8.0.0)
                    draw.text((center_x, center_y), label, fill="black", font=font, anchor="mm")
                except ValueError:
                    # Fallback for older Pillow versions
                    w_text, h_text = draw.textsize(label, font=font)
                    draw.text((center_x - w_text/2, center_y - h_text/2), label, fill="black", font=font)

        img.save(output_path)
        print(f"Successfully saved to {output_path}")

    except Exception as e:
        print(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    tasks = [
        {
            "input": "/home/jpmr/Desktop/AI test/Coisa naj/Prancha naj.png",
            "output": "/home/jpmr/Desktop/AI test/Coisa naj/Prancha naj_labeled.png",
            "rows": 3,
            "cols": 3
        },
        {
            "input": "/home/jpmr/Desktop/AI test/pranchas/radula got/RADGOT.png",
            "output": "/home/jpmr/Desktop/AI test/pranchas/radula got/RADGOT_labeled.png",
            "rows": 2,
            "cols": 2
        },
        {
            "input": "/home/jpmr/Desktop/AI test/pranchas/outra rad/OUTRA RADS.png",
            "output": "/home/jpmr/Desktop/AI test/pranchas/outra rad/OUTRA RADS_labeled.png",
            "rows": 2,
            "cols": 2
        },
        {
            "input": "/home/jpmr/Desktop/AI test/pranchas/plag/prancha_plag.png",
            "output": "/home/jpmr/Desktop/AI test/pranchas/plag/prancha_plag_labeled.png",
            "rows": 1, 
            "cols": 3
        },
        {
            "input": "/home/jpmr/Desktop/AI test/pranchas/Prancha rads juntas.png",
            "output": "/home/jpmr/Desktop/AI test/pranchas/Prancha rads juntas_labeled.png",
            "rows": 3,
            "cols": 2
        },
        {
            "input": "/home/jpmr/Desktop/AI test/pranchas/Fotos das localidades.png",
            "output": "/home/jpmr/Desktop/AI test/pranchas/Fotos das localidades_labeled.png",
            "rows": 1,
            "cols": 3
        },
        {
            "input": "/home/jpmr/Desktop/AI test/Coisa naj/Filogenia/Prancha rads juntas.png",
            "output": "/home/jpmr/Desktop/AI test/Coisa naj/Filogenia/Prancha rads juntas_labeled.png",
            "rows": 3,
            "cols": 2
        }
    ]

    for task in tasks:
        if os.path.exists(task["input"]):
             label_image(task["input"], task["output"], rows=task["rows"], cols=task["cols"])
        else:
            print(f"Input file not found: {task['input']}")
