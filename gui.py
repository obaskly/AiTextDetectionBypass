import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QFileDialog, QMessageBox, QCheckBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from paraphraser import main


class ParaphrasingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

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
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #333;
                color: #DDD;
            }
        """)

        self.titleLabel = QLabel('ParaGenie')
        self.titleLabel.setFont(QFont('Arial', 24))
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.purposeLabel = QLabel('Purpose of Writing:')
        self.readabilityLabel = QLabel('Readability Level:')
        self.filePathLabel = QLabel('Article File Path:')
        self.emailLabel = QLabel('Email Address:')

        self.purposeComboBox = QComboBox()
        self.purposeComboBox.addItems(['General Writing', 'Essay', 'Article', 'Marketing Material', 'Story', 'Cover letter', 'Report', 'Business Material', 'Legal Material'])

        self.readabilityComboBox = QComboBox()
        self.readabilityComboBox.addItems(['High School', 'University', 'Doctorate', 'Journalist', 'Marketing'])

        self.filePathLineEdit = QLineEdit()
        self.browseButton = QPushButton('Browse')
        self.browseButton.clicked.connect(self.browseFile)

        self.emailLineEdit = QLineEdit()
        self.emailLineEdit.setPlaceholderText('Enter your email address')

        # Add NLTK toggle checkbox
        self.useNltkCheckBox = QCheckBox('Use NLTK for splitting chunks')
        self.useNltkCheckBox.setChecked(False)

        self.startButton = QPushButton('Start Paraphrasing')
        self.startButton.clicked.connect(self.startParaphrasing)

        layout.addWidget(self.titleLabel)
        layout.addWidget(self.purposeLabel)
        layout.addWidget(self.purposeComboBox)
        layout.addWidget(self.readabilityLabel)
        layout.addWidget(self.readabilityComboBox)
        layout.addWidget(self.filePathLabel)
        layout.addWidget(self.filePathLineEdit)
        layout.addWidget(self.browseButton)
        layout.addWidget(self.emailLabel)
        layout.addWidget(self.emailLineEdit)
        layout.addWidget(self.useNltkCheckBox)
        layout.addWidget(self.startButton)

        self.setLayout(layout)
        self.setWindowTitle('ParaGenie V2.0')
        self.setGeometry(300, 300, 400, 450)

    def browseFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        self.filePathLineEdit.setText(fname[0])

    def startParaphrasing(self):
        purpose_choice = self.purposeComboBox.currentIndex() + 1
        readability_choice = self.readabilityComboBox.currentIndex() + 1
        article_file_path = self.filePathLineEdit.text()
        email_address = self.emailLineEdit.text()
        use_nltk = self.useNltkCheckBox.isChecked()

        if not email_address:
            QMessageBox.warning(self, 'Input Error', 'Please enter an email address.')
            return

        try:
            main(purpose_choice, readability_choice, article_file_path, email_address, use_nltk)
            QMessageBox.information(self, 'Success', 'Article has been paraphrased successfully.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')


def run_app():
    app = QApplication(sys.argv)
    ex = ParaphrasingApp()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    run_app()
