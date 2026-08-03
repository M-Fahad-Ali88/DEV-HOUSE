import cv2
import numpy as np
import os
import sys


# Text Area Cropping Function for Captcha Images



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


# Color Segmentation Function for Captcha Images




def morphological_cleanup(mask):
    
    if mask is None:
        raise ValueError("Input mask is None.")

    if not isinstance(mask, np.ndarray):
        raise TypeError("Input mask must be a NumPy array.")

    if mask.ndim != 2:
        raise ValueError(
            f"Mask must be a 2D single-channel image, got shape {mask.shape}."
        )

    unique_vals = np.unique(mask)
    if not np.array_equal(unique_vals, [0, 255]) and not np.array_equal(
        unique_vals, [0]
    ):
        mask = np.where(mask > 127, 255, 0).astype(np.uint8)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    h, w = mask.shape
    image_area = h * w
    min_area = max(3, int(image_area * 1e-5))

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask, connectivity=8
    )

    small_component_mask = np.zeros_like(mask, dtype=bool)
    for label_id in range(1, num_labels):
        area = stats[label_id, cv2.CC_STAT_AREA]
        if area <= min_area:
            small_component_mask[labels == label_id] = True

    mask[small_component_mask] = 0
    return mask


def segment_colored_text(image_path, output_path=None):
    """
    Segment colored (non‑gray) regions from an image and save as RGBA PNG.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image at '{image_path}'.")

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    _, mask = cv2.threshold(saturation, 30, 255, cv2.THRESH_BINARY)
    mask = morphological_cleanup(mask)

    b, g, r = cv2.split(img)
    rgba_img = cv2.merge((b, g, r, mask))

    if output_path is None:
        base, _ = os.path.splitext(image_path)
        output_path = f"{base}_segmented.png"
    cv2.imwrite(output_path, rgba_img)
    print(f"Saved segmented image to {output_path}")


#  UNIFIED PIPELINE (single input, auto‑chained) 


if __name__ == "__main__":
    print("--- Image Cropping & Color Segmentation Pipeline ---")
    print("Enter one image filename. The script will crop it, then segment the crop automatically.\n")

    # Step 1: get the single user input
    filename = input("Enter image name (e.g., logo.png): ").strip()
    if not filename:
        print("No input provided. Exiting.")
        sys.exit()

    if not os.path.exists(filename):
        print(f" Error: '{filename}' not found in this folder.")
        sys.exit()

    # Step 2: crop and save as "cropped_<original>"
    cropped_name = f"cropped_{filename}"
    try:
        print(f" Cropping '{filename}'...")
        crop_text_region(filename, output_path=cropped_name, padding=10)
        print(f" Cropped image saved as '{cropped_name}'")
    except Exception as e:
        print(f" Cropping failed: {e}")
        sys.exit()

    # Step 3: run color segmentation on the cropped result
    try:
        print(f" Segmenting colored text from '{cropped_name}'...")
        # The function auto‑generates an output name like "cropped_<file>_segmented.png"
        segment_colored_text(cropped_name, output_path=None)
        print(" Segmentation completed.")
    except Exception as e:
        print(f" Segmentation failed: {e}")
        sys.exit()

    print("🏁 All done, Massing IP and Exiting...")