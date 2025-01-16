import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QFileDialog, QMessageBox, QCheckBox, QTabWidget, QTextEdit, QListWidget, QHBoxLayout
)
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent, QPainter, QColor
from PyQt6.QtCore import Qt, QDir, QThread, pyqtSignal, QRect
from paraphraser import main
from ai_scanner import scan_text

class CircularProgress(QWidget):
    def __init__(self, ai_percentage=0, human_percentage=100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ai_percentage = ai_percentage
        self.human_percentage = human_percentage
        self.is_scanned = False  # Flag to check if the scan has been performed
        self.setMinimumSize(50, 50)  # Set smaller size for the circle

    def setPercentages(self, ai_percentage, human_percentage):
        self.ai_percentage = ai_percentage
        self.human_percentage = human_percentage
        self.is_scanned = True  # Mark the scan as complete
        self.update()  # Trigger a repaint to update the circle

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        # Drawing the outer circle
        rect = self.rect().adjusted(5, 5, -5, -5)  # Adjust for better circle size
        painter.setBrush(QColor(255, 255, 255))  # White background
        painter.drawEllipse(rect)

        # Draw the AI part (red)
        painter.setBrush(QColor(255, 0, 0))  # Red for AI
        ai_angle = int((self.ai_percentage * 360 / 100))  # Convert angle to integer
        painter.drawPie(rect, 90 * 16, ai_angle * 16)  # Angle is in 1/16ths of a degree

        # Draw the Human part (green)
        painter.setBrush(QColor(0, 255, 0))  # Green for Human
        human_angle = int((self.human_percentage * 360 / 100))  # Convert angle to integer
        painter.drawPie(rect, (90 + ai_angle) * 16, human_angle * 16)  # Angle is in 1/16ths of a degree

        # Only display percentage text if the scan has completed
        if self.is_scanned:
            painter.setPen(Qt.GlobalColor.black)  # Text color (black)
            painter.setFont(QFont('Arial', 10, QFont.Weight.Bold))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self.ai_percentage}% AI\n{self.human_percentage}% Human")

        painter.end()

class CircularProgressGrid(QWidget):
    def __init__(self, detectors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)  # Adjust the spacing between items
        
        row = 0
        col = 0
        self.progress_bars = {}

        for detector in detectors:
            progress_bar = CircularProgress()
            self.progress_bars[detector] = progress_bar
            grid_layout.addWidget(progress_bar, row, col)
            
            col += 1
            if col > 2:  # After 3 columns, move to the next row
                col = 0
                row += 1

        self.setLayout(grid_layout)

class APICaptureThread(QThread):
    current_email = pyqtSignal(str)  # Signal to update the current email being processed
    api_grabbed = pyqtSignal(str)    # Signal to add to the API results list
    result = pyqtSignal(dict)        # Signal to send the final result or errors

    def run(self):
        try:
            from api_grabber import main

            result_message = main(
                update_current_email=lambda email: self.current_email.emit(email),
                update_result=lambda result: self.api_grabbed.emit(result)
            )
            
            # Check if the result_message indicates an error
            if "does not exist" in result_message or "No new emails" in result_message:
                self.result.emit({"success": False, "message": result_message})
            else:
                self.result.emit({"success": True, "message": result_message})
        except Exception as e:
            self.result.emit({"success": False, "message": str(e)})

class ParaphrasingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.resultLabels = {}  # This will hold references to CircularProgress widgets
        self.detectorLabels = {}  # To hold labels for each detector
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ParaGenie V2.0')
        self.setGeometry(300, 300, 800, 600)

        self.setStyleSheet("""
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
            QLineEdit, QComboBox, QTextEdit, QListWidget {
                padding: 5px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #333;
                color: #DDD;
            }
        """)

        self.tabs = QTabWidget()

        self.paraphraserTab = self.createParaphraserTab()
        self.aiScannerTab = self.createAIScannerTab()
        self.apiGrabberTab = self.createAPIGrabberTab()

        self.tabs.addTab(self.paraphraserTab, "Paraphraser")
        self.tabs.addTab(self.aiScannerTab, "AI Scanner")
        self.tabs.addTab(self.apiGrabberTab, "API Grabber")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.tabs)
        self.setLayout(mainLayout)

    def createParaphraserTab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)

        titleLabel = QLabel('ParaGenie')
        titleLabel.setFont(QFont('Orbitron', 29))
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titleLabel.setStyleSheet(""" 
            QLabel {
                color: qlineargradient(
                    spread: pad, 
                    x1: 0, y1: 0, 
                    x2: 1, y2: 0, 
                    stop: 0 #00c6ff, 
                    stop: 1 #0072ff
                );
                font-weight: bold;
                font-size: 32px;
                padding: 20px 0;
            }
        """)

        purposeLabel = QLabel('Purpose of Writing:')
        readabilityLabel = QLabel('Readability Level:')
        toneLabel = QLabel('Tone:')
        filePathLabel = QLabel('Article File Path:')
        emailLabel = QLabel('Email Address:')

        self.purposeComboBox = QComboBox()  # Now instance variable
        self.purposeComboBox.addItems(['General Writing', 'Essay', 'Article', 'Marketing Material', 'Story', 'Cover letter', 'Report', 'Business Material', 'Legal Material'])

        self.readabilityComboBox = QComboBox()  # Now instance variable
        self.readabilityComboBox.addItems(['High School', 'University', 'Doctorate', 'Journalist', 'Marketing'])

        self.toneComboBox = QComboBox()  # Now instance variable
        self.toneComboBox.addItems(['Balanced', 'More Human', 'More Readable'])

        self.filePathLineEdit = QLineEdit()  # Now instance variable
        self.filePathLineEdit.setPlaceholderText("Drag and drop a file here or click 'Browse'")
        self.filePathLineEdit.setAcceptDrops(True)
        self.filePathLineEdit.dragEnterEvent = self.dragEnterEvent
        self.filePathLineEdit.dropEvent = self.dropEvent

        self.browseButton = QPushButton('Browse')  # Now instance variable
        self.browseButton.clicked.connect(self.browseFile)

        self.emailLineEdit = QLineEdit()  # Now instance variable
        self.emailLineEdit.setPlaceholderText('Enter your email address')

        self.useNltkCheckBox = QCheckBox('Use NLTK for splitting chunks')  # Now instance variable
        self.useNltkCheckBox.setChecked(False)

        self.saveSameFormatCheckBox = QCheckBox('Save file in the same format')  # Now instance variable
        self.saveSameFormatCheckBox.setChecked(False)

        self.startButton = QPushButton('Start Paraphrasing')  # Now instance variable
        self.startButton.clicked.connect(self.startParaphrasing)

        layout.addWidget(titleLabel)
        layout.addWidget(purposeLabel)
        layout.addWidget(self.purposeComboBox)
        layout.addWidget(readabilityLabel)
        layout.addWidget(self.readabilityComboBox)
        layout.addWidget(toneLabel)
        layout.addWidget(self.toneComboBox)
        layout.addWidget(filePathLabel)
        layout.addWidget(self.filePathLineEdit)
        layout.addWidget(self.browseButton)
        layout.addWidget(emailLabel)
        layout.addWidget(self.emailLineEdit)
        layout.addWidget(self.useNltkCheckBox)
        layout.addWidget(self.saveSameFormatCheckBox)
        layout.addWidget(self.startButton)

        tab.setLayout(layout)
        return tab

    def createAIScannerTab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # 1. Text area for input
        self.textArea = QTextEdit()
        self.textArea.setPlaceholderText("Enter or paste text here...")
        layout.addWidget(self.textArea)

        # 2. Scan button
        scanButton = QPushButton('Scan')
        scanButton.clicked.connect(self.scanText)
        layout.addWidget(scanButton)

        # 3. Create CircularProgressGrid to hold the circular progress bars
        detectors = [
            'scoreGptZero', 'scoreOpenAI', 'scoreWriter', 'scoreCrossPlag', 'scoreCopyLeaks',
            'scoreSapling', 'scoreContentAtScale', 'scoreZeroGPT'
        ]

        # Add labels and CircularProgress widgets
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        row = 0
        col = 0
        for i, detector in enumerate(detectors):
            label = QLabel(detector)
            progress_bar = CircularProgress(ai_percentage=0, human_percentage=100)
            self.resultLabels[detector] = progress_bar
            self.detectorLabels[detector] = label  # Store label reference
            grid_layout.addWidget(label, row, col)
            grid_layout.addWidget(progress_bar, row+1, col)

            col += 1
            if col > 2:  # After 3 columns, move to the next row
                col = 0
                row += 2  # Skip one row for the label

        layout.addLayout(grid_layout)

        # Set the layout for the tab
        tab.setLayout(layout)
        return tab

    def scanText(self):
        text = self.textArea.toPlainText().strip()

        if not text:
            QMessageBox.warning(self, 'Input Error', 'Please enter text to scan.')
            return

        api_key = "0e3640c3-7516-4c20-acb7-3fbfef5c1b3a"

        # Run the AI scanner
        detection_response = scan_text(api_key, text)

        if detection_response is None:
            QMessageBox.critical(self, 'Error', 'Failed to detect AI in the text.')
            return

        ai_percentage, detector_results = detection_response  # Assuming scan_text returns this properly

        # Update the results in the GUI
        for detector, result in detector_results.items():
            ai_percentage = result.get('ai_percentage', 0)
            human_percentage = result.get('human_percentage', 100)

            # Ensure the CircularProgress widget exists before trying to update it
            if detector in self.resultLabels:
                self.resultLabels[detector].setPercentages(ai_percentage, human_percentage)

        # Add final result label after the scan
        final_result_label = QLabel(f"The AI detection result: {ai_percentage}% AI content detected in the text.")
        final_result_label.setStyleSheet("color: red;" if ai_percentage > 50 else "color: green;")
        self.tabs.widget(1).layout().addWidget(final_result_label)  # Add to the AI scanner tab layout

    def createAPIGrabberTab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        currentEmailLabel = QLabel("Current Email:")
        currentEmailLabel.setStyleSheet("color: #00FF00; font-weight: bold;")
        grabbedAPIsList = QListWidget()

        grabButton = QPushButton('Grab')
        grabButton.clicked.connect(lambda: self.runAPICapture(currentEmailLabel, grabbedAPIsList))

        layout.addWidget(currentEmailLabel)
        layout.addWidget(grabbedAPIsList)
        layout.addWidget(grabButton)
        tab.setLayout(layout)
        return tab

    def browseFile(self):
        current_directory = QDir.currentPath()
        fname, _ = QFileDialog.getOpenFileName(
            self, 
            'Open file', 
            current_directory, 
            'Text Files (*.txt);;Word Documents (*.docx);;PDF Files (*.pdf)'
        )
        self.filePathLineEdit.setText(fname)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().lower().endswith(('.txt', '.docx', '.pdf')) for url in urls):
                event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.filePathLineEdit.setText(file_path)

    def startParaphrasing(self):
        purpose_choice = self.purposeComboBox.currentText()
        readability_choice = self.readabilityComboBox.currentText()
        tone_choice = self.toneComboBox.currentText().upper().replace(' ', '_')
        article_file_path = self.filePathLineEdit.text()
        email_address = self.emailLineEdit.text()
        use_nltk = self.useNltkCheckBox.isChecked()
        save_same_format = self.saveSameFormatCheckBox.isChecked()

        if not email_address:
            QMessageBox.warning(self, 'Input Error', 'Please enter an email address.')
            return

        try:
            main(purpose_choice, readability_choice, article_file_path, email_address, use_nltk, save_same_format, tone_choice)
            QMessageBox.information(self, 'Success', 'Article has been paraphrased successfully.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')

    def runAPICapture(self, currentEmailLabel, grabbedAPIsList):
        def updateCurrentEmail(email):
            # Update the current email label with the email being processed
            currentEmailLabel.setText(f"Current Email: {email}")

        def addGrabbedAPI(api_entry):
            # Append the grabbed API or failure message to the list widget
            grabbedAPIsList.addItem(api_entry)

        def handleResult(result):
            if result["success"]:
                QMessageBox.information(self, "Success", "API grabbing completed successfully.")
            else:
                QMessageBox.warning(self, "Error", result["message"])  # Show the error message in a warning box

        # Start the API capture thread
        self.apiThread = APICaptureThread()
        self.apiThread.current_email.connect(updateCurrentEmail)  # Update the current email label
        self.apiThread.api_grabbed.connect(addGrabbedAPI)         # Append grabbed APIs to the list
        self.apiThread.result.connect(handleResult)              # Handle the final result
        self.apiThread.start()

def run_app():
    app = QApplication(sys.argv)
    ex = ParaphrasingApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    run_app()
