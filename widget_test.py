import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("AI Assistant")
window.setFixedSize(400, 200)
window.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

layout = QVBoxLayout()
label = QLabel("Hello! This is your assistant widget.")
layout.addWidget(label)
window.setLayout(layout)

window.show()
sys.exit(app.exec())