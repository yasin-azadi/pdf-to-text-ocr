import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QTextEdit, QFileDialog, QProgressBar, 
                              QLabel, QMessageBox, QListWidget, QFrame)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

# ---------- Keeping processing classes constant ----------
from core.ocr_engine import OCREngine
from core.pdf_processor import PDFProcessor
from core.docx_processor import DocxProcessor

class OCRWorker(QThread):
    progress_signal = Signal(int)
    status_signal = Signal(str)
    result_signal = Signal(str, str)
    error_signal = Signal(str)

    def __init__(self, file_paths, ocr_engine):
        super().__init__()
        self.file_paths = file_paths
        self.ocr_engine = ocr_engine
        self.pdf_processor = PDFProcessor(self.ocr_engine)
        self.docx_processor = DocxProcessor()

    def run(self):
        total_files = len(self.file_paths)
        all_results = []

        for index, file_path in enumerate(self.file_paths):
            file_name = os.path.basename(file_path)
            ext = file_name.lower().split('.')[-1]
            self.status_signal.emit(f"⚡ Processing ({index+1}/{total_files}): {file_name}")
            
            try:
                text_content = ""
                if ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif']:
                    self.progress_signal.emit(int(((index) / total_files) * 100) + 10)
                    text_content = self.ocr_engine.extract_text(file_path)
                elif ext == 'pdf':
                    def inner_callback(p):
                        base_p = int((index / total_files) * 100)
                        file_weight = int((p / 100) * (100 / total_files))
                        self.progress_signal.emit(base_p + file_weight)
                    
                    text_content = self.pdf_processor.process_pdf(file_path, inner_callback)
                elif ext == 'docx':
                    text_content = self.docx_processor.process_docx(file_path)
                    self.progress_signal.emit(int(((index + 1) / total_files) * 100))
                else:
                    text_content = f"⚠️ Unsupported file format: {file_name}"

                all_results.append(f"📄 === {file_name} ===\n{text_content}\n{'─'*50}\n")
                
            except Exception as e:
                self.error_signal.emit(f"❌ Error processing {file_name}: {str(e)}")
                continue

        self.progress_signal.emit(100)
        self.status_signal.emit("✅ Processing completed successfully!")
        self.result_signal.emit("".join(all_results), self.file_paths[0])


