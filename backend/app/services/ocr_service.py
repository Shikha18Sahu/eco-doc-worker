import easyocr

_reader = None


def get_reader():
    """Lazy-load EasyOCR reader once (loading it per-request is slow)."""
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


class OCRService:
    """Real OCR using EasyOCR. Reads text from an image file path."""

    def extract_text(self, image_path: str, attempt: int) -> tuple[str, float]:
        reader = get_reader()
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