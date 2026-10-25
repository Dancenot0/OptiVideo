import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QProgressBar, QTextEdit, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, QSize
from core.engine import OptimizationEngine
from ui.icons import Icons

class MainWindow(QMainWindow):
    """
    Minimalist UI for OptiVidio.
    Follows Apple/Windows 11 design principles.
    """
    def __init__(self):
        super().__init__()
        self.selected_path = None
        self.engine = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("OptiVidio")
        self.setMinimumSize(650, 800)
        self.setup_styles()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(24)

        # Header Section
        header_layout = QVBoxLayout()
        title_label = QLabel("OptiVidio")
        title_label.setObjectName("TitleLabel")
        subtitle_label = QLabel("Professional media optimization without quality loss")
        subtitle_label.setObjectName("SubtitleLabel")
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addLayout(header_layout)

        # Drop Zone / File Picker Card
        self.drop_card = QFrame()
        self.drop_card.setObjectName("DropCard")
        self.drop_card.setMinimumHeight(200) # Prevenir colapso
        drop_layout = QVBoxLayout(self.drop_card)
        drop_layout.setContentsMargins(32, 32, 32, 32)
        drop_layout.setSpacing(16)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setPixmap(Icons.get_icon(Icons.FILE_VIDEO, "#4dabf7", QSize(48, 48)).pixmap(48, 48))
        
        self.file_status = QLabel("Drag and drop your file here or click to browse")
        self.file_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_status.setObjectName("FileStatus")

        self.select_btn = QPushButton("Browse Files")
        self.select_btn.setIcon(Icons.get_icon(Icons.FOLDER_OPEN, "#ffffff", QSize(18, 18)))
        self.select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.select_btn.clicked.connect(self.handle_file_selection)
        self.select_btn.setFixedWidth(180)
        
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        btn_container.addWidget(self.select_btn)
        btn_container.addStretch()

        drop_layout.addWidget(self.icon_label)
        drop_layout.addWidget(self.file_status)
        drop_layout.addLayout(btn_container)
        main_layout.addWidget(self.drop_card)

        # Settings Card
        settings_card = QFrame()
        settings_card.setObjectName("SettingsCard")
        settings_card.setFixedHeight(120) # Altura fija para evitar squashing
        settings_layout = QHBoxLayout(settings_card)
        settings_layout.setContentsMargins(24, 24, 24, 24)
        settings_layout.setSpacing(32)

        # Codec Choice
        codec_vbox = QVBoxLayout()
        codec_vbox.addWidget(QLabel("Video Codec"))
        self.codec_choice = QComboBox()
        self.codec_choice.addItems(["libx265", "libx264"])
        codec_vbox.addWidget(self.codec_choice)
        settings_layout.addLayout(codec_vbox)

        # Quality Choice
        quality_vbox = QVBoxLayout()
        quality_vbox.addWidget(QLabel("Target Quality"))
        self.quality_choice = QComboBox()
        self.quality_choice.addItem("Visual Lossless (CRF 20)", 20)
        self.quality_choice.addItem("Standard Balance (CRF 24)", 24)
        self.quality_choice.addItem("Maximum Efficiency (CRF 28)", 28)
        self.quality_choice.setCurrentIndex(1)
        quality_vbox.addWidget(self.quality_choice)
        settings_layout.addLayout(quality_vbox)

        # Output Format Choice
        format_vbox = QVBoxLayout()
        format_vbox.addWidget(QLabel("Output Format"))
        self.format_choice = QComboBox()
        self.format_choice.addItems(["mp4", "mkv", "mov", "mp3", "wav", "m4a"])
        format_vbox.addWidget(self.format_choice)
        settings_layout.addLayout(format_vbox)

        main_layout.addWidget(settings_card)

        # Action and Progress Section
        self.run_btn = QPushButton("Optimize Now")
        self.run_btn.setObjectName("PrimaryButton")
        self.run_btn.setEnabled(False)
        self.run_btn.setFixedHeight(50)
        self.run_btn.setIcon(Icons.get_icon(Icons.PLAY, "#ffffff", QSize(20, 20)))
        self.run_btn.clicked.connect(self.process_media)
        main_layout.addWidget(self.run_btn)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setVisible(False)
        self.console.setMaximumHeight(150) # Limitar altura para no empujar todo
        main_layout.addWidget(self.console)

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0f111a; }
            QWidget { font-family: 'Segoe UI', 'Inter', sans-serif; color: #e6edf3; }
            
            #TitleLabel { font-size: 32px; font-weight: 700; color: #ffffff; }
            #SubtitleLabel { font-size: 14px; color: #8b949e; margin-bottom: 8px; }
            
            #DropCard { 
                background-color: #161b22; 
                border: 2px dashed #30363d; 
                border-radius: 12px; 
            }
            #DropCard[selected="true"] { border-color: #2f81f7; border-style: solid; background-color: #1c2128; }
            
            #FileStatus { font-size: 16px; color: #c9d1d9; font-weight: 500; }
            
            #SettingsCard { 
                background-color: #161b22; 
                border-radius: 12px; 
                border: 1px solid #30363d;
            }
            
            QLabel { font-size: 13px; color: #8b949e; font-weight: 600; }
            
            QPushButton {
                background-color: #21262d;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                color: #c9d1d9;
            }
            QPushButton:hover { background-color: #30363d; border-color: #8b949e; }
            QPushButton:pressed { background-color: #161b22; }
            
            #PrimaryButton {
                background-color: #238636;
                color: #ffffff;
                border: none;
                font-size: 15px;
            }
            #PrimaryButton:hover { background-color: #2ea043; }
            #PrimaryButton:disabled { background-color: #21262d; color: #484f58; }
            
            QComboBox {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 200px;
                min-height: 20px;
                color: #c9d1d9;
            }
            QComboBox:hover { border-color: #58a6ff; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox QAbstractItemView {
                background-color: #161b22;
                border: 1px solid #30363d;
                selection-background-color: #1f6feb;
                selection-color: #ffffff;
                outline: none;
                color: #c9d1d9;
            }
            
            QProgressBar {
                height: 8px;
                background-color: #30363d;
                border-radius: 4px;
                border: none;
                text-align: transparent;
            }
            QProgressBar::chunk {
                background-color: #2f81f7;
                border-radius: 4px;
            }
            
            QTextEdit {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 8px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                color: #7ee787;
                padding: 12px;
            }
        """)

    def handle_file_selection(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Media", "", 
            "All Media (*.mp4 *.mkv *.avi *.mov *.mp3 *.wav *.m4a)"
        )
        if path:
            self.selected_path = path
            self.file_status.setText(os.path.basename(path))
            self.drop_card.setProperty("selected", "true")
            self.drop_card.style().unpolish(self.drop_card)
            self.drop_card.style().polish(self.drop_card)
            self.run_btn.setEnabled(True)

    def process_media(self):
        if not self.selected_path: return

        base, _ = os.path.splitext(self.selected_path)
        output_ext = f".{self.format_choice.currentText()}"
        out_path = f"{base}_optimized{output_ext}"
        
        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.console.setVisible(True)
        self.console.clear()

        self.engine = OptimizationEngine(
            self.selected_path, out_path, 
            self.codec_choice.currentText(), self.quality_choice.currentData()
        )
        self.engine.log.connect(lambda t: self.console.append(t))
        self.engine.finished.connect(self.handle_finish)
        self.engine.start()

    def handle_finish(self, success, result):
        self.progress.setRange(0, 100)
        self.run_btn.setEnabled(True)
        self.progress.setValue(100 if success else 0)
        
        if success:
            self.icon_label.setPixmap(Icons.get_icon(Icons.CHECK_CIRCLE, "#28a745", QSize(48, 48)).pixmap(48, 48))
            self.console.append(f"\nSUCCESS: Optimization complete.\nSaved as: {result}")
        else:
            self.icon_label.setPixmap(Icons.get_icon(Icons.ALERT_CIRCLE, "#dc3545", QSize(48, 48)).pixmap(48, 48))
            self.console.append(f"\nFAILURE: {result}")
