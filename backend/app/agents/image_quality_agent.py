import time

import cv2

from app.state.workflow_state import WorkflowState, WorkflowStatus, HistoryEntry

BLUR_THRESHOLD = 100.0  # Laplacian variance below this = too blurry
MIN_WIDTH = 300
MIN_HEIGHT = 300


class ImageQualityAgent:
    """Checks whether the uploaded document image is usable for OCR:
    blur (via Laplacian variance) and minimum resolution."""

    name = "ImageQualityAgent"

    def run(self, state: WorkflowState) -> WorkflowState:
        start = time.perf_counter()

        state.status = WorkflowStatus.CHECKING_QUALITY
        state.current_step = "image_quality_check"

        image_path = state.structured_data.get("_image_path")
        quality_ok = True
        reasons = []

        if not image_path:
            quality_ok = False
            reasons.append("no image path found")
        else:
            img = cv2.imread(image_path)
            if img is None:
                quality_ok = False
                reasons.append("image could not be read")
            else:
                height, width = img.shape[:2]
                if width < MIN_WIDTH or height < MIN_HEIGHT:
                    quality_ok = False
                    reasons.append(f"resolution too low ({width}x{height})")

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                if laplacian_var < BLUR_THRESHOLD:
                    quality_ok = False
                    reasons.append(f"image too blurry (sharpness={laplacian_var:.1f})")

        reason_summary = "; ".join(reasons) if reasons else "quality acceptable"
        duration_ms = (time.perf_counter() - start) * 1000

        state.add_history(HistoryEntry(
            agent=self.name,
            input_summary=f"image_path={image_path}",
            output_summary=reason_summary,
            decision="pass" if quality_ok else "fail",
            duration_ms=duration_ms,
        ))

        if not quality_ok:
            state.validation_errors.append(f"Image quality insufficient: {reason_summary}")
            state.human_review_required = True

        return state