import cv2
import numpy as np
import os
import sys

# ============================================
# EDGE DETECTION FUNCTIONS
# ============================================

def canny_edge_detection(image, low_threshold=50, high_threshold=150, blur_ksize=5):
    """
    Canny edge detection using Bilateral Filtering to remove glossy 3D inner reflections.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Bilateral filter removes internal glossy gradients while keeping outer text edges sharp
    smoothed = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    edges = cv2.Canny(smoothed, low_threshold, high_threshold)
    return edges

def canny_auto_edge_detection(image, blur_ksize=5):
    """
    Auto-threshold Canny edge detection with Bilateral Filtering.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Smooth internal reflections
    smoothed = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    
    # Auto threshold using median
    v = np.median(smoothed)
    lower = int(max(0, (1.0 - 0.33) * v))
    upper = int(min(255, (1.0 + 0.33) * v))
    
    edges = cv2.Canny(smoothed, lower, upper)
    return edges

def sobel_edge_detection(image, ksize=3):
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    smoothed = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    sobel_x = cv2.Sobel(smoothed, cv2.CV_64F, 1, 0, ksize=ksize)
    sobel_y = cv2.Sobel(smoothed, cv2.CV_64F, 0, 1, ksize=ksize)
    
    magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
    magnitude = np.uint8(magnitude / np.max(magnitude) * 255)
    
    _, edges = cv2.threshold(magnitude, 30, 255, cv2.THRESH_BINARY)
    return edges

def laplacian_edge_detection(image, ksize=3):
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    smoothed = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    laplacian = cv2.Laplacian(smoothed, cv2.CV_64F, ksize=ksize)
    laplacian = np.uint8(np.absolute(laplacian))
    
    _, edges = cv2.threshold(laplacian, 30, 255, cv2.THRESH_BINARY)
    return edges

def scharr_edge_detection(image):
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    smoothed = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    scharr_x = cv2.Scharr(smoothed, cv2.CV_64F, 1, 0)
    scharr_y = cv2.Scharr(smoothed, cv2.CV_64F, 0, 1)
    
    magnitude = np.sqrt(scharr_x**2 + scharr_y**2)
    magnitude = np.uint8(magnitude / np.max(magnitude) * 255)
    
    _, edges = cv2.threshold(magnitude, 30, 255, cv2.THRESH_BINARY)
    return edges

def apply_edge_detection(image_path, output_path=None, method='canny_auto'):
    """
    Apply edge detection directly to the cropped color image.
    """
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Error: Could not open image at {image_path}")

    if method == 'canny':
        edges = canny_edge_detection(img)
    elif method == 'canny_auto':
        edges = canny_auto_edge_detection(img)
    elif method == 'sobel':
        edges = sobel_edge_detection(img)
    elif method == 'laplacian':
        edges = laplacian_edge_detection(img)
    elif method == 'scharr':
        edges = scharr_edge_detection(img)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    if output_path is None:
        base, _ = os.path.splitext(image_path)
        output_path = f"{base}_edges_{method}.png"
    
    cv2.imwrite(output_path, edges)
    print(f"  ✅ Edge map saved to: {output_path}")
    
    return edges

# ============================================
# TEXT AREA CROPPING FUNCTION
# ============================================

def crop_text_region(image_path, output_path=None, threshold=240, padding=5):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Error: Could not open image at {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    points = cv2.findNonZero(thresh)

    if points is None:
        print("Warning: No text region found.")
        return img

    x, y, w, h = cv2.boundingRect(points)
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(img.shape[1] - x, w + 2 * padding)
    h = min(img.shape[0] - y, h + 2 * padding)

    cropped_img = img[y:y+h, x:x+w]
    if output_path:
        cv2.imwrite(output_path, cropped_img)
    return cropped_img

# ============================================
# IMPROVED SEGMENTATION - VERSION 2 (BEST)
# ============================================

def morphological_cleanup(mask):
    if mask is None:
        raise ValueError("Input mask is None.")

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask

def segment_colored_text(image_path, output_path=None):
    """
    Color range-based segmentation (Version 2 - BEST METHOD)
    Detects colored text by filtering non-white, non-black pixels in HSV space.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image at '{image_path}'.")

    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define color ranges for text (anything that's not white, black, or gray)
    # Lower: Min saturation 30 (to avoid grays), Min value 50 (to avoid black)
    # Upper: Max saturation and value
    lower_bound = np.array([0, 30, 50])     
    upper_bound = np.array([180, 255, 255])
    
    # Create mask for colored regions
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    
    # Clean up the mask
    mask = morphological_cleanup(mask)

    # Create RGBA image (original colors + transparency mask)
    b, g, r = cv2.split(img)
    rgba_img = cv2.merge((b, g, r, mask))

    if output_path is None:
        base, _ = os.path.splitext(image_path)
        output_path = f"{base}_segmented.png"
    cv2.imwrite(output_path, rgba_img)
    print(f"  ✅ Segmented image saved to: {output_path}")
    return output_path

# ============================================
# DISPLAY FUNCTIONS
# ============================================

def display_edge_methods():
    print("\n📊 Available Edge Detection Methods:")
    print("  1. canny      - Standard Canny edge detection")
    print("  2. canny_auto - Canny with automatic thresholds (Recommended)")
    print("  3. sobel      - Sobel gradient-based detection")
    print("  4. laplacian  - Laplacian second-derivative detection")
    print("  5. scharr     - Scharr (better than Sobel for small gradients)")
    print("  6. none       - Skip edge detection")

# ============================================
# MAIN PIPELINE
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("  IMAGE PROCESSING PIPELINE")
    print("  Cropping → Segmentation (v2) → Edge Detection (Optional)")
    print("=" * 60)

    filename = input("📁 Enter image name (e.g., Captcha.jfif): ").strip()
    if not filename or not os.path.exists(filename):
        print(f"❌ Error: Image '{filename}' not found.")
        sys.exit()

    print("\n🔍 Do you want to apply edge detection?")
    edge_choice = input("   (y/n, default: y): ").strip().lower()
    
    use_edge = edge_choice != 'n'
    edge_method = 'canny_auto'
    
    if use_edge:
        display_edge_methods()
        user_method = input("\n🔧 Select method (default: canny_auto): ").strip()
        if user_method:
            edge_method = user_method

    base, _ = os.path.splitext(filename)
    cropped_name = f"{base}_cropped.png"
    
    try:
        print("\n🔹 STEP 1: Cropping text region...")
        crop_text_region(filename, output_path=cropped_name, padding=10)
        print(f"  ✅ Cropped image saved as: {cropped_name}")
        
        print("\n🔹 STEP 2: Segmenting colored text (using v2 - Color Range)...")
        segmented_name = f"{base}_cropped_segmented.png"
        segment_colored_text(cropped_name, output_path=segmented_name)
        
        if use_edge:
            print(f"\n🔹 STEP 3: Applying {edge_method} edge detection to cropped image...")
            edge_output = f"{base}_edges_{edge_method}.png"
            apply_edge_detection(cropped_name, output_path=edge_output, method=edge_method)
        
        print("\n" + "=" * 60)
        print("✅ PROCESSING COMPLETE!")
        print("=" * 60)
        print(f"\n📁 Output Files:")
        print(f"   1. Cropped:      {cropped_name}")
        print(f"   2. Segmented:    {segmented_name}")
        if use_edge:
            print(f"   3. Edge Map:     {edge_output}")

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit()