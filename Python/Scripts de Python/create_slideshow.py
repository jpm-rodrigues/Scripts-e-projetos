import subprocess
import os

def create_slideshow():
    # File names based on previous list_dir
    images = [
        "IMG_20250225_074637.jpg",
        "IMG_20250225_074637_1.jpg",
        "IMG_20250225_074639.jpg"
    ]
    
    output_file = "slideshow.mp4"
    
    # Settings
    img_duration = 4
    fade_duration = 1
    
    # Build inputs
    inputs = []
    for img in images:
        inputs.extend(["-loop", "1", "-t", str(img_duration), "-i", img])
        
    # Build filter complex
    # We need to scale images to the same size first to avoid errors
    # We'll use 1920x1080 as the target resolution
    
    filter_parts = []
    
    # Scale and pad each input
    for i in range(len(images)):
        filter_parts.append(f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v{i}]")
        
    # Chain xfades
    # [v0][v1]xfade...[x1]
    # [x1][v2]xfade...[x2]
    
    current_stream = "v0"
    offset = img_duration - fade_duration
    
    for i in range(1, len(images)):
        next_stream = f"v{i}"
        out_stream = f"x{i}" if i < len(images) - 1 else "out"
        
        filter_parts.append(f"[{current_stream}][{next_stream}]xfade=transition=fade:duration={fade_duration}:offset={offset}[{out_stream}]")
        
        current_stream = out_stream
        offset += (img_duration - fade_duration)
        
    filter_complex = ";".join(filter_parts)
    
    # Full command
    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex, "-map", f"[{current_stream}]", "-c:v", "libx264", "-pix_fmt", "yuv420p", output_file]
    
    print("Running command:", " ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Successfully created {output_file}")
    except subprocess.CalledProcessError as e:
        print("Error creating slideshow:", e)

if __name__ == "__main__":
    create_slideshow()
