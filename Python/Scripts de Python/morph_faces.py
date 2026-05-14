import cv2
import numpy as np
import mediapipe as mp
import sys
import os

def get_landmarks(image_path):
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read {image_path}")
        return None, None
    
    results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    if not results.multi_face_landmarks:
        print(f"No face detected in {image_path}")
        return None, image
        
    landmarks = []
    h, w, _ = image.shape
    for point in results.multi_face_landmarks[0].landmark:
        landmarks.append((int(point.x * w), int(point.y * h)))
        
    # Add corners and midpoints to ensure full image warp
    landmarks.extend([(0, 0), (w//2, 0), (w-1, 0), (0, h//2), (w-1, h//2), (0, h-1), (w//2, h-1), (w-1, h-1)])
    
    return landmarks, image

def apply_affine_transform(src, src_tri, dst_tri, size):
    warp_mat = cv2.getAffineTransform(np.float32(src_tri), np.float32(dst_tri))
    dst = cv2.warpAffine(src, warp_mat, (size[0], size[1]), None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    return dst

def morph_triangle(img1, img2, img, t1, t2, t, alpha):
    # Find bounding rectangle for each triangle
    r1 = cv2.boundingRect(np.float32([t1]))
    r2 = cv2.boundingRect(np.float32([t2]))
    r = cv2.boundingRect(np.float32([t]))

    # Offset points by left top corner of the respective rectangles
    t1_rect = []
    t2_rect = []
    t_rect = []

    for i in range(0, 3):
        t_rect.append(((t[i][0] - r[0]), (t[i][1] - r[1])))
        t1_rect.append(((t1[i][0] - r1[0]), (t1[i][1] - r1[1])))
        t2_rect.append(((t2[i][0] - r2[0]), (t2[i][1] - r2[1])))

    # Get mask by filling triangle
    mask = np.zeros((r[3], r[2], 3), dtype=np.float32)
    cv2.fillConvexPoly(mask, np.int32(t_rect), (1.0, 1.0, 1.0), 16, 0)

    # Apply warpImage to small rectangular patches
    img1_rect = img1[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
    img2_rect = img2[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]]

    size = (r[2], r[3])
    warp_img1 = apply_affine_transform(img1_rect, t1_rect, t_rect, size)
    warp_img2 = apply_affine_transform(img2_rect, t2_rect, t_rect, size)

    # Alpha blend rectangular patches
    img_rect = (1.0 - alpha) * warp_img1 + alpha * warp_img2

    # Copy triangular region of the rectangular patch to the output image
    img[r[1]:r[1]+r[3], r[0]:r[0]+r[2]] = img[r[1]:r[1]+r[3], r[0]:r[0]+r[2]] * (1 - mask) + img_rect * mask

def main():
    if len(sys.argv) < 3:
        print("Usage: python morph_faces.py <image1> <image2>")
        sys.exit(1)

    filename1 = sys.argv[1]
    filename2 = sys.argv[2]
    
    # Load landmarks
    points1, img1 = get_landmarks(filename1)
    points2, img2 = get_landmarks(filename2)
    
    if points1 is None or points2 is None:
        print("Could not detect faces in one or both images. Falling back to simple cross-dissolve.")
        # Fallback logic could go here, but for now we exit or just do simple blend
        # Let's resize to match
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
        # Simple cross dissolve video
        out = cv2.VideoWriter('morph_output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (img1.shape[1], img1.shape[0]))
        for alpha in np.linspace(0, 1, 60):
            blended = cv2.addWeighted(img1, 1-alpha, img2, alpha, 0)
            out.write(blended)
        out.release()
        print("Saved simple cross-dissolve to morph_output.mp4")
        return

    # Resize img2 to match img1 dimensions if needed, but landmarks need to be scaled
    # Actually, better to resize images to same size FIRST before detecting landmarks?
    # But we already detected. Let's just resize img2 to img1 and re-detect or scale points.
    # For simplicity, let's assume they are similar or we resize img2 to img1.
    
    # Load img2 original
    img2_orig = cv2.imread(filename2)
    if img2_orig is None:
        print(f"Error: Could not read {filename2}")
        return

    # Detect landmarks on ORIGINAL img2 to avoid distortion issues
    points2_orig, _ = get_landmarks(filename2)
    
    if points2_orig is None:
        print("Could not detect face in image 2 (original). Using cross-dissolve.")
        # Resize for cross dissolve
        img2 = cv2.resize(img2_orig, (img1.shape[1], img1.shape[0]))
        
        # Simple cross dissolve video
        out = cv2.VideoWriter('morph_output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (img1.shape[1], img1.shape[0]))
        for alpha in np.linspace(0, 1, 60):
            blended = cv2.addWeighted(img1, 1-alpha, img2, alpha, 0)
            out.write(blended)
        out.release()
        print("Saved simple cross-dissolve to morph_output.mp4")
        return

    # Now resize img2 to match img1
    h, w = img1.shape[:2]
    h2_orig, w2_orig = img2_orig.shape[:2]
    img2 = cv2.resize(img2_orig, (w, h))
    
    # Scale points from orig img2 to resized img2
    points2 = []
    scale_x = w / w2_orig
    scale_y = h / h2_orig
    
    # The last 8 points are corners/midpoints added by get_landmarks, we should re-add them for the new size
    # instead of scaling them, to be safe and exact.
    # get_landmarks returns 468 face points + 8 boundary points = 476 points.
    # Let's scale the first 468 points.
    
    for i in range(len(points2_orig) - 8):
        px, py = points2_orig[i]
        points2.append((int(px * scale_x), int(py * scale_y)))
        
    # Add boundary points for the NEW size
    points2.extend([(0, 0), (w//2, 0), (w-1, 0), (0, h//2), (w-1, h//2), (0, h-1), (w//2, h-1), (w-1, h-1)])

    # Delaunay triangulation
    rect = (0, 0, w, h)
    subdiv = cv2.Subdiv2D(rect)
    
    # Use average points for triangulation to avoid skinny triangles
    points_avg = []
    for i in range(len(points1)):
        x = (points1[i][0] + points2[i][0]) / 2
        y = (points1[i][1] + points2[i][1]) / 2
        points_avg.append((x, y))
        subdiv.insert((x, y))
        
    triangle_indices = []
    triangle_list = subdiv.getTriangleList()
    
    # Map triangle vertices to indices in points list
    for t in triangle_list:
        pt = [(t[0], t[1]), (t[2], t[3]), (t[4], t[5])]
        ind = []
        for j in range(3):
            for k in range(len(points_avg)):
                if abs(pt[j][0] - points_avg[k][0]) < 1.0 and abs(pt[j][1] - points_avg[k][1]) < 1.0:
                    ind.append(k)
                    break
        if len(ind) == 3:
            triangle_indices.append(ind)

    # Generate Morph Animation
    out = cv2.VideoWriter('morph_output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (w, h))
    
    for alpha in np.linspace(0, 1, 60): # 3 seconds at 20fps
        img_morph = np.zeros(img1.shape, dtype=img1.dtype)
        
        points_morph = []
        for i in range(len(points1)):
            x = (1 - alpha) * points1[i][0] + alpha * points2[i][0]
            y = (1 - alpha) * points1[i][1] + alpha * points2[i][1]
            points_morph.append((int(x), int(y)))
            
        for indices in triangle_indices:
            t1 = [points1[indices[0]], points1[indices[1]], points1[indices[2]]]
            t2 = [points2[indices[0]], points2[indices[1]], points2[indices[2]]]
            t = [points_morph[indices[0]], points_morph[indices[1]], points_morph[indices[2]]]
            
            morph_triangle(img1, img2, img_morph, t1, t2, t, alpha)
            
        out.write(img_morph)
        print(f"Frame {alpha:.2f} done")
        
    out.release()
    print("Saved morph_output.mp4")

if __name__ == '__main__':
    main()
