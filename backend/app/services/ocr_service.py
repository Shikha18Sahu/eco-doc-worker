# import easyocr

# _reader = None


# def get_reader():
#     """Lazy-load EasyOCR reader once (loading it per-request is slow)."""
#     global _reader
#     if _reader is None:
#         _reader = easyocr.Reader(["en"], gpu=False)
#     return _reader


# class OCRService:
#     """Real OCR using EasyOCR. Reads text from an image file path."""

#     def extract_text(self, image_path: str, attempt: int) -> tuple[str, float]:
#         reader = get_reader()
#         results = reader.readtext(image_path)

#         if not results:
#             return "", 0.0

#         lines = []
#         confidences = []
#         for (_, text, conf) in results:
#             lines.append(text)
#             confidences.append(conf)

#         full_text = "\n".join(lines)
#         avg_confidence = sum(confidences) / len(confidences)

#         return full_text, round(avg_confidence, 2)


import cv2
import easyocr
import numpy as np

_reader = None


def get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def preprocess_image(image_path: str) -> np.ndarray:
    """Enhances the image before OCR: grayscale, contrast boost via
    CLAHE, denoising, and upscaling if the image is small. This is a
    lightweight preprocessing step (no heavy model) aimed at improving
    EasyOCR's accuracy on photographed forms."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image at {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # CLAHE: boosts local contrast, helps faint handwriting stand out
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast_enhanced = clahe.apply(gray)

    # Light denoising to reduce JPEG/WhatsApp compression artifacts
    denoised = cv2.fastNlMeansDenoising(contrast_enhanced, h=10)

    # Upscale if the image is small — EasyOCR does better on larger text
    height, width = denoised.shape[:2]
    if width < 1200:
        scale = 1200 / width
        denoised = cv2.resize(
            denoised, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
        )

    # Convert back to 3-channel BGR since EasyOCR expects that format
    result = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)
    return result


class OCRService:
    """Real OCR using EasyOCR, with a lightweight preprocessing step
    (grayscale, contrast enhancement, denoising, upscaling) applied
    before OCR runs, to improve accuracy on photographed documents."""

    def extract_text(self, image_path: str, attempt: int) -> tuple[str, float]:
        reader = get_reader()

        try:
            preprocessed = preprocess_image(image_path)
            results = reader.readtext(preprocessed)
        except Exception as e:
            print(f"[OCRService ERROR] Preprocessing failed, falling back to raw image: {e}")
            results = reader.readtext(image_path)

        if not results:
            return "", 0.0

        lines = []
        confidences = []
        for (_, text, conf) in results:
            lines.append(text)
            confidences.append(conf)

        full_text = "\n".join(lines)
        avg_confidence = sum(confidences) / len(confidences)

        return full_text, round(avg_confidence, 2)