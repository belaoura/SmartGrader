import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame,
                             QMessageBox, QDesktopWidget, QComboBox,
                             QDialog, QDialogButtonBox, QFormLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from exam_form import ExamForm
from question_form import QuestionForm
from database import get_exams, get_questions_with_choices, get_exam_statistics

# Import the answer sheet generator
from generate_qcm_sheet import generate_exam_sheet

class ExamSelectionDialog(QDialog):
    """Dialog to select an exam for generating answer sheet"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Exam")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # Set style
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QComboBox {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                min-height: 20px;
                background-color: white;
            }
            QComboBox:focus {
                border: 2px solid #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                width: 0;
                height: 0;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton#cancel {
                background-color: #9e9e9e;
            }
            QPushButton#cancel:hover {
                background-color: #757575;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("📄 Generate Answer Sheet")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form layout
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Exam selection
        self.exam_combo = QComboBox()
        self.exam_combo.setMinimumHeight(40)
        form_layout.addRow("Select Exam:", self.exam_combo)
        
        layout.addWidget(form_widget)
        
        # Load exams
        self.load_exams()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Style buttons
        for button in button_box.buttons():
            if button_box.buttonRole(button) == QDialogButtonBox.AcceptRole:
                button.setText("Generate")
                button.setStyleSheet("background-color: #4CAF50;")
            else:
                button.setObjectName("cancel")
        
        layout.addWidget(button_box)
    
    def load_exams(self):
        """Load exams into combobox"""
        self.exam_combo.clear()
        exams = get_exams()
        
        if exams:
            for exam in exams:
                self.exam_combo.addItem(f"{exam[1]} (ID: {exam[0]})", exam[0])
        else:
            self.exam_combo.addItem("No exams available")
    
    def get_selected_exam_id(self):
        """Get the ID of the selected exam"""
        return self.exam_combo.currentData()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart QCM Grader - Exam Management System")
        self.setGeometry(100, 100, 1000, 650)
        
        # Center window on screen
        self.center_window()
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QFrame#header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #1976D2);
                border-bottom: 3px solid #0D47A1;
            }
            QFrame#card {
                background-color: white;
                border-radius: 15px;
                padding: 25px;
            }
            QLabel#title {
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
            QLabel#subtitle {
                color: rgba(255,255,255,0.9);
                font-size: 14px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 18px 25px;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                min-width: 250px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1976D2;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton#exam_btn {
                background-color: #4CAF50;
            }
            QPushButton#exam_btn:hover {
                background-color: #388E3C;
            }
            QPushButton#question_btn {
                background-color: #FF9800;
            }
            QPushButton#question_btn:hover {
                background-color: #F57C00;
            }
            QPushButton#generate_btn {
                background-color: #9C27B0;
            }
            QPushButton#generate_btn:hover {
                background-color: #7B1FA2;
            }
            QPushButton#exit_btn {
                background-color: #f44336;
            }
            QPushButton#exit_btn:hover {
                background-color: #d32f2f;
            }
            QLabel#stat_label {
                font-size: 16px;
                color: #666;
            }
            QLabel#stat_value {
                font-size: 24px;
                font-weight: bold;
                color: #2196F3;
            }
            QStatusBar {
                background-color: #2196F3;
                color: white;
                padding: 5px;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.create_header(main_layout)
        
        # Content
        self.create_content(main_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        
        # Load statistics
        self.load_statistics()
    
    def center_window(self):
        """Center window on screen"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def create_header(self, layout):
        """Create header with title"""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(120)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        # Title container
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(5)
        
        title = QLabel("📚 Smart QCM Grader")
        title.setObjectName("title")
        title_layout.addWidget(title)
        
        subtitle = QLabel("Exam and Question Management System")
        subtitle.setObjectName("subtitle")
        title_layout.addWidget(subtitle)
        
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        
        # Date and time
        self.time_label = QLabel()
        self.time_label.setObjectName("subtitle")
        self.update_time()
        header_layout.addWidget(self.time_label)
        
        # Update time every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        layout.addWidget(header)
    
    def create_content(self, layout):
        """Create main content area"""
        content = QFrame()
        content.setContentsMargins(30, 30, 30, 30)
        content_layout = QHBoxLayout(content)
        content_layout.setSpacing(30)
        
        # Left panel - Main actions
        left_panel = QFrame()
        left_panel.setObjectName("card")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)
        
        welcome_label = QLabel("Welcome!")
        welcome_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #333;")
        left_layout.addWidget(welcome_label)
        
        desc_label = QLabel(
            "Smart QCM Grader helps you create and manage exams, "
            "questions, and automatically grade multiple-choice tests.\n\n"
            "Choose an action below to get started:"
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; font-size: 14px; line-height: 1.5;")
        left_layout.addWidget(desc_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #e0e0e0; margin: 10px 0;")
        left_layout.addWidget(separator)
        
        # Action buttons with icons
        self.exam_btn = QPushButton("📝  Add New Exam")
        self.exam_btn.setObjectName("exam_btn")
        self.exam_btn.setMinimumHeight(60)
        self.exam_btn.clicked.connect(self.open_exam_form)
        left_layout.addWidget(self.exam_btn)
        
        self.question_btn = QPushButton("❓  Add New Question")
        self.question_btn.setObjectName("question_btn")
        self.question_btn.setMinimumHeight(60)
        self.question_btn.clicked.connect(self.open_question_form)
        left_layout.addWidget(self.question_btn)
        
        # NEW: Generate Answer Sheet Button
        self.generate_btn = QPushButton("📄  Generate Answer Sheet")
        self.generate_btn.setObjectName("generate_btn")
        self.generate_btn.setMinimumHeight(60)
        self.generate_btn.clicked.connect(self.generate_answer_sheet)
        left_layout.addWidget(self.generate_btn)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet("background-color: #e0e0e0; margin: 10px 0;")
        left_layout.addWidget(separator2)
        
        self.exit_btn = QPushButton("🚪  Exit")
        self.exit_btn.setObjectName("exit_btn")
        self.exit_btn.setMinimumHeight(60)
        self.exit_btn.clicked.connect(self.close)
        left_layout.addWidget(self.exit_btn)
        
        left_layout.addStretch()
        
        content_layout.addWidget(left_panel)
        
        # Right panel - Statistics
        right_panel = QFrame()
        right_panel.setObjectName("card")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(20)
        
        stats_title = QLabel("📊 System Statistics")
        stats_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px;")
        right_layout.addWidget(stats_title)
        
        # Statistics cards
        self.stats_widget = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_widget)
        self.stats_layout.setSpacing(15)
        
        # Total Exams
        exam_stats = self.create_stat_card("📚 Total Exams", "0", "#4CAF50")
        self.stats_layout.addWidget(exam_stats)
        self.total_exams_label = exam_stats.findChild(QLabel, "value")
        
        # Total Questions
        question_stats = self.create_stat_card("❓ Total Questions", "0", "#FF9800")
        self.stats_layout.addWidget(question_stats)
        self.total_questions_label = question_stats.findChild(QLabel, "value")
        
       
        # Exams with questions
        exam_with_q_stats = self.create_stat_card("📋 Exams with Questions", "0", "#2196F3")
        self.stats_layout.addWidget(exam_with_q_stats)
        self.exams_with_q_label = exam_with_q_stats.findChild(QLabel, "value")
        
        right_layout.addWidget(self.stats_widget)
        right_layout.addStretch()
        
        content_layout.addWidget(right_panel)
        
        # Set equal width for panels
        left_panel.setMinimumWidth(450)
        right_panel.setMinimumWidth(350)
        
        layout.addWidget(content)
    
    def create_stat_card(self, title, value, color):
        """Create a statistics card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #f8f9fa;
                border-radius: 12px;
                padding: 15px;
                border-left: 5px solid {color};
            }}
        """)
        layout = QHBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        layout.addWidget(value_label)
        
        return card
    
    def update_time(self):
        """Update time in header"""
        from datetime import datetime
        current_time = datetime.now().strftime("%d %B %Y - %H:%M:%S")
        self.time_label.setText(f"📅 {current_time}")
    
    def load_statistics(self):
        """Load system statistics"""
        try:
            exams = get_exams()
            questions = get_questions_with_choices()
            
            self.total_exams_label.setText(str(len(exams)))
            self.total_questions_label.setText(str(len(questions)))
            
            
            
            # Count exams that have questions
            exams_with_questions = len(set(q['exam_id'] for q in questions))
            self.exams_with_q_label.setText(str(exams_with_questions))
                
        except Exception as e:
            self.statusBar().showMessage(f"Error loading statistics: {str(e)}")
    
    def open_exam_form(self):
        """Open exam creation form"""
        try:
            self.exam_form = ExamForm()
            self.exam_form.exam_added.connect(self.on_exam_added)
            self.exam_form.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open exam form: {str(e)}")
    
    def open_question_form(self):
        """Open question creation form"""
        try:
            # Check if exams exist
            exams = get_exams()
            if not exams:
                reply = QMessageBox.question(
                    self, 
                    "No Exams",
                    "No exams found. Would you like to create an exam first?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    self.open_exam_form()
                return
            
            self.question_form = QuestionForm()
            self.question_form.question_added.connect(self.on_question_added)
            self.question_form.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open question form: {str(e)}")
    
    def generate_answer_sheet(self):
        """Generate answer sheet for selected exam"""
        try:
            # Check if exams exist
            exams = get_exams()
            if not exams:
                QMessageBox.warning(
                    self,
                    "No Exams",
                    "No exams found. Please create an exam first."
                )
                return
            
            # Show exam selection dialog
            dialog = ExamSelectionDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                exam_id = dialog.get_selected_exam_id()
                
                if exam_id is None:
                    QMessageBox.warning(self, "Warning", "Please select a valid exam.")
                    return
                
                # Get exam details
                exam_info = next((e for e in exams if e[0] == exam_id), None)
                if exam_info:
                    exam_title = exam_info[1]
                else:
                    exam_title = f"Exam ID: {exam_id}"
                
                # Check if exam has questions
                questions = get_questions_with_choices()
                exam_questions = [q for q in questions if q['exam_id'] == exam_id]
                
                if not exam_questions:
                    QMessageBox.warning(
                        self,
                        "No Questions",
                        f"The selected exam '{exam_title}' has no questions.\n"
                        "Please add questions to the exam first."
                    )
                    return
                
                # Confirm generation
                reply = QMessageBox.question(
                    self,
                    "Confirm Generation",
                    f"Generate answer sheet for:\n\n"
                    f"Exam: {exam_title}\n"
                    f"Questions: {len(exam_questions)}\n\n"
                    f"This will create a printable QCM answer sheet.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    self.statusBar().showMessage(f"Generating answer sheet for {exam_title}...")
                    
                    result = generate_exam_sheet(exam_id)
                    
                    if result:
                        html_path, pdf_path = result
                        
                        if html_path and os.path.exists(html_path):
                            self.statusBar().showMessage(f"Answer sheet generated successfully!", 5000)
                            
                            msg = "Answer sheet generated successfully!\n\n"
                            msg += f"📄 HTML: {html_path}\n"
                            if pdf_path and os.path.exists(pdf_path):
                                msg += f"📑 PDF: {pdf_path}\n"
                            
                            open_reply = QMessageBox.question(
                                self,
                                "Success",
                                msg + "\nWould you like to open the files?",
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes
                            )
                            
                            if open_reply == QMessageBox.Yes:
                                self.open_file(html_path)
                                if pdf_path and os.path.exists(pdf_path):
                                    self.open_file(pdf_path)
                        else:
                            QMessageBox.critical(
                                self,
                                "Generation Failed",
                                "Failed to generate answer sheet. Please check the console for errors."
                            )
                            self.statusBar().showMessage("Answer sheet generation failed!", 5000)
                    else:
                        QMessageBox.critical(
                            self,
                            "Generation Failed",
                            "Failed to generate answer sheet. No result returned."
                        )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate answer sheet:\n{str(e)}")
            self.statusBar().showMessage("Error generating answer sheet!", 5000)
    
    def open_file(self, filepath):
        """Open a file with the default application"""
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
        except Exception as e:
            QMessageBox.information(
                self,
                "File Location",
                f"The file was saved to:\n{filepath}"
            )
    
    def on_exam_added(self):
        """Handle exam added event"""
        self.load_statistics()
        self.statusBar().showMessage("Exam added successfully!", 3000)
    
    def on_question_added(self):
        """Handle question added event"""
        self.load_statistics()
        self.statusBar().showMessage("Question added successfully!", 3000)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()