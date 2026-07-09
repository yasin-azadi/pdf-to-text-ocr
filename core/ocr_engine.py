import os
import sys

from paddleocr import PaddleOCR


class OCREngine:
    def __init__(self):

        # Compatible with PyInstaller
        if getattr(sys, "frozen", False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )

        models_dir = os.path.join(base_dir, "models")

        det_dir = os.path.join(models_dir, "det")
        rec_dir = os.path.join(models_dir, "rec")

        if not os.path.isdir(det_dir):
            raise FileNotFoundError(det_dir)

        if not os.path.isdir(rec_dir):
            raise FileNotFoundError(rec_dir)

        self.ocr = PaddleOCR(
            # -------- Detection --------
            text_detection_model_name="PP-OCRv6_small_det",
            text_detection_model_dir=det_dir,

            # -------- Recognition --------
            text_recognition_model_name="PP-OCRv6_small_rec",
            text_recognition_model_dir=rec_dir,

            # -------- Optional modules --------
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,

            device="cpu",
            enable_hpi=False
        )

    def extract_text(self, image_path: str) -> str:

        if not os.path.exists(image_path):
            raise FileNotFoundError(image_path)

        results = self.ocr.predict(image_path)

        texts = []

        for result in results:

            if hasattr(result, "rec_texts"):
                texts.extend(result.rec_texts)

            elif hasattr(result, "res"):
                texts.extend(result.res.get("rec_texts", []))

            elif isinstance(result, dict):
                texts.extend(result.get("rec_texts", []))

        return "\n".join(texts)