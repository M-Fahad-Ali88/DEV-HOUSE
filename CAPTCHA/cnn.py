#!/usr/bin/env python3
"""
COMPLETE CAPTCHA SOLVER
All phases combined:
  Phase 1: Preprocessing (saturation channel, CLAHE, Otsu)
  Phase 2: Segmentation (sliding window for cursive text)
  Phase 3: Recognition (CNN model, with Tesseract fallback)
  Phase 4: Training (train CNN on labeled data)
"""

import sys
import cv2
import numpy as np
from pathlib import Path
import random
import json
import shutil
import warnings
warnings.filterwarnings("ignore")

# Deep Learning
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim

# Visualization
import matplotlib.pyplot as plt

# Tesseract (optional fallback)
try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False


# ======================== CONFIGURATION ========================
CONFIG = {
    # Image
    'img_size': 56,
    'charset': 'abcdefghijklmnopqrstuvwxyz0123456789',
    
    # Preprocessing
    'clahe_clip': 3.0,
    'clahe_grid': (8, 8),
    'morph_kernel': 3,
    'min_blob_area': 20,
    
    # Segmentation
    'overlap_ratio': 0.33,
    
    # CNN Model
    'batch_size': 16,
    'epochs': 100,
    'learning_rate': 0.001,
    'train_split': 0.8,
}


# ======================== PHASE 1: PREPROCESSING ========================
class Phase1_Preprocessing:
    """
    Convert CAPTCHA image to clean binary.
    Uses saturation channel (best for colored text on white background).
    """
    
    def __init__(self, config=None):
        self.config = config or CONFIG
        self.steps = {}
    
    def run(self, image_path, verbose=True):
        """Run complete preprocessing pipeline."""
        if verbose:
            print("\n" + "=" * 50)
            print("PHASE 1: PREPROCESSING")
            print("=" * 50)
        
        # Load
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Cannot load: {image_path}")
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.steps['original'] = img_rgb.copy()
        
        # Step 1: Extract saturation channel
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        s_channel = hsv[:, :, 1]
        self.steps['saturation'] = s_channel.copy()
        
        # Step 2: Enhance contrast
        clahe = cv2.createCLAHE(
            clipLimit=self.config['clahe_clip'],
            tileGridSize=self.config['clahe_grid']
        )
        enhanced = clahe.apply(s_channel)
        self.steps['enhanced'] = enhanced.copy()
        
        # Step 3: Denoise
        denoised = cv2.bilateralFilter(enhanced, d=5, sigmaColor=50, sigmaSpace=50)
        self.steps['denoised'] = denoised.copy()
        
        # Step 4: Threshold
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        self.steps['thresholded'] = binary.copy()
        
        # Ensure white text on black background
        if np.sum(binary > 128) > binary.size * 0.5:
            binary = 255 - binary
        
        # Step 5: Morphological cleaning
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (self.config['morph_kernel'], self.config['morph_kernel'])
        )
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
        self.steps['closed'] = binary.copy()
        
        # Step 6: Remove small noise
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        cleaned = np.zeros_like(binary)
        
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] >= self.config['min_blob_area']:
                cleaned[labels == i] = 255
        
        self.steps['cleaned'] = cleaned.copy()
        
        # Quality check
        white_px = np.sum(cleaned > 0)
        text_ratio = white_px / cleaned.size
        
        quality = 10
        if text_ratio < 0.02:
            quality -= 3
        elif text_ratio > 0.4:
            quality -= 2
        
        if verbose:
            print(f"  White pixels: {white_px} ({text_ratio:.1%})")
            print(f"  Quality: {quality}/10")
        
        return cleaned, quality
    
    def visualize(self):
        """Show preprocessing steps."""
        n = len(self.steps)
        cols = 3
        rows = (n + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(15, 4 * rows))
        axes = axes.flatten() if n > 1 else [axes]
        
        for i, (name, img) in enumerate(self.steps.items()):
            axes[i].imshow(img, cmap='gray' if len(img.shape) == 2 else None)
            axes[i].set_title(name, fontsize=10)
            axes[i].axis('off')
        
        for i in range(n, len(axes)):
            axes[i].axis('off')
        
        plt.suptitle('Phase 1: Preprocessing Steps', fontweight='bold')
        plt.tight_layout()
        plt.show()


