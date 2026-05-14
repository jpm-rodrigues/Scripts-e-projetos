import subprocess
import os

def create_slideshow():
    # Directory containing the composite images
    image_dir = "/home/jpmr/Desktop/AI test/Rolê/Tecno Duro/Teste composição de fotos/composites"
    
    # List and sort images
    images = sorted([
        os.path.join(image_dir, f) 
        for f in os.listdir(image_dir) 
        if f.endswith('.jpg')
    ])
    
    # Settings
    hold_duration = 0.5
    
    inputs = []
    for img in images:
        # -loop 1 -t 0.5 -i img
        inputs.extend(["-loop", "1", "-t", str(hold_duration), "-i", img])
        
    filter_parts = []
    
    # Scale and prepare for concat
    for i in range(len(images)):
        # Scale to 1920x1080 and set SAR to 1 to ensure compatibility
        filter_parts.append(f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v{i}]")
        
    # Concat all streams
    # [v0][v1]...[vn]concat=n=N:v=1:a=0[out]
    input_labels = "".join([f"[v{i}]" for i in range(len(images))])
    concat_filter = f"{input_labels}concat=n={len(images)}:v=1:a=0[out]"
    
    filter_complex = ";".join(filter_parts) + ";" + concat_filter

    # Output 1: AVI (MPEG-4)
    output_avi = "slideshow.avi"
    cmd_avi = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex, "-map", "[out]", 
           "-c:v", "mpeg4", "-q:v", "3", 
           output_avi]
    
    print("Running command for AVI:", " ".join(cmd_avi))
    try:
        subprocess.run(cmd_avi, check=True)
        print(f"Successfully created {output_avi}")
    except subprocess.CalledProcessError as e:
        print("Error creating AVI:", e)

    # Output 2: GIF
    # For GIF we need to generate a palette first for best quality, but for simple slideshows we can just output.
    # We'll use a split filter to generate palette and map it.
    output_gif = "slideshow.gif"
    
    # We need a slightly different filter complex for GIF to include palette generation if we want high quality,
    # but let's try a simple direct output first to keep it robust.
    # Actually, let's just run a second command using the AVI as input to save processing time/complexity
    
    cmd_gif = ["ffmpeg", "-y", "-i", output_avi, "-vf", "fps=10,scale=750:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse", output_gif]
    
    print("Running command for GIF:", " ".join(cmd_gif))
    try:
        subprocess.run(cmd_gif, check=True)
        print(f"Successfully created {output_gif}")
    except subprocess.CalledProcessError as e:
        print("Error creating GIF:", e)
    
    print("Running command:", " ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Successfully created {output_file}")
    except subprocess.CalledProcessError as e:
        print("Error creating slideshow:", e)

if __name__ == "__main__":
    create_slideshow()
