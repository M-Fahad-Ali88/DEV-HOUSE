#!/usr/bin/env python3
"""
PHASE 1: PREPROCESSING (Final Version)
Goal: Convert CAPTCHA to clean binary image (white text, black background)
Quality Target: 8+/10

Best Libraries:
- OpenCV: Image I/O, CLAHE, morphology
- scikit-image: Thresholding, filters
- scipy: Signal processing
- NumPy: Array operations
"""

import sys
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import cv2
import numpy as np
from pathlib import Path
from skimage import filters, exposure, morphology
from scipy import ndimage, signal
import matplotlib.pyplot as plt


class Phase1Preprocessing:
    """
    Complete preprocessing pipeline.
    
    Pipeline:
    1. Load & Analyze
    2. Channel Selection (Saturation for green text)
    3. Contrast Enhancement (CLAHE + histogram stretch)
    4. Denoising (Bilateral + NLM)
    5. Thresholding (Otsu + Sauvola + Li - picks best)
    6. Binary Cleaning (morph close → remove noise → fill holes)
    7. Quality Check (score 0-10)
    """
    
    def __init__(self):
        self.steps = {}
        self.metadata = {}
        
    def run(self, image_path, output_path=None, show_steps=True):
        """Run complete Phase 1 pipeline."""
        print("=" * 60)
        print("PHASE 1: PREPROCESSING PIPELINE")
        print("=" * 60)
        
        # Step 1: Load
        print("\n[1/7] Loading image...")
        img = self._load_image(image_path)
        self.steps['1_original'] = img.copy()
        print(f"  Shape: {img.shape}")
        
        # Step 2: Channel selection
        print("\n[2/7] Selecting best channel...")
        best_channel, channel_name, analysis = self._select_best_channel(img)
        self.steps['2_channel'] = best_channel.copy()
        self.metadata['analysis'] = analysis
        print(f"  Selected: {channel_name}")
        print(f"  Text saturation: {analysis.get('text_saturation', 'N/A')}")
        
        # Step 3: Contrast
        print("\n[3/7] Enhancing contrast...")
        enhanced = self._enhance_contrast(best_channel)
        self.steps['3_enhanced'] = enhanced.copy()
        print(f"  Range: [{enhanced.min()}, {enhanced.max()}]")
        
        # Step 4: Denoise
        print("\n[4/7] Denoising...")
        denoised = self._denoise(enhanced)
        self.steps['4_denoised'] = denoised.copy()
        
        # Step 5: Threshold
        print("\n[5/7] Thresholding...")
        binary = self._threshold(denoised)
        self.steps['5_thresholded'] = binary.copy()
        print(f"  White pixels: {np.sum(binary > 128)}")
        
        # Step 6: Clean
        print("\n[6/7] Cleaning binary...")
        cleaned = self._clean_binary(binary)
        self.steps['6_cleaned'] = cleaned.copy()
        print(f"  Final white pixels: {np.sum(cleaned > 128)}")
        
        # Step 7: Quality
        print("\n[7/7] Quality check...")
        quality = self._check_quality(cleaned)
        self.metadata['quality'] = quality
        print(f"  Blobs: {quality['num_blobs']}")
        print(f"  Score: {quality['score']}/10 - {quality['status']}")
        
        # Save
        if output_path:
            cv2.imwrite(str(output_path), cleaned)
            print(f"\n✅ Saved: {output_path}")
        
        # Show
        if show_steps:
            self._visualize()
        
        print("\n" + "=" * 60)
        print(f"PHASE 1 COMPLETE - Score: {quality['score']}/10")
        print("=" * 60)
        
        return cleaned
    
    # ======================== STEP 1 ========================
    def _load_image(self, path):
        img = cv2.imread(str(path))
        if img is None:
            raise ValueError(f"Cannot load: {path}")
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # ======================== STEP 2 ========================
    def _select_best_channel(self, img):
        """Select best channel for text/background separation."""
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        
        channels = {
            'Saturation (HSV)': hsv[:, :, 1],
            'Value (HSV)': hsv[:, :, 2],
            'Grayscale': cv2.cvtColor(img, cv2.COLOR_RGB2GRAY),
        }
        
        # Score each channel
        scores = {}
        for name, ch in channels.items():
            scores[name] = self._calculate_separability(ch)
        
        best_name = max(scores, key=scores.get)
        best_channel = channels[best_name]
        
        # Analysis
        thresh = filters.threshold_otsu(best_channel)
        text_mask = best_channel > thresh
        
        analysis = {
            'best_channel': best_name,
            'text_saturation': round(np.mean(hsv[:, :, 1][text_mask]), 1),
            'bg_saturation': round(np.mean(hsv[:, :, 1][~text_mask]), 1),
            'scores': {k: round(v, 3) for k, v in scores.items()}
        }
        
        return best_channel, best_name, analysis
    
    def _calculate_separability(self, channel):
        """Calculate bimodality score."""
        ch_norm = (channel - channel.min()) / (channel.max() - channel.min() + 1e-6)
        hist, _ = np.histogram(ch_norm, bins=50)
        hist_smooth = ndimage.gaussian_filter1d(hist.astype(float), sigma=2)
        
        peaks, _ = signal.find_peaks(hist_smooth, height=hist_smooth.max() * 0.1)
        
        if len(peaks) >= 2:
            valleys, _ = signal.find_peaks(-hist_smooth)
            if len(valleys) > 0:
                valley_h = hist_smooth[valleys[len(valleys)//2]]
                peak_h = sorted(hist_smooth[peaks])[-1]
                separation = (peak_h - valley_h) / (peak_h + 1e-6)
            else:
                separation = 0.5
        else:
            separation = 0.0
        
        std_score = np.std(channel) / (np.mean(channel) + 1e-6)
        return separation * 0.6 + std_score * 0.4
    
    # ======================== STEP 3 ========================
    def _enhance_contrast(self, channel):
        """CLAHE + histogram stretching."""
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(channel)
        p2, p98 = np.percentile(enhanced, (2, 98))
        return exposure.rescale_intensity(enhanced, in_range=(p2, p98)).astype(np.uint8)
    
    # ======================== STEP 4 ========================
    def _denoise(self, channel):
        """Bilateral filter for edge-preserving denoising."""
        return cv2.bilateralFilter(channel, d=5, sigmaColor=50, sigmaSpace=50)
    
    # ======================== STEP 5 ========================
    def _threshold(self, channel):
        """Try multiple methods, pick best result."""
        results = {}
        
        # Otsu
        t = filters.threshold_otsu(channel)
        results['otsu'] = (channel > t).astype(np.uint8) * 255
        
        # Li
        t = filters.threshold_li(channel)
        results['li'] = (channel > t).astype(np.uint8) * 255
        
        # Pick best: text should be 5-45% of image
        best = None
        best_score = 0
        for name, binary in results.items():
            ratio = np.sum(binary > 0) / binary.size
            score = 1.0 if 0.05 < ratio < 0.45 else (0.3 if ratio < 0.05 else 0.1)
            if ndimage.label(binary)[1] > 1:
                score += 0.2
            if score > best_score:
                best_score = score
                best = binary
        
        # Ensure white text on black
        if best is not None and np.sum(best > 0) > best.size * 0.5:
            best = 255 - best
        
        return best if best is not None else results['otsu']
    
    # ======================== STEP 6 ========================
    def _clean_binary(self, binary):
        """Morphological cleaning."""
        # Close gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # Remove small objects (scikit-image 0.26+ compatible)
        try:
            cleaned = morphology.remove_small_objects(closed.astype(bool), min_size=15)
        except:
            cleaned = morphology.remove_small_objects(closed.astype(bool), min_size=15, 
                                                       connectivity=2)
        
        # Fill holes
        try:
            cleaned = morphology.remove_small_holes(cleaned, area_threshold=30)
        except:
            cleaned = morphology.remove_small_holes(cleaned, area_threshold=30, 
                                                     connectivity=2)
        
        cleaned = (cleaned * 255).astype(np.uint8)
        
        # Final smooth
        kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        return cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel2)
    
    # ======================== STEP 7 ========================
    def _check_quality(self, binary):
        """Quality assessment."""
        labeled, num_blobs = ndimage.label(binary)
        
        blob_sizes = [np.sum(labeled == i) for i in range(1, num_blobs + 1)]
        avg_size = np.mean(blob_sizes) if blob_sizes else 0
        total_white = np.sum(binary > 0)
        
        score = 10
        
        if num_blobs == 0:
            score, status = 0, '❌ No text found'
        elif num_blobs == 1:
            score, status = 6, '⚠️ All merged'
        elif num_blobs > 20:
            score, status = 5, '⚠️ Too noisy'
        else:
            status = '✅ Good'
        
        text_ratio = total_white / binary.size
        if text_ratio < 0.02:
            score -= 3
            status += ' (low text)'
        elif text_ratio > 0.4:
            score -= 2
            status += ' (too much)'
        
        if len(blob_sizes) > 1 and np.std(blob_sizes) > avg_size:
            score -= 1
        
        return {
            'num_blobs': num_blobs,
            'avg_blob_size': round(avg_size),
            'total_white': total_white,
            'score': max(0, min(10, score)),
            'status': status
        }
    
    # ======================== VISUALIZATION ========================
    def _visualize(self):
        """Display all steps."""
        step_names = list(self.steps.keys())
        n = len(step_names)
        cols, rows = 4, (n + 3) // 4
        
        fig, axes = plt.subplots(rows, cols, figsize=(16, 4 * rows))
        axes = axes.flatten() if n > 1 else [axes]
        
        for i, name in enumerate(step_names):
            img = self.steps[name]
            axes[i].imshow(img, cmap='gray' if len(img.shape) == 2 else None)
            axes[i].set_title(name.split('_', 1)[-1], fontsize=10, fontweight='bold')
            axes[i].axis('off')
        
        for i in range(n, len(axes)):
            axes[i].axis('off')
        
        plt.suptitle('Phase 1: Preprocessing Pipeline', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()


# ======================== MAIN ========================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python phase1_preprocessing.py <image> [--save output.png]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = None
    
    if "--save" in sys.argv:
        idx = sys.argv.index("--save")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]
    
    processor = Phase1Preprocessing()
    result = processor.run(image_path, output_path)
    
    # Return binary image for next phase
    print(f"\nPhase 1 output ready for Phase 2 (Segmentation)")