# ---------- New beautiful design ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📝 Offline OCR Converter - Dark Edition")
        self.setMinimumSize(900, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # ---------- Glass and dark style ----------
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
            }
            QWidget {
                background: transparent;
                border-radius: 12px;
            }
            QLabel#titleLabel {
                font-size: 28px;
                color: #e0e0e0;
                padding: 20px;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 20px;
                font-weight: bold;
            }
            QPushButton {
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.15);
                color: #e0e0e0;
                padding: 12px 24px;
                border-radius: 25px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.15);
                border: 1px solid #00d2ff;
                color: #ffffff;
            }
            QPushButton:pressed {
                background: rgba(0,210,255,0.2);
            }
            QPushButton#startBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f9b8e, stop:1 #00d2ff);
                border: none;
                font-size: 16px;
                letter-spacing: 1px;
                color: white;
                padding: 15px 30px;
            }
            QPushButton#startBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0e8d81, stop:1 #00b8e6);
            }
            QPushButton#clearBtn {
                background: rgba(255,82,82,0.8);
                border: none;
                color: white;
            }
            QPushButton#clearBtn:hover {
                background: #ff5252;
            }
            QPushButton#saveBtn {
                background: rgba(255,183,77,0.8);
                border: none;
                color: #1a1a2e;
            }
            QPushButton#saveBtn:hover {
                background: #ffb74d;
            }
            QPushButton:disabled {
                background: rgba(100,100,100,0.3);
                color: #666;
                border: 1px solid #444;
            }
            QListWidget {
                background: rgba(20,20,35,0.9);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 14px;
                padding: 8px;
                font-size: 13px;
                color: #ccc;
                outline: none;
            }
            QListWidget::item {
                border-radius: 8px;
                padding: 6px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background: rgba(0,210,255,0.25);
                color: #ffffff;
            }
            QTextEdit {
                background: rgba(15,15,25,0.9);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 16px;
                font-family: 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                color: #d4d4d4;
                padding: 12px;
                selection-background-color: #00d2ff;
            }
            QProgressBar {
                border: none;
                border-radius: 12px;
                background: rgba(255,255,255,0.08);
                height: 12px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f9b8e, stop:1 #00d2ff);
                border-radius: 12px;
            }
            QLabel {
                color: #b0b0b0;
                font-weight: normal;
                background: transparent;
            }
            QLabel#statusLabel {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px;
                padding: 10px 16px;
                font-size: 14px;
                color: #cccccc;
            }
            QFrame#mainFrame {
                background: rgba(20,20,35,0.4);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 30px;
                padding: 25px;
            }
        """)

        self.status_label = QLabel("🚀 Initializing offline OCR engine...")
        self.ocr_engine = None
        self.init_ui()
        self.selected_files = []

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(18)

        # Glass title
        title_label = QLabel("✦  Intelligent Text Extraction  ✦")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Main frame
        main_frame = QFrame()
        main_frame.setObjectName("mainFrame")
        main_layout.addWidget(main_frame)
        layout = QVBoxLayout(main_frame)
        layout.setSpacing(18)

        # Button row
        top_layout = QHBoxLayout()
        self.btn_select_files = QPushButton("📂 Select Files")
        self.btn_select_files.setMinimumHeight(48)
        self.btn_select_files.clicked.connect(self.select_files)

        self.btn_clear = QPushButton("🗑 Clear List")
        self.btn_clear.setObjectName("clearBtn")
        self.btn_clear.setMinimumHeight(48)
        self.btn_clear.clicked.connect(self.clear_list)

        top_layout.addWidget(self.btn_select_files)
        top_layout.addWidget(self.btn_clear)
        layout.addLayout(top_layout)

        # File list label
        file_label = QLabel("📋 Selected Files:")
        file_label.setStyleSheet("font-size: 15px; color: #aaaaaa; margin-top: 6px;")
        layout.addWidget(file_label)

        self.file_list_widget = QListWidget()
        self.file_list_widget.setMaximumHeight(130)
        self.file_list_widget.setAlternatingRowColors(False)
        layout.addWidget(self.file_list_widget)

        # Start button (Call to Action)
        self.btn_start = QPushButton("⚡ Start OCR")
        self.btn_start.setObjectName("startBtn")
        self.btn_start.setMinimumHeight(60)
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.clicked.connect(self.start_processing)
        layout.addWidget(self.btn_start)

        # Progress bar and status
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar, 3)

        self.status_label = QLabel("💡 Ready to start")
        self.status_label.setObjectName("statusLabel")
        progress_layout.addWidget(self.status_label, 2)
        layout.addLayout(progress_layout)

        # Output area
        text_label = QLabel("📝 Output Text:")
        text_label.setStyleSheet("font-size: 15px; color: #aaaaaa; margin-top: 6px;")
        layout.addWidget(text_label)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Extracted text will appear here...")
        self.text_edit.setMinimumHeight(260)
        layout.addWidget(self.text_edit)

        # Bottom row
        bottom_layout = QHBoxLayout()
        self.btn_save = QPushButton("💾 Save (.txt)")
        self.btn_save.setObjectName("saveBtn")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_output)
        bottom_layout.addWidget(self.btn_save)

        self.btn_clear_text = QPushButton("🧹 Clear Text")
        self.btn_clear_text.setObjectName("clearBtn")
        self.btn_clear_text.clicked.connect(lambda: self.text_edit.clear())
        bottom_layout.addWidget(self.btn_clear_text)
        layout.addLayout(bottom_layout)

        # Support information
        info_label = QLabel("🖼️ Images · 📄 PDF · 📃 Word (DOCX)")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        # Statistics
        self.stats_label = QLabel("📊 Ready")
        self.stats_label.setStyleSheet("color: #95a5a6; font-size: 13px;")
        self.stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_label)

    # Methods for file selection, processing, and saving - exactly as before
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select file", "", 
            "All Supported Files (*.pdf *.docx *.jpg *.jpeg *.png *.bmp *.tiff *.tif);;Images (*.jpg *.jpeg *.png *.bmp *.tiff);;PDF Files (*.pdf);;Word Files (*.docx)"
        )
        if files:
            self.selected_files.extend(files)
            self.selected_files = list(set(self.selected_files))
            self.file_list_widget.clear()
            for f in self.selected_files:
                file_size = os.path.getsize(f) / 1024
                item_text = f"📎 {os.path.basename(f)} ({file_size:.1f} KB)"
                self.file_list_widget.addItem(item_text)
            total_mb = sum(os.path.getsize(f) for f in self.selected_files) / 1024 / 1024
            self.stats_label.setText(f"📊 Files: {len(self.selected_files)} | Total size: {total_mb:.2f} MB")

    def clear_list(self):
        self.selected_files = []
        self.file_list_widget.clear()
        self.text_edit.clear()
        self.progress_bar.setValue(0)
        self.btn_save.setEnabled(False)
        self.status_label.setText("🗑️ List cleared")
        self.stats_label.setText("📊 Ready")

    def start_processing(self):
        if not self.selected_files:
            QMessageBox.warning(self, "⚠️ Error", "Please select at least one file first.")
            return

        self.btn_start.setEnabled(False)
        self.btn_select_files.setEnabled(False)
        self.btn_start.setText("⏳ Processing...")
        
        if not self.ocr_engine:
            self.status_label.setText("⏳ Loading PaddleOCR model...")
            try:
                self.ocr_engine = OCREngine()
            except Exception as e:
                QMessageBox.critical(self, "❌ Error", f"Local models failed to load:\n{str(e)}")
                self.btn_start.setEnabled(True)
                self.btn_select_files.setEnabled(True)
                self.btn_start.setText("⚡ Start OCR")
                return

        self.worker = OCRWorker(self.selected_files, self.ocr_engine)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.status_signal.connect(self.status_label.setText)
        self.worker.result_signal.connect(self.processing_finished)
        self.worker.error_signal.connect(self.show_error)
        self.worker.start()

    def processing_finished(self, text_result, first_file_path):
        self.text_edit.setPlainText(text_result)
        self.btn_start.setEnabled(True)
        self.btn_select_files.setEnabled(True)
        self.btn_save.setEnabled(True)
        self.btn_start.setText("⚡ Start OCR")
        
        word_count = len(text_result.split())
        char_count = len(text_result)
        self.status_label.setText(f"✅ Done! {word_count} words, {char_count} characters")
        QMessageBox.information(self, "✅ Success", f"Processing completed.\n{word_count} words extracted.")

    def show_error(self, error_msg):
        QMessageBox.warning(self, "⚠️ Error", error_msg)

    def save_output(self):
        if not self.text_edit.toPlainText().strip():
            QMessageBox.warning(self, "⚠️ Error", "No text to save.")
            return
            
        default_path = os.path.join(os.path.dirname(self.selected_files[0]), "ocr_output.txt") if self.selected_files else ""
        save_path, _ = QFileDialog.getSaveFileName(self, "💾 Save Text File", default_path, "Text Files (*.txt);;All Files (*.*)")
        
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(self.text_edit.toPlainText())
            self.status_label.setText(f"✅ Saved: {os.path.basename(save_path)}")
            QMessageBox.information(self, "✅ Save Successful", "File saved successfully.")