#!/usr/bin/env python3
"""
CAPTCHA SOLVER - Template Matching (Auto-Detect Character Count)
Now automatically determines number of characters - no need for --chars!
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from collections import defaultdict
import json
import shutil
from collections import Counter

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

CONFIG = {
    'img_size': 56,
    'charset': 'abcdefghijklmnopqrstuvwxyz0123456789',
    'clahe_clip': 3.0,
    'morph_kernel': 3,
    'min_blob_area': 20,
    'overlap_ratio': 0.33,
}


def preprocess(image_path):
    """Phase 1: Convert to clean binary."""
    img = cv2.imread(str(image_path))
    if img is None:
        return None
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    s_channel = hsv[:, :, 1]
    
    clahe = cv2.createCLAHE(clipLimit=CONFIG['clahe_clip'], tileGridSize=(8, 8))
    enhanced = clahe.apply(s_channel)
    denoised = cv2.bilateralFilter(enhanced, d=5, sigmaColor=50, sigmaSpace=50)
    
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    if np.sum(binary > 128) > binary.size * 0.5:
        binary = 255 - binary
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (CONFIG['morph_kernel'], CONFIG['morph_kernel']))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    return binary


def estimate_char_count(binary):
    """
    Auto-detect number of characters.
    Default is 7 (most common CAPTCHA length).
    Override with --chars for different lengths.
    """
    coords = cv2.findNonZero(binary)
    if coords is None:
        return 7
    
    x, y, w, h = cv2.boundingRect(coords)
    ratio = w / h
    
    # Rough estimate based on width-to-height ratio
    if ratio > 3.5:
        estimated = 9
    elif ratio > 3.0:
        estimated = 8
    elif ratio > 2.5:
        estimated = 7
    elif ratio > 2.0:
        estimated = 6
    else:
        estimated = 5
    
    print(f"  Auto-detected: ~{estimated} characters (text: {w}x{h}, ratio: {ratio:.1f})")
    print(f"  Tip: Use --chars N if this is wrong")
    
    return estimated

def segment(binary, num_chars):
    """Phase 2: Sliding window segmentation."""
    coords = cv2.findNonZero(binary)
    if coords is None:
        return []
    
    x, y, w_roi, h_roi = cv2.boundingRect(coords)
    text_region = binary[y:y+h_roi, x:x+w_roi]
    
    window_w = w_roi // num_chars
    overlap = int(window_w * CONFIG['overlap_ratio'])
    
    chars = []
    start = 0
    
    for i in range(num_chars):
        end = min(start + window_w, w_roi)
        crop = text_region[:, start:end]
        crop = cv2.copyMakeBorder(crop, 3, 3, 3, 3, cv2.BORDER_CONSTANT, value=0)
        crop = cv2.resize(crop, (CONFIG['img_size'], CONFIG['img_size']))
        chars.append(crop)
        start = end - overlap
    
    return chars


class TemplateDatabase:
    """Store and match character templates."""
    
    def __init__(self, save_path="templates.json"):
        self.save_path = save_path
        self.templates = defaultdict(list)
        self.loaded = False
    
    def build_from_labeled_images(self, data_dir):
        """Extract characters from labeled images and build template database."""
        print("=" * 60)
        print("BUILDING TEMPLATE DATABASE")
        print("=" * 60)
        
        data_dir = Path(data_dir)
        total_chars = 0
        
        for img_path in sorted(data_dir.glob("*")):
            if img_path.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.bmp', '.jfif']:
                continue
            
            label = img_path.stem.lower()
            label = ''.join(c for c in label if c in CONFIG['charset'])
            
            if not label:
                continue
            
            print(f"\nProcessing: {img_path.name} -> '{label}' ({len(label)} chars)")
            
            binary = preprocess(img_path)
            if binary is None:
                print(f"  ❌ Cannot load")
                continue
            
            chars = segment(binary, len(label))
            
            if len(chars) != len(label):
                print(f"  ⚠️ Got {len(chars)} chars, expected {len(label)}")
                continue
            
            for i, (char_img, char_label) in enumerate(zip(chars, label)):
                self.templates[char_label].append(char_img)
                total_chars += 1
            
            print(f"  ✅ Added {len(label)} characters")
        
        print(f"\n📊 Template database built:")
        for char in sorted(self.templates.keys()):
            count = len(self.templates[char])
            bar = '█' * count
            print(f"  '{char}': {count} templates {bar}")
        
        print(f"\n  Total: {total_chars} character templates")
        print(f"  Unique characters: {len(self.templates)}")
        
        self.save()
    
    def save(self):
        """Save templates to disk."""
        output_dir = Path("templates")
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir()
        
        metadata = {}
        
        for char, images in self.templates.items():
            char_dir = output_dir / char
            char_dir.mkdir(exist_ok=True)
            
            for i, img in enumerate(images):
                save_img = 255 - img
                cv2.imwrite(str(char_dir / f"{i}.png"), save_img)
            
            metadata[char] = len(images)
        
        with open(output_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n💾 Templates saved to '{output_dir}/'")
    
    def load(self, templates_dir="templates"):
        """Load templates from disk."""
        templates_dir = Path(templates_dir)
        metadata_path = templates_dir / "metadata.json"
        
        if not metadata_path.exists():
            print(f"❌ No templates found at {templates_dir}")
            return False
        
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        self.templates = defaultdict(list)
        
        for char, count in metadata.items():
            char_dir = templates_dir / char
            for i in range(count):
                img = cv2.imread(str(char_dir / f"{i}.png"), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    img = 255 - img
                    self.templates[char].append(img)
        
        self.loaded = True
        print(f"✅ Loaded templates for {len(self.templates)} characters")
        return True
    
    def match(self, char_img, top_k=3):
        """Match a character image against all templates."""
        if not self.templates:
            return [('?', 0)]
        
        results = []
        
        for char, templates in self.templates.items():
            best_score = 0
            
            for template in templates:
                if template.shape != char_img.shape:
                    template_resized = cv2.resize(template, (CONFIG['img_size'], CONFIG['img_size']))
                else:
                    template_resized = template
                
                score = cv2.matchTemplate(char_img, template_resized, cv2.TM_CCOEFF_NORMED)[0][0]
                best_score = max(best_score, score)
            
            results.append((char, best_score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


class CaptchaSolver:
    """CAPTCHA solver with auto-detect character count."""
    
    def __init__(self):
        self.database = TemplateDatabase()
    
    def build_database(self, data_dir):
        """Build template database from labeled images."""
        self.database.build_from_labeled_images(data_dir)
    
    def solve(self, image_path, num_chars=None, verbose=True):
        """
        Solve a CAPTCHA image.
        
        Args:
            image_path: Path to CAPTCHA
            num_chars: Number of characters (auto-detected if None)
        """
        if not self.database.loaded:
            self.database.load()
        
        if not self.database.templates:
            print("❌ No templates loaded! Build database first.")
            return "?"
        
        if verbose:
            print("\n" + "=" * 60)
            print(f"SOLVING: {Path(image_path).name}")
            print("=" * 60)
        
        # Preprocess
        binary = preprocess(image_path)
        if binary is None:
            return "?"
        
        # Auto-detect character count if not specified
        if num_chars is None:
            num_chars = estimate_char_count(binary)
        
        if verbose:
            print(f"  Using {num_chars} characters")
        
        # Segment
        chars = segment(binary, num_chars)
        
        if not chars:
            print("  ❌ Segmentation failed")
            return "?"
        
        # Match each character
        result = []
        all_scores = []
        
        if verbose:
            print(f"\n  Character Matches:")
            print("  " + "-" * 50)
        
        for i, char_img in enumerate(chars):
            matches = self.database.match(char_img, top_k=3)
            
            best_char, best_score = matches[0]
            result.append(best_char)
            all_scores.append(best_score)
            
            if verbose:
                bar = '█' * int(best_score * 20)
                print(f"  [{i+1}] -> '{best_char}' ({best_score:.0%}) {bar}")
        
        text = ''.join(result)
        avg_score = np.mean(all_scores)
        
        if verbose:
            print("\n" + "=" * 60)
            print(f"📝 RESULT: {text}")
            print(f"   Confidence: {avg_score:.1%}")
            print("=" * 60)
        
        return text


# ======================== COMMAND LINE ========================
if __name__ == "__main__":
    print("=" * 60)
    print("CAPTCHA SOLVER - Template Matching (Auto-Detect)")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  1. Build templates:")
        print("     python template_solver.py --build <data_dir>")
        print()
        print("  2. Solve (auto-detect chars):")
        print("     python template_solver.py --solve <image>")
        print()
        print("  3. Solve (specify chars):")
        print("     python template_solver.py --solve <image> --chars 7")
        print()
        print("  4. Build then solve:")
        print("     python template_solver.py --build <data_dir> --solve <image>")
        sys.exit(0)
    
    solver = CaptchaSolver()
    
    if "--build" in sys.argv:
        idx = sys.argv.index("--build")
        if idx + 1 < len(sys.argv):
            data_dir = sys.argv[idx + 1]
            solver.build_database(data_dir)
    
    if "--solve" in sys.argv:
        idx = sys.argv.index("--solve")
        image_path = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        
        num_chars = None
        if "--chars" in sys.argv:
            chars_idx = sys.argv.index("--chars")
            if chars_idx + 1 < len(sys.argv):
                num_chars = int(sys.argv[chars_idx + 1])
        
        if image_path:
            text = solver.solve(image_path, num_chars)
            print(f"\n✅ Final: {text}")