# ======================== PHASE 2: SEGMENTATION ========================
class Phase2_Segmentation:
    """
    Split binary image into character windows.
    Uses sliding window for cursive/merged text.
    """
    
    def __init__(self, config=None):
        self.config = config or CONFIG
    
    def run(self, binary, num_chars, verbose=True):
        """Segment binary into character images."""
        if verbose:
            print("\n" + "=" * 50)
            print("PHASE 2: SEGMENTATION")
            print("=" * 50)
        
        h, w = binary.shape
        
        # Find text region
        coords = cv2.findNonZero(binary)
        if coords is None:
            if verbose:
                print("  ❌ No text found")
            return [], 0
        
        x, y, w_roi, h_roi = cv2.boundingRect(coords)
        text_region = binary[y:y+h_roi, x:x+w_roi]
        
        if verbose:
            print(f"  Text region: {w_roi}x{h_roi}")
            print(f"  Target characters: {num_chars}")
        
        # Sliding window
        window_w = w_roi // num_chars
        overlap = int(window_w * self.config['overlap_ratio'])
        
        chars = []
        start = 0
        
        for i in range(num_chars):
            end = min(start + window_w, w_roi)
            crop = text_region[:, start:end]
            
            # Standardize
            crop = cv2.copyMakeBorder(crop, 3, 3, 3, 3, cv2.BORDER_CONSTANT, value=0)
            crop = cv2.resize(crop, (self.config['img_size'], self.config['img_size']),
                            interpolation=cv2.INTER_CUBIC)
            
            chars.append(crop)
            start = end - overlap
        
        if verbose:
            print(f"  Extracted: {len(chars)} characters")
        
        return chars, len(chars)
    
    def visualize(self, binary, chars):
        """Show segmentation results."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Binary with windows
        axes[0].imshow(binary, cmap='gray')
        
        h, w = binary.shape
        coords = cv2.findNonZero(binary)
        if coords is not None:
            x, y, w_roi, h_roi = cv2.boundingRect(coords)
            window_w = w_roi // len(chars)
            
            colors = plt.cm.rainbow(np.linspace(0, 1, len(chars)))
            for i in range(len(chars)):
                start_x = x + i * (window_w - int(window_w * 0.33))
                rect = plt.Rectangle((start_x, y), window_w, h_roi,
                                     fill=False, edgecolor=colors[i], linewidth=2)
                axes[0].add_patch(rect)
        
        axes[0].set_title(f'Segmentation: {len(chars)} windows', fontweight='bold')
        axes[0].axis('off')
        
        # Characters
        total_w = len(chars) * (self.config['img_size'] + 4)
        display = np.ones((self.config['img_size'], total_w), dtype=np.uint8) * 255
        
        x_pos = 2
        for i, char_img in enumerate(chars):
            display[:, x_pos:x_pos+self.config['img_size']] = 255 - char_img
            x_pos += self.config['img_size'] + 4
        
        axes[1].imshow(display, cmap='gray')
        axes[1].set_title(f'{len(chars)} Characters', fontweight='bold')
        axes[1].axis('off')
        
        plt.suptitle('Phase 2: Segmentation Result', fontweight='bold')
        plt.tight_layout()
        plt.show()


# ======================== PHASE 3: CNN MODEL ========================
class CharCNN(nn.Module):
    """CNN for character classification."""
    
    def __init__(self, num_classes, img_size=56):
        super().__init__()
        
        self.conv1 = nn.Conv2d(1, 32, 3, padding=1)   # 56 -> 28
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)  # 28 -> 14
        self.conv3 = nn.Conv2d(64, 128, 3, padding=1) # 14 -> 7
        self.conv4 = nn.Conv2d(128, 256, 3, padding=1)# 7 -> 3
        
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.5)
        
        # Calculate feature size after convolutions
        feature_size = img_size // 16  # After 4 pooling layers
        self.fc1 = nn.Linear(256 * feature_size * feature_size, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, num_classes)
        
        self.bn1 = nn.BatchNorm2d(32)
        self.bn2 = nn.BatchNorm2d(64)
        self.bn3 = nn.BatchNorm2d(128)
        self.bn4 = nn.BatchNorm2d(256)
    
    def forward(self, x):
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        x = self.pool(F.relu(self.bn4(self.conv4(x))))
        
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        
        return x


class Phase3_Recognition:
    """
    Character recognition using CNN (with Tesseract fallback).
    """
    
    def __init__(self, config=None):
        self.config = config or CONFIG
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.char_to_idx = {c: i for i, c in enumerate(self.config['charset'])}
        self.idx_to_char = {i: c for i, c in enumerate(self.config['charset'])}
        self.num_classes = len(self.config['charset'])
        
        self.model = CharCNN(self.num_classes, self.config['img_size']).to(self.device)
        self.model_trained = False
    
    def load_model(self, model_path):
        """Load trained model."""
        if Path(model_path).exists():
            self.model.load_state_dict(
                torch.load(model_path, map_location=self.device, weights_only=True)
            )
            self.model.eval()
            self.model_trained = True
            print(f"✅ Model loaded: {model_path}")
            return True
        else:
            print(f"⚠️ Model not found: {model_path}")
            return False
    
    def predict(self, char_images, verbose=True):
        """Predict characters from images."""
        if not self.model_trained:
            # Fallback to Tesseract
            return self._predict_tesseract(char_images, verbose)
        
        self.model.eval()
        results = []
        confidences = []
        
        with torch.no_grad():
            for img in char_images:
                tensor = torch.FloatTensor(img).unsqueeze(0).unsqueeze(0).to(self.device) / 255.0
                output = self.model(tensor)
                probs = F.softmax(output, dim=1)
                conf, pred = torch.max(probs, 1)
                
                results.append(self.idx_to_char[pred.item()])
                confidences.append(conf.item())
        
        if verbose:
            print(f"  Characters: {''.join(results)}")
            print(f"  Confidences: {[f'{c:.0%}' for c in confidences]}")
        
        return ''.join(results), confidences
    
    def _predict_tesseract(self, char_images, verbose=True):
        """Tesseract fallback."""
        if not HAS_TESSERACT:
            return '?' * len(char_images), [0] * len(char_images)
        
        results = []
        confidences = []
        
        for img in char_images:
            # Prepare for Tesseract
            ocr_img = 255 - img
            ocr_img = cv2.copyMakeBorder(ocr_img, 8, 8, 8, 8, cv2.BORDER_CONSTANT, value=255)
            
            config = f'--psm 10 -c tessedit_char_whitelist={self.config["charset"]}'
            
            try:
                data = pytesseract.image_to_data(ocr_img, config=config,
                                                  output_type=pytesseract.Output.DICT)
                
                char = '?'
                conf = 0
                for i in range(len(data['text'])):
                    if data['text'][i].strip() and int(data['conf'][i]) > conf:
                        char = data['text'][i].strip()[0].lower()
                        conf = int(data['conf'][i])
                
                results.append(char)
                confidences.append(conf / 100.0)
            except:
                results.append('?')
                confidences.append(0.0)
        
        if verbose:
            print(f"  [Tesseract] Characters: {''.join(results)}")
        
        return ''.join(results), confidences


# ======================== PHASE 4: TRAINING ========================
class CaptchaDataset(Dataset):
    """Dataset from labeled CAPTCHA images."""
    
    def __init__(self, samples, preprocessor, segmenter, char_to_idx, augment=True):
        self.samples = samples
        self.preprocessor = preprocessor
        self.segmenter = segmenter
        self.char_to_idx = char_to_idx
        self.augment = augment
    
    def __len__(self):
        # Each image produces multiple character samples
        return sum(len(label) for _, label in self.samples)
    
    def __getitem__(self, idx):
        # Find which image and which character
        cumulative = 0
        for img_path, label in self.samples:
            if idx < cumulative + len(label):
                char_pos = idx - cumulative
                
                # Preprocess
                binary, _ = self.preprocessor.run(img_path, verbose=False)
                
                # Segment
                chars, _ = self.segmenter.run(binary, len(label), verbose=False)
                
                if char_pos >= len(chars):
                    char_pos = random.randint(0, len(chars) - 1)
                
                char_img = chars[char_pos]
                target_char = label[char_pos]
                target = self.char_to_idx[target_char]
                
                # Augment
                if self.augment:
                    char_img = self._augment(char_img)
                
                # Normalize
                tensor = torch.FloatTensor(char_img).unsqueeze(0) / 255.0
                
                return tensor, target, target_char
            
            cumulative += len(label)
        
        # Fallback
        return self[0]
    
    def _augment(self, img):
        """Random augmentation."""
        if random.random() < 0.3:
            noise = np.random.normal(0, 3, img.shape).astype(np.uint8)
            img = cv2.add(img, noise)
        
        if random.random() < 0.2:
            angle = random.uniform(-5, 5)
            h, w = img.shape
            matrix = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
            img = cv2.warpAffine(img, matrix, (w, h), borderValue=0)
        
        return np.clip(img, 0, 255).astype(np.uint8)


class Phase4_Training:
    """Train the CNN model on labeled data."""
    
    def __init__(self, config=None):
        self.config = config or CONFIG
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.char_to_idx = {c: i for i, c in enumerate(self.config['charset'])}
        self.idx_to_char = {i: c for i, c in enumerate(self.config['charset'])}
        self.num_classes = len(self.config['charset'])
        
        self.preprocessor = Phase1_Preprocessing(config)
        self.segmenter = Phase2_Segmentation(config)
        self.model = CharCNN(self.num_classes, self.config['img_size']).to(self.device)
    
    def run(self, data_dir, epochs=None):
        """Train model on labeled images."""
        if epochs is None:
            epochs = self.config['epochs']
        
        print("\n" + "=" * 50)
        print("PHASE 4: CNN TRAINING")
        print("=" * 50)
        
        # Load samples
        data_dir = Path(data_dir)
        samples = []
        
        for img_path in data_dir.glob("*"):
            if img_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.jfif']:
                label = img_path.stem.lower()
                label = ''.join(c for c in label if c in self.char_to_idx)
                if label:
                    samples.append((img_path, label))
        
        if not samples:
            print("❌ No labeled images found!")
            print("   Name images like: msmnmix.png, abc123.png, etc.")
            return 0
        
        print(f"📁 Found {len(samples)} labeled images")
        
        # Split train/val
        random.shuffle(samples)
        split = int(len(samples) * self.config['train_split'])
        train_samples = samples[:split]
        val_samples = samples[split:]
        
        print(f"  Train: {len(train_samples)} images")
        print(f"  Val: {len(val_samples)} images")
        
        # Create datasets
        train_dataset = CaptchaDataset(train_samples, self.preprocessor,
                                       self.segmenter, self.char_to_idx, augment=True)
        val_dataset = CaptchaDataset(val_samples, self.preprocessor,
                                     self.segmenter, self.char_to_idx, augment=False)
        
        train_loader = DataLoader(train_dataset, batch_size=self.config['batch_size'],
                                  shuffle=True, collate_fn=self._collate)
        val_loader = DataLoader(val_dataset, batch_size=self.config['batch_size'],
                                shuffle=False, collate_fn=self._collate)
        
        # Train
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(self.model.parameters(), lr=self.config['learning_rate'])
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
        
        best_acc = 0
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            train_loss = 0
            
            for images, targets, _ in train_loader:
                images = images.to(self.device)
                targets = targets.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(images)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            # Validation
            self.model.eval()
            correct = total = 0
            
            with torch.no_grad():
                for images, targets, _ in val_loader:
                    images = images.to(self.device)
                    targets = targets.to(self.device)
                    
                    outputs = self.model(images)
                    _, predicted = torch.max(outputs, 1)
                    
                    correct += (predicted == targets).sum().item()
                    total += targets.size(0)
            
            acc = correct / max(total, 1)
            avg_loss = train_loss / max(len(train_loader), 1)
            
            print(f"  Epoch {epoch+1:3d}/{epochs} | Loss: {avg_loss:.4f} | Val Acc: {acc:.2%}")
            
            if acc > best_acc:
                best_acc = acc
                torch.save(self.model.state_dict(), 'best_model.pth')
                print(f"    ✅ Saved (acc: {acc:.2%})")
            
            scheduler.step()
        
        print(f"\n🏆 Best accuracy: {best_acc:.2%}")
        print(f"   Model saved: best_model.pth")
        
        return best_acc
    
    @staticmethod
    def _collate(batch):
        images = torch.stack([item[0] for item in batch])
        targets = torch.LongTensor([item[1] for item in batch])
        chars = [item[2] for item in batch]
        return images, targets, chars


# ======================== COMPLETE SOLVER ========================
class CaptchaSolver:
    """
    Complete CAPTCHA solver combining all 4 phases.
    
    Usage:
        # Training
        solver = CaptchaSolver()
        solver.train("training_data/")
        
        # Solving
        solver = CaptchaSolver(model_path="best_model.pth")
        text = solver.solve("captcha.png", num_chars=7)
    """
    
    def __init__(self, model_path=None):
        self.preprocessor = Phase1_Preprocessing()
        self.segmenter = Phase2_Segmentation()
        self.recognizer = Phase3_Recognition()
        self.trainer = Phase4_Training()
        
        if model_path:
            self.recognizer.load_model(model_path)
    
    def solve(self, image_path, num_chars=7, visualize=False):
        """
        Solve a CAPTCHA image.
        
        Args:
            image_path: Path to CAPTCHA image
            num_chars: Number of characters in the CAPTCHA
            visualize: Show processing steps
        
        Returns:
            Recognized text string
        """
        print("\n" + "=" * 60)
        print(f"SOLVING: {Path(image_path).name}")
        print("=" * 60)
        
        # Phase 1: Preprocessing
        binary, quality = self.preprocessor.run(image_path)
        
        if visualize:
            self.preprocessor.visualize()
        
        # Phase 2: Segmentation
        chars, count = self.segmenter.run(binary, num_chars)
        
        if not chars:
            print("❌ Segmentation failed")
            return "?"
        
        if visualize:
            self.segmenter.visualize(binary, chars)
        
        # Phase 3: Recognition
        text, confidences = self.recognizer.predict(chars)
        
        print("\n" + "=" * 60)
        print(f"📝 RESULT: {text}")
        print(f"   Confidence: {np.mean(confidences):.1%}")
        print("=" * 60)
        
        return text
    
    def train(self, data_dir, epochs=None):
        """Train the CNN model."""
        return self.trainer.run(data_dir, epochs)


# ======================== COMMAND LINE INTERFACE ========================
if __name__ == "__main__":
    print("=" * 60)
    print("CAPTCHA SOLVER - Complete Pipeline")
    print("=" * 60)
    print(f"Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    print(f"Tesseract: {'Available' if HAS_TESSERACT else 'Not available'}")
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  1. Train model:")
        print("     python solver.py --train <data_dir> [--epochs 100]")
        print()
        print("  2. Solve CAPTCHA:")
        print("     python solver.py --solve <image> --chars 7 [--model best_model.pth]")
        print()
        print("  3. Train then solve:")
        print("     python solver.py --train <data_dir> --solve <image> --chars 7")
        print()
        print("Data directory should contain images named by their text:")
        print("  data/msmnmix.png, data/abc123.png, etc.")
        sys.exit(0)
    
    # Parse arguments
    train_dir = None
    solve_image = None
    num_chars = 7
    model_path = "best_model.pth"
    epochs = None
    
    if "--train" in sys.argv:
        idx = sys.argv.index("--train")
        if idx + 1 < len(sys.argv):
            train_dir = sys.argv[idx + 1]
    
    if "--solve" in sys.argv:
        idx = sys.argv.index("--solve")
        if idx + 1 < len(sys.argv):
            solve_image = sys.argv[idx + 1]
    
    if "--chars" in sys.argv:
        idx = sys.argv.index("--chars")
        if idx + 1 < len(sys.argv):
            num_chars = int(sys.argv[idx + 1])
    
    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        if idx + 1 < len(sys.argv):
            model_path = sys.argv[idx + 1]
    
    if "--epochs" in sys.argv:
        idx = sys.argv.index("--epochs")
        if idx + 1 < len(sys.argv):
            epochs = int(sys.argv[idx + 1])
    
    # Initialize solver
    solver = CaptchaSolver(model_path=model_path if solve_image else None)
    
    # Train if requested
    if train_dir:
        solver.train(train_dir, epochs)
        # After training, load the best model
        solver.recognizer.load_model("best_model.pth")
    
    # Solve if requested
    if solve_image:
        text = solver.solve(solve_image, num_chars, visualize=True)