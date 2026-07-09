import os
from pypdf import PdfReader
from pdf2image import convert_from_path

class PDFProcessor:
    def __init__(self, ocr_engine):
        self.ocr_engine = ocr_engine

    def process_pdf(self, pdf_path, progress_callback=None):
        """Intelligent processing of PDF files (text-based or scanned)"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")

        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        extracted_text = []

        # 1. Attempt to extract digital text
        is_digital = False
        digital_text_buffer = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                digital_text_buffer.append(f"--- Page {i+1} ---\n{text}")
                is_digital = True
            if progress_callback:
                # Update phase 1 (initial check)
                progress_callback(int(((i + 1) / total_pages) * 30))

        if is_digital:
            return "\n\n".join(digital_text_buffer)

        # 2. If the PDF was scanned (image-based), convert to images and run OCR
        # Note: On Windows, Poppler must be installed, which is passed in the method.
        try:
            pages = convert_from_path(pdf_path, dpi=200)
            total_converted_pages = len(pages)
            
            # Create a temporary folder to store page images
            temp_dir = os.path.join(os.path.dirname(pdf_path), "temp_ocr_proc")
            os.makedirs(temp_dir, exist_ok=True)
            
            ocr_text_buffer = []
            for index, page in enumerate(pages):
                image_path = os.path.join(temp_dir, f"page_{index}.png")
                page.save(image_path, "PNG")
                
                # Run OCR on the page image
                page_text = self.ocr_engine.extract_text(image_path)
                ocr_text_buffer.append(f"--- Page {index+1} (OCR) ---\n{page_text}")
                
                # Delete temporary image after processing
                if os.path.exists(image_path):
                    os.remove(image_path)
                
                if progress_callback:
                    # Update phase 2 (from 30 to 100 percent)
                    actual_progress = 30 + int(((index + 1) / total_converted_pages) * 70)
                    progress_callback(actual_progress)
            
            # Remove temporary folder
            os.rmdir(temp_dir)
            return "\n\n".join(ocr_text_buffer)
            
        except Exception as e:
            raise Exception(f"Error processing PDF image (Poppler is probably not installed): {str(e)}")