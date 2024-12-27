import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QFileDialog, QMessageBox, QCheckBox, QTabWidget, QTextEdit, QListWidget, QHBoxLayout
)
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import Qt, QDir, QThread, pyqtSignal
from paraphraser import main

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

        textArea = QTextEdit()
        textArea.setPlaceholderText("Enter or paste text here...")

        scanButton = QPushButton('Scan')
        scanButton.clicked.connect(lambda: QMessageBox.information(self, "Scan", "Scanning text..."))

        layout.addWidget(textArea)
        layout.addWidget(scanButton)
        tab.setLayout(layout)
        return tab

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
        purpose_choice = self.purposeComboBox.currentIndex() + 1
        readability_choice = self.readabilityComboBox.currentIndex() + 1
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
