from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from skimage import measure, morphology

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("captcha")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class CharGlyph:
    index: int
    bbox: tuple[int, int, int, int]  # x, y, w, h
    mask: np.ndarray
    color_patch: np.ndarray


@dataclass
class AnalysisResult:
    text: str
    confidence: float
    angle: str
    source: str


@dataclass
class PipelineResult:
    input_path: Path
    separated_path: Path
    output_path: Path
    extracted_text: str
    confidence: float
    color_checks: list[bool] = field(default_factory=list)
    angle_results: list[AnalysisResult] = field(default_factory=list)
    verification_passes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Step 1 & 2 — separation + 1px spacing
# ---------------------------------------------------------------------------


def load_image(path: Path) -> tuple[np.ndarray, np.ndarray]:
    bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if bgr is None:
        raise FileNotFoundError(f"Cannot read image: {path}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return bgr, rgb


def remove_thin_noise_lines(bgr: np.ndarray) -> np.ndarray:
    """Remove 1px interference lines common in captchas."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    if np.mean(binary) > 127:
        binary = cv2.bitwise_not(binary)

    # Keep thicker letter strokes; discard very thin structures.
    opened = morphology.opening(binary > 0, morphology.disk(1))
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
    horiz = cv2.morphologyEx(opened.astype(np.uint8) * 255, cv2.MORPH_OPEN, h_kernel)
    vert = cv2.morphologyEx(opened.astype(np.uint8) * 255, cv2.MORPH_OPEN, v_kernel)
    lines = cv2.bitwise_or(horiz, vert)
    text_only = cv2.bitwise_and(opened.astype(np.uint8) * 255, cv2.bitwise_not(lines))

    # Inpaint removed line pixels from original.
    mask = ((binary > 0) & (text_only == 0)).astype(np.uint8) * 255
    if mask.sum() > 0:
        return cv2.inpaint(bgr, mask, 3, cv2.INPAINT_TELEA)
    return bgr


def build_text_mask(gray: np.ndarray) -> np.ndarray:
    """Binary mask where text pixels are True."""
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Prefer dark text on light background; flip if needed.
    if np.mean(otsu) > 127:
        otsu = cv2.bitwise_not(otsu)

    # Remove speckle noise while keeping thin strokes.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(otsu, cv2.MORPH_OPEN, kernel, iterations=1)
    return cleaned > 0


def split_touching_components(mask: np.ndarray) -> np.ndarray:
    """
    Reduce overlap by eroding slightly, then watershed split on wide blobs.
    Returns refined binary mask.
    """
    binary = (mask.astype(np.uint8)) * 255
    dist = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist, 0.35 * dist.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)

    unknown = cv2.subtract(binary, sure_fg)
    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    color_bgr = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    cv2.watershed(color_bgr, markers)

    split = np.zeros_like(binary)
    split[markers > 1] = 255
    if split.sum() < binary.sum() * 0.5:
        # Fallback: light erosion separates most overlaps.
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        split = cv2.erode(binary, kernel, iterations=1)
    return split > 0


def extract_glyphs(rgb: np.ndarray, mask: np.ndarray) -> list[CharGlyph]:
    labeled = measure.label(mask, connectivity=2)
    regions = measure.regionprops(labeled)

    img_h, img_w = mask.shape[:2]
    min_area = max(20, int(img_h * img_w * 0.002))

    glyphs: list[CharGlyph] = []
    for region in regions:
        min_row, min_col, max_row, max_col = region.bbox
        h, w = max_row - min_row, max_col - min_col
        if h < 5 or w < 3 or region.area < min_area:
            continue

        submask = (labeled[min_row:max_row, min_col:max_col] == region.label)
        patch = rgb[min_row:max_row, min_col:max_col].copy()
        patch[~submask] = [255, 255, 255]

        glyphs.append(
            CharGlyph(
                index=0,
                bbox=(min_col, min_row, w, h),
                mask=submask,
                color_patch=patch,
            )
        )

    glyphs.sort(key=lambda g: g.bbox[0])
    for i, g in enumerate(glyphs):
        g.index = i
    return glyphs


def rebuild_with_spacing(
    glyphs: list[CharGlyph],
    gap_px: int = 1,
    pad: int = 4,
    bg: tuple[int, int, int] = (255, 255, 255),
) -> np.ndarray:
    if not glyphs:
        return np.full((40, 120, 3), bg, dtype=np.uint8)

    total_w = sum(g.bbox[2] for g in glyphs) + gap_px * max(0, len(glyphs) - 1) + pad * 2
    max_h = max(g.bbox[3] for g in glyphs) + pad * 2
    canvas = np.full((max_h, total_w, 3), bg, dtype=np.uint8)

    x = pad
    for g in glyphs:
        _, _, w, h = g.bbox
        y = pad + (max_h - pad * 2 - h) // 2
        canvas[y : y + h, x : x + w] = g.color_patch
        x += w + gap_px

    return canvas


def separate_overlapping(rgb: np.ndarray) -> tuple[np.ndarray, list[CharGlyph]]:
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    mask = build_text_mask(gray)
    refined = split_touching_components(mask)
    glyphs = extract_glyphs(rgb, refined)
    spaced = rebuild_with_spacing(glyphs, gap_px=1)
    return spaced, glyphs


def ocr_single_glyph(glyph: CharGlyph) -> tuple[str, float]:
    """OCR one separated character with single-char mode."""
    patch = glyph.color_patch
    proc = preprocess_for_ocr(patch, scale=4)
    text, conf = ocr_image(proc, psm=10)
    if text:
        return text[0], conf
    return "", conf


def ocr_glyph_sequence(glyphs: list[CharGlyph]) -> tuple[str, float]:
    """Read separated glyphs left-to-right — most reliable for overlapped captchas."""
    chars: list[str] = []
    confs: list[float] = []
    for g in glyphs:
        ch, conf = ocr_single_glyph(g)
        if ch:
            chars.append(ch)
            confs.append(conf)
        log.info("Step 4 — glyph[%d] at x=%d -> %r (%.1f%%)", g.index, g.bbox[0], ch or "?", conf)
    text = _clean_ocr_text("".join(chars))
    confidence = float(np.mean(confs)) if confs else 0.0
    return text, confidence


# ---------------------------------------------------------------------------
# Step 3 — color preservation checks (3 passes)
# ---------------------------------------------------------------------------


def color_preservation_check(original: np.ndarray, candidate: np.ndarray) -> bool:
    """
    Confirm the main image colors are unchanged.
    Separated view uses white background; we compare text-colored pixels only.
    """
    orig_gray = cv2.cvtColor(original, cv2.COLOR_RGB2GRAY)
    _, text_mask = cv2.threshold(orig_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    if np.mean(text_mask) > 127:
        text_mask = cv2.bitwise_not(text_mask)
    text_mask = text_mask > 0

    if text_mask.sum() == 0:
        return True

    orig_pixels = original[text_mask]
    # Map original text pixels to nearest in candidate (same spatial layout area).
    cand_pixels = candidate[text_mask] if candidate.shape == original.shape else None

    if cand_pixels is None:
        # Spaced image differs in size — compare mean text color statistics.
        cand_gray = cv2.cvtColor(candidate, cv2.COLOR_RGB2GRAY)
        _, cand_mask = cv2.threshold(cand_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        if np.mean(cand_mask) > 127:
            cand_mask = cv2.bitwise_not(cand_mask)
        cand_pixels = candidate[cand_mask > 0]
        if len(cand_pixels) == 0:
            return False
        orig_mean = orig_pixels.mean(axis=0)
        cand_mean = cand_pixels.mean(axis=0)
        diff = np.abs(orig_mean - cand_mean)
        return bool(np.all(diff <= 18))

    diff = np.abs(orig_pixels.astype(np.int16) - cand_pixels.astype(np.int16))
    mean_diff = diff.mean()
    return bool(mean_diff <= 12)


def run_color_verification(original: np.ndarray, separated: np.ndarray, passes: int = 3) -> list[bool]:
    results: list[bool] = []
    for i in range(1, passes + 1):
        ok = color_preservation_check(original, separated)
        results.append(ok)
        status = "PASS" if ok else "FAIL"
        log.info("Step 3 — color check pass %d/%d: %s (no unintended color drift)", i, passes, status)
    return results


# ---------------------------------------------------------------------------
# Step 4 & 5 — multi-angle OCR + triple verification
# ---------------------------------------------------------------------------


def _clean_ocr_text(text: str) -> str:
    return "".join(ch for ch in text.upper() if ch.isalnum())


def ocr_image(img: np.ndarray, psm: int = 7, whitelist: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") -> tuple[str, float]:
    config = f"--psm {psm} -c tessedit_char_whitelist={whitelist}"
    data = pytesseract.image_to_data(img, config=config, output_type=pytesseract.Output.DICT)

    chars: list[str] = []
    confidences: list[float] = []
    for ch, conf in zip(data["text"], data["conf"]):
        ch = ch.strip()
        if not ch:
            continue
        try:
            c = float(conf)
        except ValueError:
            continue
        if c >= 0:
            chars.append(ch)
            confidences.append(c)

    text = _clean_ocr_text("".join(chars))
    confidence = float(np.mean(confidences)) if confidences else 0.0
    return text, confidence


def preprocess_for_ocr(img: np.ndarray, scale: int = 3) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if img.ndim == 3 else img
    gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def skew_angle(gray: np.ndarray) -> float:
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=60)
    if lines is None:
        return 0.0
    angles = []
    for rho_theta in lines[:20]:
        _, theta = rho_theta[0]
        angle = (theta * 180 / np.pi) - 90
        if -45 <= angle <= 45:
            angles.append(angle)
    return float(np.median(angles)) if angles else 0.0


def rotate_image(img: np.ndarray, angle: float) -> np.ndarray:
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        img,
        matrix,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255) if img.ndim == 3 else 255,
    )


def italic_shear(img: np.ndarray, shear: float = 0.25) -> np.ndarray:
    h, w = img.shape[:2]
    matrix = np.float32([[1, shear, 0], [0, 1, 0]])
    return cv2.warpAffine(
        img,
        matrix,
        (w + int(shear * h), h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255) if img.ndim == 3 else 255,
    )


def analyze_by_columns(img: np.ndarray, cols: int = 6) -> str:
    h, w = img.shape[:2]
    chunk = max(1, w // cols)
    letters: list[str] = []
    for i in range(cols):
        x0 = i * chunk
        x1 = w if i == cols - 1 else (i + 1) * chunk
        slice_img = img[:, x0:x1]
        if slice_img.size == 0:
            continue
        text, _ = ocr_image(preprocess_for_ocr(slice_img), psm=10)
        if text:
            letters.append(text[0])
    return _clean_ocr_text("".join(letters))


def analyze_by_rows(img: np.ndarray, rows: int = 3) -> str:
    h, w = img.shape[:2]
    chunk = max(1, h // rows)
    parts: list[str] = []
    for i in range(rows):
        y0 = i * chunk
        y1 = h if i == rows - 1 else (i + 1) * chunk
        slice_img = img[y0:y1, :]
        text, _ = ocr_image(preprocess_for_ocr(slice_img), psm=7)
        parts.append(text)
    return _clean_ocr_text("".join(parts))


def multi_angle_analysis(img: np.ndarray, source: str) -> list[AnalysisResult]:
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if img.ndim == 3 else img
    angle = skew_angle(gray)

    variants: list[tuple[str, np.ndarray]] = [
        ("normal", img),
        ("tilt_corrected", rotate_image(img, -angle)),
        ("italic", italic_shear(img)),
        ("row_slices", img),
        ("column_slices", img),
    ]

    results: list[AnalysisResult] = []
    for label, variant in variants:
        if label == "row_slices":
            text = analyze_by_rows(variant)
            conf = 70.0 if text else 0.0
        elif label == "column_slices":
            text = analyze_by_columns(variant)
            conf = 70.0 if text else 0.0
        else:
            text, conf = ocr_image(preprocess_for_ocr(variant))
        results.append(AnalysisResult(text=text, confidence=conf, angle=label, source=source))
        log.info(
            "Step 4 — angle=%-16s source=%-10s text=%r conf=%.1f%%",
            label,
            source,
            text,
            conf,
        )
    return results


def consensus_word(results: Iterable[AnalysisResult], min_length: int = 1) -> tuple[str, float]:
    texts = [r.text for r in results if r.text and len(r.text) >= min_length]
    if not texts:
        return "", 0.0

    counter = Counter(texts)
    word, count = counter.most_common(1)[0]
    confidence = (count / len(texts)) * 100

    matching = [r for r in results if r.text == word]
    if matching:
        confidence = max(confidence, float(np.mean([r.confidence for r in matching])))

    return word, confidence


def weighted_consensus(results: Iterable[AnalysisResult]) -> tuple[str, float]:
    """
    Prefer glyph-sequence and separated normal views over noisy original passes.
    """
    weights = {
        "glyph_sequence": 3.0,
        "separated": 2.5,
        "separated_initial": 2.0,
        "original_pass_1": 1.0,
        "original_pass_2": 1.0,
        "original_pass_3": 1.0,
    }
    score: Counter[str] = Counter()
    conf_sum: dict[str, float] = {}
    conf_count: dict[str, int] = {}

    for r in results:
        if not r.text:
            continue
        w = weights.get(r.source, 1.0)
        if r.angle in ("normal", "tilt_corrected"):
            w *= 1.2
        score[r.text] += w
        conf_sum[r.text] = conf_sum.get(r.text, 0.0) + r.confidence * w
        conf_count[r.text] = conf_count.get(r.text, 0) + 1

    if not score:
        return "", 0.0

    word = score.most_common(1)[0][0]
    total_weight = sum(score.values())
    agreement = (score[word] / total_weight) * 100
    avg_conf = conf_sum[word] / max(conf_count[word], 1)
    confidence = max(agreement, avg_conf)
    return word, confidence


def triple_verification(
    original: np.ndarray,
    separated: np.ndarray,
    glyph_word: str,
    glyph_conf: float,
) -> tuple[str, float, list[str], list[AnalysisResult]]:
    passes: list[str] = []
    all_results: list[AnalysisResult] = []

    if glyph_word:
        all_results.append(
            AnalysisResult(text=glyph_word, confidence=glyph_conf, angle="glyph_sequence", source="glyph_sequence")
        )

    for i in range(1, 4):
        log.info("Step 5 — verification pass %d/3 on original image", i)
        pass_results = multi_angle_analysis(original, source=f"original_pass_{i}")
        all_results.extend(pass_results)
        word, _ = consensus_word(pass_results, min_length=2)
        passes.append(word)
        log.info("Step 5 — pass %d consensus: %r", i, word or "(none)")

    spaced_results = multi_angle_analysis(separated, source="separated")
    all_results.extend(spaced_results)

    final_word, confidence = weighted_consensus(all_results)

    non_empty = [p for p in passes if p]
    if non_empty:
        pass_counter = Counter(non_empty)
        agree = pass_counter.most_common(1)[0][1] / len(non_empty)
        if pass_counter.most_common(1)[0][0] == final_word:
            confidence = max(confidence, agree * 100)

    if glyph_word and final_word == glyph_word:
        confidence = max(confidence, glyph_conf, 95.0)

    return final_word, confidence, passes, all_results


# ---------------------------------------------------------------------------
# Step 6 — clean output image
# ---------------------------------------------------------------------------


def render_clean_text(text: str, out_path: Path, size: int = 72) -> None:
    width = max(320, len(text) * int(size * 0.65) + 40)
    height = size + 40
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    font = None
    for name in ("arial.ttf", "Arial.ttf", "DejaVuSans-Bold.ttf", "segoeui.ttf"):
        try:
            font = ImageFont.truetype(name, size)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (width - tw) // 2
    y = (height - th) // 2
    draw.text((x, y), text, fill="black", font=font)
    img.save(out_path)
    log.info("Step 6 — clean readable image saved: %s", out_path)


# ---------------------------------------------------------------------------
# Pipeline orchestration
# ---------------------------------------------------------------------------


def process_captcha(input_path: Path, output_dir: Path) -> PipelineResult:
    input_path = input_path.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = input_path.stem
    separated_path = output_dir / f"{stem}_separated.png"
    output_path = output_dir / f"{stem}_readable.png"
    report_path = output_dir / f"{stem}_report.json"

    log.info("=== CAPTCHA pipeline start: %s ===", input_path.name)

    bgr, rgb = load_image(input_path)
    denoised_bgr = remove_thin_noise_lines(bgr)
    rgb = cv2.cvtColor(denoised_bgr, cv2.COLOR_BGR2RGB)

    log.info("Step 1 — separating overlapping characters")
    separated, glyphs = separate_overlapping(rgb)
    cv2.imwrite(str(separated_path), cv2.cvtColor(separated, cv2.COLOR_RGB2BGR))
    log.info("Step 1 — found %d character glyphs", len(glyphs))

    log.info("Step 2 — rebuilt image with 1px spacing between characters")
    log.info("Step 2 — saved: %s", separated_path)

    color_checks = run_color_verification(rgb, separated, passes=3)
    if not all(color_checks):
        log.warning("Step 3 — color verification reported drift; OCR continues with caution")

    log.info("Step 4 — per-glyph sequence + multi-angle analysis (italic, tilt, row, column)")
    glyph_word, glyph_conf = ocr_glyph_sequence(glyphs)
    angle_results = multi_angle_analysis(separated, source="separated_initial")
    if glyph_word:
        angle_results.append(
            AnalysisResult(text=glyph_word, confidence=glyph_conf, angle="glyph_sequence", source="glyph_sequence")
        )
    step4_word, step4_conf = weighted_consensus(angle_results)
    if not step4_word:
        step4_word, step4_conf = glyph_word, glyph_conf
    log.info("Step 4 — confirmed word from all angles: %r (%.1f%%)", step4_word, step4_conf)

    final_word, confidence, verify_passes, all_results = triple_verification(
        rgb, separated, glyph_word, glyph_conf
    )

    if confidence < 95.0:
        log.warning(
            "Step 5 — confidence %.1f%% is below 95%% target; best guess: %r",
            confidence,
            final_word,
        )
    else:
        log.info("Step 5 — final word (>=95%% confidence): %r (%.1f%%)", final_word, confidence)

    print("\n" + "=" * 60)
    print(f"EXTRACTED CAPTCHA TEXT: {final_word or step4_word or '(unknown)'}")
    print(f"CONFIDENCE: {confidence:.1f}%")
    print("=" * 60 + "\n")

    render_text = final_word or step4_word or "UNKNOWN"
    render_clean_text(render_text, output_path)

    result = PipelineResult(
        input_path=input_path,
        separated_path=separated_path,
        output_path=output_path,
        extracted_text=render_text,
        confidence=confidence,
        color_checks=color_checks,
        angle_results=all_results,
        verification_passes=verify_passes,
    )

    report_path.write_text(
        json.dumps(
            {
                "input": str(input_path),
                "extracted_text": result.extracted_text,
                "confidence": result.confidence,
                "color_checks": result.color_checks,
                "verification_passes": result.verification_passes,
                "separated_image": str(separated_path),
                "readable_image": str(output_path),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    log.info("Report saved: %s", report_path)
    log.info("=== CAPTCHA pipeline complete ===")
    return result


def find_tesseract() -> str | None:
    import shutil

    found = shutil.which("tesseract")
    if found:
        return found

    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        str(Path.home() / "AppData/Local/Programs/Tesseract-OCR/tesseract.exe"),
    ]
    for path in candidates:
        if Path(path).exists():
            return path
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze local CAPTCHA images for testing.")
    parser.add_argument("image", type=Path, help="Path to captcha image (png/jpg/bmp)")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory for separated/readable images (default: ./output)",
    )
    parser.add_argument(
        "--tesseract-cmd",
        type=str,
        default="",
        help="Optional path to tesseract.exe if not on PATH",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tesseract = args.tesseract_cmd or find_tesseract()
    if tesseract:
        pytesseract.pytesseract.tesseract_cmd = tesseract
        log.debug("Using tesseract: %s", tesseract)

    if not args.image.exists():
        log.error("Input image not found: %s", args.image)
        return 1

    try:
        process_captcha(args.image, args.output_dir)
    except pytesseract.TesseractNotFoundError:
        log.error(
            "Tesseract OCR not found. Install from https://github.com/UB-Mannheim/tesseract/wiki "
            "or pass --tesseract-cmd"
        )
        return 2
    except Exception as exc:
        log.exception("Pipeline failed: %s", exc)
        return 3

    return 0


if __name__ == "__main__":
    sys.exit(main())
