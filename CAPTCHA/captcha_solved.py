import os
import sys
import cv2
import numpy as np
import torch
from skimage.morphology import skeletonize

# ============================================================
# 1. SETUP MODEL PATH
# ============================================================
dexined_path = r'd:\DEV HOUSE\Pyhton\DexiNed'
if os.path.exists(dexined_path):
    sys.path.insert(0, dexined_path)
else:
    print(f"⚠️ Warning: DexiNed folder not found at {dexined_path}")

try:
    from model import DexiNed
except ImportError:
    print("⚠️ Warning: Could not import DexiNed. Edge detection will be disabled.")
    DexiNed = None

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
dexined_model = None

def load_dexined():
    global dexined_model
    if dexined_model is None and DexiNed is not None:
        print(f" 🔄 Loading DexiNed model on {device}...")
        dexined_model = DexiNed().to(device)
        checkpoint_path = 'checkpoints/BIPED/10/10_model.pth'
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        dexined_model.load_state_dict(torch.load(checkpoint_path, map_location=device))
        dexined_model.eval()
        print(" ✅ DexiNed ready.")
    return dexined_model

# ============================================================
# 2. CROP FUNCTION
# ============================================================
def crop_text_region(img, padding=10):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    points = cv2.findNonZero(thresh)
    if points is None:
        print(" ⚠️ Warning: No text region found. Returning original image.")
        return img
    x, y, w, h = cv2.boundingRect(points)
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(img.shape[1] - x, w + 2 * padding)
    h = min(img.shape[0] - y, h + 2 * padding)
    return img[y:y+h, x:x+w]

# ============================================================
# 3. SOLID TEXT MASK
# ============================================================
def get_solid_text_mask(img, min_area=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    if np.max(saturation) < 30:
        return np.zeros(img.shape[:2], dtype=np.uint8)
    _, mask = cv2.threshold(saturation, 30, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    cleaned_mask = np.zeros_like(mask)
    for label_id in range(1, num_labels):
        if stats[label_id, cv2.CC_STAT_AREA] > min_area:
            cleaned_mask[labels == label_id] = 255
    return cleaned_mask

# ============================================================
# 4. TRUE SKELETON
# ============================================================
def get_true_skeleton(solid_mask):
    binary = solid_mask > 0
    return skeletonize(binary).astype(np.uint8) * 255

# ============================================================
# 5. DEXINED EDGE DETECTION
# ============================================================
def detect_edges_dexined(img, threshold=0.5):
    model = load_dexined()
    if model is None:
        return None
    if img.ndim == 3 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    h, w = img.shape[:2]
    new_h = ((h + 15) // 16) * 16
    new_w = ((w + 15) // 16) * 16
    img_pad = cv2.copyMakeBorder(img, 0, new_h - h, 0, new_w - w, cv2.BORDER_REPLICATE)
    mean_bgr = np.array([103.939, 116.779, 123.68], dtype=np.float32)
    tensor = img_pad.astype(np.float32) - mean_bgr
    tensor = np.transpose(tensor, (2, 0, 1))
    tensor = torch.from_numpy(tensor).unsqueeze(0).to(device)
    with torch.no_grad():
        preds = model(tensor)
        fused_tensor = torch.sigmoid(preds[-1])[0, 0, :h, :w]
        fused = fused_tensor.cpu().numpy()
    binary = fused > threshold
    return skeletonize(binary).astype(np.uint8) * 255

# ============================================================
# MAIN PIPELINE
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print(" 🚀 CAPTCHA PIPELINE: CROP -> SOLID MASK -> TRUE SKELETON")
    print("=" * 60)

    filename = input("\nEnter image path: ").strip().strip('"')
    if not filename or not os.path.exists(filename):
        print(f"❌ Error: File '{filename}' not found.")
        sys.exit()

    base_name = os.path.splitext(os.path.basename(filename))[0]
    output_dir = os.path.dirname(os.path.abspath(filename))
    input_img = cv2.imread(filename)
    if input_img is None:
        print(f"❌ Error: Could not read image '{filename}'.")
        sys.exit()

    # Counter for sequential numbering
    step = 1

    try:
        # Step 1: Crop
        print(f"\n[{step}/4] Cropping text region...")
        cropped = crop_text_region(input_img, padding=10)
        crop_path = os.path.join(output_dir, f"{step}_cropped_{base_name}.png")
        cv2.imwrite(crop_path, cropped)
        print(f"   -> Saved: {crop_path}")
        step += 1

        # Step 2: Solid Text Mask
        print(f"[{step}/4] Extracting solid text and filtering noise...")
        solid_mask = get_solid_text_mask(cropped, min_area=30)
        solid_path = os.path.join(output_dir, f"{step}_solid_{base_name}.png")
        cv2.imwrite(solid_path, solid_mask)
        print(f"   -> Saved: {solid_path}")
        step += 1

        # Step 3: True Skeleton
        print(f"[{step}/4] Generating true skeleton (center spine)...")
        skeleton = get_true_skeleton(solid_mask)
        skeleton_path = os.path.join(output_dir, f"{step}_skeleton_{base_name}.png")
        cv2.imwrite(skeleton_path, skeleton)
        print(f"   -> Saved: {skeleton_path}")
        step += 1

        # Step 4: DexiNed (Optional)
        if DexiNed is not None:
            print(f"\n[{step}/4] Running DexiNed edge detection...")
            colored_solid = cv2.bitwise_and(cropped, cropped, mask=solid_mask)
            dexined_edges = detect_edges_dexined(colored_solid, threshold=0.5)
            if dexined_edges is not None:
                dexined_path_out = os.path.join(output_dir, f"{step}_dexined_hollow_{base_name}.png")
                cv2.imwrite(dexined_path_out, dexined_edges)
                print(f"   -> Saved: {dexined_path_out}")
                step += 1

        print("\n" + "=" * 60)
        print(f" 🎉 SUCCESS! {step-1} files saved to: {output_dir}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        sys.exit(1)