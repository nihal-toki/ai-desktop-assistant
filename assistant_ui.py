import sys
import os
from dotenv import load_dotenv
from google import genai
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QScrollArea
)
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor, QPainterPath, QBrush, QPen
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread, QTimer, QRectF, QPointF
from pynput import keyboard

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

chat_session = client.chats.create(
    model="gemini-3.6-flash",
    config={
        "system_instruction": (
            "Keep answers concise. Use bullet points or numbered lists "
            "only when the content is naturally a list, steps, or "
            "comparison. Otherwise answer in short plain sentences. "
            "Avoid long paragraphs."
        )
    }
)


class SpeechBubble(QWidget):
    """A container widget that paints itself as a rounded speech bubble
    with a small pointed tail, and holds any child widgets inside it."""

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.inner_layout = QVBoxLayout()
        self.inner_layout.setContentsMargins(16, 16, 16, 24)
        self.setLayout(self.inner_layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(0, 0, self.width(), self.height() - 12)
        path = QPainterPath()
        path.addRoundedRect(rect, 18, 18)

        tail_x = 40
        tail = QPainterPath()
        tail.moveTo(tail_x, rect.bottom())
        tail.lineTo(tail_x + 16, rect.bottom())
        tail.lineTo(tail_x, rect.bottom() + 12)
        tail.closeSubpath()

        path.addPath(tail)

        painter.setBrush(QBrush(QColor("white")))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawPath(path)


app = QApplication(sys.argv)

SMALL_SIZE = (400, 60)
FULL_SIZE = (400, 400)
ICON_SIZE = (140, 100)

window = QWidget()
window.setWindowTitle("Zebraz")
window.resize(*SMALL_SIZE)
window.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

layout = QVBoxLayout()

base_icon_pixmap = QPixmap("chat_icon.png").scaled(
    ICON_SIZE[0], ICON_SIZE[1],
    Qt.AspectRatioMode.KeepAspectRatio,
    Qt.TransformationMode.SmoothTransformation
)

thinking_icon = QLabel()
thinking_icon.setFixedSize(*ICON_SIZE)
thinking_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
thinking_icon.hide()
layout.addWidget(thinking_icon, alignment=Qt.AlignmentFlag.AlignHCenter)


def render_bubble_text(text):
    pixmap = QPixmap(base_icon_pixmap)
    painter = QPainter(pixmap)
    painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
    painter.setPen(QColor("black"))
    text_rect = pixmap.rect()
    text_rect.adjust(0, -6, 0, -6)
    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
    painter.end()
    thinking_icon.setPixmap(pixmap)


chat_label = QLabel("")
chat_label.setWordWrap(True)
chat_label.setAlignment(Qt.AlignmentFlag.AlignTop)
chat_label.setStyleSheet("background: transparent; color: black;")

bubble_container = SpeechBubble()
bubble_container.inner_layout.addWidget(chat_label)

scroll_area = QScrollArea()
scroll_area.setWidget(bubble_container)
scroll_area.setWidgetResizable(True)
scroll_area.setStyleSheet("""
    QScrollArea {
        background-color: transparent;
        border: none;
    }
""")
scroll_area.hide()

input_box = QLineEdit()
input_box.setPlaceholderText("How can I help you?")

layout.addWidget(scroll_area)
layout.addWidget(input_box)
window.setLayout(layout)

chat_history = ""
first_question_asked = False

dot_states = ["Thinking", "Thinking.", "Thinking..", "Thinking..."]
dot_index = 0

dot_timer = QTimer()


def animate_dots():
    global dot_index
    render_bubble_text(dot_states[dot_index % len(dot_states)])
    dot_index += 1


dot_timer.timeout.connect(animate_dots)


class GeminiWorker(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, question):
        super().__init__()
        self.question = question

    def run(self):
        response = chat_session.send_message(self.question)
        self.result_ready.emit(response.text)


current_worker = None


def show_answer(answer_text):
    global chat_history

    dot_timer.stop()
    thinking_icon.hide()

    if not scroll_area.isVisible():
        scroll_area.show()
        window.resize(*FULL_SIZE)
        position_top_right()

    chat_history += f"<b>Assistant:</b> {answer_text}<br><br>"
    chat_label.setText(chat_history)
    scroll_area.verticalScrollBar().setValue(scroll_area.verticalScrollBar().maximum())


def ask_gemini():
    global chat_history, first_question_asked, current_worker, dot_index
    question = input_box.text()
    if not question:
        return

    if not first_question_asked:
        input_box.setPlaceholderText("Write a message")
        first_question_asked = True

    chat_history += f"<b>You:</b> {question}<br>"
    if scroll_area.isVisible():
        chat_label.setText(chat_history)
        scroll_area.verticalScrollBar().setValue(scroll_area.verticalScrollBar().maximum())

    input_box.clear()

    dot_index = 0
    render_bubble_text("Thinking")
    thinking_icon.show()
    dot_timer.start(400)

    current_worker = GeminiWorker(question)
    current_worker.result_ready.connect(show_answer)
    current_worker.start()


input_box.returnPressed.connect(ask_gemini)


def position_top_right():
    screen = app.primaryScreen().availableGeometry()
    margin = 20
    x = screen.right() - window.width() - margin
    y = screen.top() + margin
    window.move(x, y)


class Bridge(QObject):
    toggle_signal = pyqtSignal()


bridge = Bridge()


def toggle_window():
    if window.isVisible():
        window.hide()
    else:
        position_top_right()
        window.show()
        input_box.setFocus()


bridge.toggle_signal.connect(toggle_window)


def on_activate():
    bridge.toggle_signal.emit()


def for_canonical(f):
    return lambda k: f(l.canonical(k))


hotkey = keyboard.HotKey(
    keyboard.HotKey.parse('<cmd>+<shift>+a'),
    on_activate
)

l = keyboard.Listener(
    on_press=for_canonical(hotkey.press),
    on_release=for_canonical(hotkey.release)
)
l.start()

print("Widget assistant running. Press Cmd+Shift+A to show/hide it.")
sys.exit(app.exec())