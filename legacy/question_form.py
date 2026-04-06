from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QTextEdit, QSpinBox, QPushButton,
                             QGroupBox, QRadioButton, QCheckBox, QButtonGroup,
                             QMessageBox, QWidget, QGridLayout, QFrame,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QLineEdit, QScrollArea, QSplitter, QSizePolicy,
                             QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

from database import get_exams, insert_question, insert_choice, get_questions_with_choices

class QuestionForm(QDialog):
    question_added = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Question")
        self.setWindowState(Qt.WindowMaximized)  # Start maximized
        self.setModal(True)
        
        # Set minimum size
        self.setMinimumSize(1200, 700)
        
        # Set style
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f2f5;
            }
            QFrame#header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #1976D2);
                min-height: 70px;
                max-height: 70px;
            }
            QLabel#header_title {
                color: white;
                font-size: 22px;
                font-weight: bold;
                padding-left: 25px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 12px 0 12px;
                color: #2196F3;
                background-color: white;
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
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton#secondary {
                background-color: #9e9e9e;
            }
            QPushButton#secondary:hover {
                background-color: #757575;
            }
            QPushButton#success {
                background-color: #4CAF50;
            }
            QPushButton#success:hover {
                background-color: #388E3C;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                min-height: 20px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 2px solid #2196F3;
            }
            QTableWidget {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                gridline-color: #f0f0f0;
                font-size: 13px;
                alternate-background-color: #f9f9f9;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QRadioButton, QCheckBox {
                font-size: 14px;
                spacing: 10px;
            }
            QRadioButton::indicator, QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar:horizontal {
                border: none;
                background-color: #f0f0f0;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-width: 30px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #a0a0a0;
            }
            QSplitter::handle {
                background-color: #e0e0e0;
                width: 2px;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.create_header(main_layout)
        
        # Content with splitter
        content = QFrame()
        content.setContentsMargins(20, 20, 20, 20)
        content_layout = QHBoxLayout(content)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setChildrenCollapsible(False)
        content_layout.addWidget(splitter)
        
        # Left panel - Input form (with scroll)
        left_panel = self.create_input_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Preview (with scroll)
        right_panel = self.create_preview_panel()
        splitter.addWidget(right_panel)
        
        # Set initial sizes (40% left, 60% right)
        screen_width = QApplication.primaryScreen().availableGeometry().width()
        splitter.setSizes([int(screen_width * 0.4), int(screen_width * 0.6)])
        
        main_layout.addWidget(content)
        
        # Load exams
        self.load_exams()
        
        # Connect exam selection change to update preview
        self.exam_combo.currentIndexChanged.connect(self.on_exam_changed)
        
        # Load initial preview
        self.load_preview()
    
    def create_header(self, layout):
        """Create header"""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(70)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        header_title = QLabel("➕ Add New Question")
        header_title.setObjectName("header_title")
        header_layout.addWidget(header_title)
        
        header_layout.addStretch()
        
        # Add exam info
        self.header_exam_label = QLabel("No exam selected")
        self.header_exam_label.setStyleSheet("color: white; font-size: 14px; padding-right: 20px;")
        header_layout.addWidget(self.header_exam_label)
        
        layout.addWidget(header)
    
    def create_input_panel(self):
        """Create the input form panel with scroll"""
        panel = QFrame()
        panel.setObjectName("card")
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Main layout for panel
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for input form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(15, 15, 15, 15)
        
        # Exam selection
        exam_group = QGroupBox("📋 Exam Information")
        exam_layout = QVBoxLayout()
        exam_layout.setSpacing(12)
        
        self.exam_combo = QComboBox()
        self.exam_combo.setMinimumHeight(40)
        self.exam_combo.setPlaceholderText("Select an exam...")
        exam_layout.addWidget(QLabel("Select Exam:"))
        exam_layout.addWidget(self.exam_combo)
        
        exam_group.setLayout(exam_layout)
        container_layout.addWidget(exam_group)
        
        # Question details
        question_group = QGroupBox("❓ Question Details")
        question_layout = QVBoxLayout()
        question_layout.setSpacing(12)
        
        question_layout.addWidget(QLabel("Question Text:"))
        self.question_text = QTextEdit()
        self.question_text.setMinimumHeight(120)
        self.question_text.setMaximumHeight(150)
        self.question_text.setPlaceholderText("Enter your question here...")
        question_layout.addWidget(self.question_text)
        
        marks_layout = QHBoxLayout()
        marks_layout.addWidget(QLabel("Marks:"))
        self.marks_spin = QSpinBox()
        self.marks_spin.setRange(1, 100)
        self.marks_spin.setValue(1)
        self.marks_spin.setMinimumHeight(35)
        self.marks_spin.setSuffix(" points")
        self.marks_spin.setFixedWidth(150)
        marks_layout.addWidget(self.marks_spin)
        marks_layout.addStretch()
        question_layout.addLayout(marks_layout)
        
        question_group.setLayout(question_layout)
        container_layout.addWidget(question_group)
        
        # Choices configuration
        config_group = QGroupBox("⚙️ Choices Configuration")
        config_layout = QGridLayout()
        config_layout.setVerticalSpacing(15)
        config_layout.setHorizontalSpacing(20)
        
        config_layout.addWidget(QLabel("Number of choices:"), 0, 0)
        self.choice_count = QSpinBox()
        self.choice_count.setRange(2, 6)
        self.choice_count.setValue(4)
        self.choice_count.setMinimumHeight(35)
        self.choice_count.setFixedWidth(100)
        self.choice_count.valueChanged.connect(self.rebuild_choices)
        config_layout.addWidget(self.choice_count, 0, 1)
        
        config_layout.addWidget(QLabel("Multiple correct answers:"), 1, 0)
        self.multiple_correct = QCheckBox()
        self.multiple_correct.stateChanged.connect(self.rebuild_choices)
        config_layout.addWidget(self.multiple_correct, 1, 1)
        
        config_group.setLayout(config_layout)
        container_layout.addWidget(config_group)
        
        # Choices
        self.choices_group = QGroupBox("🔤 Answer Choices")
        self.choices_layout = QVBoxLayout()
        self.choices_group.setLayout(self.choices_layout)
        
        # Scroll area for choices
        choices_scroll = QScrollArea()
        choices_scroll.setWidgetResizable(True)
        choices_scroll.setFrameShape(QFrame.NoFrame)
        choices_scroll.setMinimumHeight(250)
        choices_scroll.setMaximumHeight(350)
        choices_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        choices_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        choices_container = QWidget()
        self.choices_inner_layout = QVBoxLayout(choices_container)
        self.choices_inner_layout.setSpacing(10)
        self.choices_inner_layout.setContentsMargins(5, 5, 5, 5)
        choices_scroll.setWidget(choices_container)
        
        self.choices_layout.addWidget(choices_scroll)
        container_layout.addWidget(self.choices_group)
        
        # Initialize choices
        self.choice_widgets = []
        self.rebuild_choices()
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        self.save_btn = QPushButton("💾 Save Question")
        self.save_btn.setObjectName("success")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.clicked.connect(self.save_question)
        button_layout.addWidget(self.save_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear Form")
        self.clear_btn.setObjectName("secondary")
        self.clear_btn.setMinimumHeight(45)
        self.clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_btn)
        
        container_layout.addLayout(button_layout)
        container_layout.addStretch()
        
        # Set container as scroll area widget
        scroll.setWidget(container)
        panel_layout.addWidget(scroll)
        
        return panel
    
    def create_preview_panel(self):
        """Create the preview panel with scroll"""
        panel = QFrame()
        panel.setObjectName("card")
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Main layout for panel
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(15, 15, 15, 15)
        panel_layout.setSpacing(15)
        
        # Preview header with exam info
        preview_header = QFrame()
        preview_header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        header_layout = QHBoxLayout(preview_header)
        
        header_title = QLabel("📋 Questions Preview")
        header_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2196F3;
        """)
        header_layout.addWidget(header_title)
        
        header_layout.addStretch()
        
        self.exam_filter_label = QLabel("Showing all exams")
        self.exam_filter_label.setStyleSheet("color: #666; font-size: 13px; padding: 5px 10px; background-color: #f0f0f0; border-radius: 5px;")
        header_layout.addWidget(self.exam_filter_label)
        
        panel_layout.addWidget(preview_header)
        
        # Search bar
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(15, 10, 15, 10)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 18px;")
        search_layout.addWidget(search_icon)
        
        self.preview_search = QLineEdit()
        self.preview_search.setPlaceholderText("Search questions...")
        self.preview_search.setStyleSheet("border: none; font-size: 14px;")
        self.preview_search.textChanged.connect(self.filter_preview)
        search_layout.addWidget(self.preview_search)
        
        refresh_btn = QPushButton("⟳ Refresh")
        refresh_btn.setObjectName("secondary")
        refresh_btn.setMaximumWidth(100)
        refresh_btn.setMinimumHeight(35)
        refresh_btn.clicked.connect(self.load_preview)
        search_layout.addWidget(refresh_btn)
        
        panel_layout.addWidget(search_frame)
        
        # Preview table with scroll
        table_container = QFrame()
        table_container.setStyleSheet("background-color: white; border-radius: 10px;")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(10, 10, 10, 10)
        
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(5)
        self.preview_table.setHorizontalHeaderLabels([
            "ID", "Exam", "Question", "Choices", "Marks"
        ])
        
        # Set table properties
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setShowGrid(True)
        self.preview_table.setGridStyle(Qt.SolidLine)
        
        # Set column widths
        header = self.preview_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        # Enable word wrap and selection
        self.preview_table.setWordWrap(True)
        self.preview_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.preview_table.setSelectionMode(QTableWidget.SingleSelection)
        
        table_layout.addWidget(self.preview_table)
        panel_layout.addWidget(table_container)
        
        return panel
    
    def rebuild_choices(self):
        """Rebuild choice input fields based on configuration"""
        # Clear existing widgets
        for widgets in self.choice_widgets:
            for widget in widgets:
                if widget:
                    widget.deleteLater()
        self.choice_widgets.clear()
        
        # Clear layout
        while self.choices_inner_layout.count():
            child = self.choices_inner_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Create new choice inputs
        num_choices = self.choice_count.value()
        is_multiple = self.multiple_correct.isChecked()
        
        labels = ['A', 'B', 'C', 'D', 'E', 'F']
        
        # Single selection group for radio buttons
        self.radio_group = QButtonGroup()
        
        for i in range(num_choices):
            choice_frame = QFrame()
            choice_frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 2px;
                    border: 1px solid #e0e0e0;
                }
                QFrame:hover {
                    border: 1px solid #2196F3;
                    background-color: #f0f7ff;
                }
            """)
            choice_layout = QHBoxLayout(choice_frame)
            choice_layout.setContentsMargins(15, 10, 15, 10)
            choice_layout.setSpacing(15)
            
            # Label
            label = QLabel(f"{labels[i]}:")
            label.setFont(QFont("Arial", 12, QFont.Bold))
            label.setMinimumWidth(30)
            label.setStyleSheet("color: #2196F3;")
            choice_layout.addWidget(label)
            
            # Choice text input
            text_input = QLineEdit()
            text_input.setPlaceholderText(f"Enter choice {labels[i]}")
            text_input.setMinimumHeight(35)
            choice_layout.addWidget(text_input)
            
            # Correct indicator
            if is_multiple:
                correct_check = QCheckBox("Correct")
                correct_check.setStyleSheet("""
                    QCheckBox {
                        color: #4CAF50;
                        font-weight: bold;
                        spacing: 8px;
                    }
                    QCheckBox::indicator {
                        width: 20px;
                        height: 20px;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #4CAF50;
                        border-radius: 4px;
                    }
                """)
                choice_layout.addWidget(correct_check)
                self.choice_widgets.append([label, text_input, correct_check])
            else:
                correct_radio = QRadioButton()
                correct_radio.setStyleSheet("""
                    QRadioButton::indicator {
                        width: 20px;
                        height: 20px;
                    }
                    QRadioButton::indicator:checked {
                        background-color: #4CAF50;
                        border-radius: 10px;
                    }
                """)
                self.radio_group.addButton(correct_radio, i)
                choice_layout.addWidget(correct_radio)
                self.choice_widgets.append([label, text_input, correct_radio])
            
            self.choices_inner_layout.addWidget(choice_frame)
    
    def load_exams(self):
        """Load exams into combobox"""
        self.exam_combo.clear()
        exams = get_exams()
        
        if exams:
            for exam in exams:
                self.exam_combo.addItem(f"{exam[1]} ", exam[0])
            self.save_btn.setEnabled(True)
            self.exam_combo.setCurrentIndex(0)
        else:
            self.exam_combo.addItem("⚠️ No exams available - Create an exam first")
            self.save_btn.setEnabled(False)
    
    def on_exam_changed(self, index):
        """Handle exam selection change"""
        if index >= 0 and self.exam_combo.currentData() is not None:
            exam_id = self.exam_combo.currentData()
            exam_text = self.exam_combo.currentText()
            self.header_exam_label.setText(f"Selected: {exam_text}")
            self.exam_filter_label.setText(f"Showing questions for: {exam_text}")
            self.load_preview()  # Reload preview for selected exam
        else:
            self.header_exam_label.setText("No exam selected")
            self.exam_filter_label.setText("Showing all exams")
            self.load_preview()  # Load all questions
    
    def load_preview(self):
        """Load questions into preview table"""
        all_questions = get_questions_with_choices()
        
        # Filter by selected exam if one is selected
        current_exam_id = self.exam_combo.currentData()
        if current_exam_id is not None:
            questions = [q for q in all_questions if q['exam_id'] == current_exam_id]
        else:
            questions = all_questions
        
        self.all_questions = questions  # Store for filtering
        
        self.preview_table.setRowCount(len(questions))
        self.preview_table.setColumnCount(5)
        
        for row, q in enumerate(questions):
            # Question ID
            id_item = QTableWidgetItem(str(q['question_id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.preview_table.setItem(row, 0, id_item)
            
            # Exam name
            exam_item = QTableWidgetItem(q['exam_name'])
            exam_item.setTextAlignment(Qt.AlignCenter)
            self.preview_table.setItem(row, 1, exam_item)
            
            # Question text
            q_text = q['question_text']
            if len(q_text) > 150:
                q_text = q_text[:150] + "..."
            question_item = QTableWidgetItem(q_text)
            question_item.setToolTip(q['question_text'])  # Show full text on hover
            self.preview_table.setItem(row, 2, question_item)
            
            # Choices with correct answers
            choices_text = ""
            correct_count = 0
            for choice in q['choices']:
                prefix = "✓ " if choice['is_correct'] else "  "
                if choice['is_correct']:
                    correct_count += 1
                choices_text += f"{prefix}{choice['label']}: {choice['text']}\n"
            
            choices_item = QTableWidgetItem(choices_text.strip())
            choices_item.setToolTip(choices_text)  # Show full text on hover
            self.preview_table.setItem(row, 3, choices_item)
            
            # Marks
            marks_item = QTableWidgetItem(str(q['marks']))
            marks_item.setTextAlignment(Qt.AlignCenter)
            self.preview_table.setItem(row, 4, marks_item)
            
            # Color coding based on correct answers
            if correct_count > 0:
                if correct_count == 1:
                    color = QColor(230, 255, 230)  # Light green for single correct
                else:
                    color = QColor(255, 255, 200)  # Light yellow for multiple correct
            else:
                color = QColor(255, 230, 230)  # Light red for no correct
            
            for col in range(5):
                item = self.preview_table.item(row, col)
                if item:
                    item.setBackground(color)
        
        # Resize rows
        for row in range(len(questions)):
            self.preview_table.resizeRowToContents(row)
    
    def filter_preview(self, text):
        """Filter preview table based on search text"""
        if not hasattr(self, 'all_questions'):
            return
        
        if not text:
            # Reset to all questions for current exam
            self.preview_table.setRowCount(len(self.all_questions))
            for row, q in enumerate(self.all_questions):
                self.preview_table.setItem(row, 0, QTableWidgetItem(str(q['question_id'])))
                self.preview_table.setItem(row, 1, QTableWidgetItem(q['exam_name']))
                
                q_text = q['question_text']
                if len(q_text) > 150:
                    q_text = q_text[:150] + "..."
                self.preview_table.setItem(row, 2, QTableWidgetItem(q_text))
                
                self.preview_table.setItem(row, 4, QTableWidgetItem(str(q['marks'])))
            return
        
        # Filter questions
        filtered = [q for q in self.all_questions 
                   if text.lower() in q['question_text'].lower()]
        
        self.preview_table.setRowCount(len(filtered))
        for row, q in enumerate(filtered):
            id_item = QTableWidgetItem(str(q['question_id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.preview_table.setItem(row, 0, id_item)
            
            exam_item = QTableWidgetItem(q['exam_name'])
            exam_item.setTextAlignment(Qt.AlignCenter)
            self.preview_table.setItem(row, 1, exam_item)
            
            q_text = q['question_text']
            if len(q_text) > 150:
                q_text = q_text[:150] + "..."
            self.preview_table.setItem(row, 2, QTableWidgetItem(q_text))
            
            self.preview_table.setItem(row, 4, QTableWidgetItem(str(q['marks'])))
    
    def save_question(self):
        """Save the question to database"""
        # Validate exam selection
        if self.exam_combo.currentText().startswith("⚠️") or self.exam_combo.currentData() is None:
            QMessageBox.critical(self, "Error", 
                               "Please create an exam first before adding questions!")
            return
        
        # Get exam ID
        exam_id = self.exam_combo.currentData()
        
        # Get question text
        question_text = self.question_text.toPlainText().strip()
        if not question_text:
            QMessageBox.critical(self, "Validation Error", 
                               "Question text is required!")
            self.question_text.setFocus()
            return
        
        # Get marks
        marks = self.marks_spin.value()
        
        # Get choices
        choices_text = []
        correct_indices = []
        
        for i, widgets in enumerate(self.choice_widgets):
            text = widgets[1].text().strip()
            if not text:
                QMessageBox.critical(self, "Validation Error", 
                                   f"Choice {chr(65 + i)} cannot be empty!")
                widgets[1].setFocus()
                return
            choices_text.append(text)
            
            # Check if correct
            if self.multiple_correct.isChecked():
                if widgets[2].isChecked():
                    correct_indices.append(i)
            else:
                if widgets[2].isChecked():
                    correct_indices.append(i)
        
        # Validate correct answers
        if not correct_indices:
            QMessageBox.critical(self, "Validation Error", 
                               "Please select at least one correct answer!")
            return
        
        try:
            # Insert question
            question_id = insert_question(
                exam_id=exam_id,
                text=question_text,
                choices_number=len(choices_text),
                marks=marks
            )
            
            # Insert choices
            labels = ['A', 'B', 'C', 'D', 'E', 'F']
            for i, text in enumerate(choices_text):
                is_correct = 1 if i in correct_indices else 0
                insert_choice(
                    question_id=question_id,
                    label=labels[i],
                    text=text,
                    is_correct=is_correct
                )
            
            # Show success message
            QMessageBox.information(self, "Success", 
                                   f"Question saved successfully!\nQuestion ID: {question_id}")
            
            # Clear form
            self.clear_form()
            
            # Refresh preview
            self.load_preview()
            
            # Emit signal
            self.question_added.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", 
                               f"Failed to save question:\n{str(e)}")
    
    def clear_form(self):
        """Clear all input fields"""
        self.question_text.clear()
        self.marks_spin.setValue(1)
        self.choice_count.setValue(4)
        self.multiple_correct.setChecked(False)
        
        # Clear all choice inputs
        for widgets in self.choice_widgets:
            widgets[1].clear()
            if self.multiple_correct.isChecked():
                if isinstance(widgets[2], QCheckBox):
                    widgets[2].setChecked(False)
            else:
                if isinstance(widgets[2], QRadioButton):
                    widgets[2].setChecked(False)
        
        # Reset radio group if not multiple
        if not self.multiple_correct.isChecked() and hasattr(self, 'radio_group'):
            for btn in self.radio_group.buttons():
                btn.setChecked(False)