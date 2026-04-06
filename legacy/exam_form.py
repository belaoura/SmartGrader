import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFormLayout,
                             QDateEdit, QSpinBox, QWidget, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon

from database import insert_exam

class ExamForm(QDialog):
    exam_added = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Exam")
        self.setGeometry(400, 300, 550, 450)
        self.setModal(True)
        
        # Set window icon (if you have one)
        # self.setWindowIcon(QIcon('icon.png'))
        
        # Set style
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QFrame#header {
                background-color: #2196F3;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            QFrame#content {
                background-color: white;
                border-radius: 10px;
            }
            QLabel#title {
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit, QDateEdit, QSpinBox {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                min-height: 20px;
                background-color: white;
            }
            QLineEdit:focus, QDateEdit:focus, QSpinBox:focus {
                border: 2px solid #2196F3;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton#cancel {
                background-color: #f44336;
            }
            QPushButton#cancel:hover {
                background-color: #d32f2f;
            }
            QDateEdit {
                padding-right: 30px;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        
        header_title = QLabel("📝 Create New Exam")
        header_title.setObjectName("title")
        header_title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(header_title)
        
        main_layout.addWidget(header)
        
        # Content
        content = QFrame()
        content.setObjectName("content")
        content.setContentsMargins(30, 30, 30, 30)
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Form layout
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Exam title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., Mathematics Final Exam")
        self.title_input.setMinimumWidth(300)
        form_layout.addRow("Exam Title:", self.title_input)
        
        # Subject
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("e.g., Mathematics")
        form_layout.addRow("Subject:", self.subject_input)
        
        # Date
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Exam Date:", self.date_input)
        
        # Total marks
        self.marks_input = QSpinBox()
        self.marks_input.setRange(1, 1000)
        self.marks_input.setValue(100)
        self.marks_input.setSuffix(" points")
        form_layout.addRow("Total Marks:", self.marks_input)
        
        content_layout.addWidget(form_widget)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #e0e0e0;")
        content_layout.addWidget(separator)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.save_btn = QPushButton("✓ Save Exam")
        self.save_btn.clicked.connect(self.save_exam)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("✗ Cancel")
        self.cancel_btn.setObjectName("cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content)
    
    def save_exam(self):
        """Save exam to database"""
        # Validate inputs
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.critical(self, "Validation Error", 
                               "Exam title is required!")
            self.title_input.setFocus()
            return
        
        subject = self.subject_input.text().strip()
        if not subject:
            QMessageBox.critical(self, "Validation Error", 
                               "Subject is required!")
            self.subject_input.setFocus()
            return
        
        date = self.date_input.date().toString("yyyy-MM-dd")
        marks = self.marks_input.value()
        
        try:
            # Insert exam
            exam_id = insert_exam(
                title=title,
                subject=subject,
                date=date,
                total_marks=marks
            )
            
            # Show success message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Success")
            msg.setText("Exam created successfully!")
            msg.setInformativeText(f"Exam ID: {exam_id}\nTitle: {title}\nSubject: {subject}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
            # Emit signal
            self.exam_added.emit()
            
            # Close dialog
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", 
                               f"Failed to create exam:\n{str(e)}")