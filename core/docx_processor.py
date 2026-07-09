import os
import docx2txt

class DocxProcessor:
    @staticmethod
    def process_docx(docx_path):
        
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"فایل Word یافت نشد: {docx_path}")
            
        text = docx2txt.process(docx_path)
        return text if text else ""
