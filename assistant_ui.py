import sys
import os
import random
import signal
from dotenv import load_dotenv
from google import genai
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QScrollArea
)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPainterPath, QBrush, QPen, QTransform
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread, QTimer, QRectF
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
    """A container widget painted as a rounded speech bubble with a
    small tail at the TOP-RIGHT, pointing upward toward the character
    that sits above it."""

    def __init__(self):
        super().__init__()
        self.inner_layout = QVBoxLayout()
        self.inner_layout.setContentsMargins(16, 24, 16, 16)
        self.setLayout(self.inner_layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(0, 12, self.width(), self.height() - 12)
        path = QPainterPath()
        path.addRoundedRect(rect, 18, 18)

        tail_x = self.width() - 56
        tail = QPainterPath()
        tail.moveTo(tail_x, rect.top())
        tail.lineTo(tail_x + 16, rect.top())
        tail.lineTo(tail_x + 8, rect.top() - 12)
        tail.closeSubpath()

        path.addPath(tail)

        painter.setBrush(QBrush(QColor("white")))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawPath(path)


def create_fallback_character(width, height):
    """Draws a simple placeholder character with a real alpha channel,
    used only if character.png is missing or fails to load, so the
    script never crashes on a missing asset."""
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QBrush(QColor("#F7B6C2")))
    painter.setPen(QPen(QColor("#5A4038"), 3))
    painter.drawEllipse(width // 4, height // 8, width // 2, width // 2)

    painter.setBrush(QBrush(QColor("#A9C7E8")))
    body_top = height // 8 + width // 2 - 10
    painter.drawRoundedRect(
        width // 3, body_top, width // 3, height - body_top - 10, 12, 12
    )

    painter.end()
    return pixmap


app = QApplication(sys.argv)

CHAR_SIZE = (160, 160)
BUBBLE_MAX_HEIGHT = 220
WALK_SPEED = 3
WALK_TICK_MS = 40

window = QWidget()
window.setWindowFlags(
    Qt.WindowType.FramelessWindowHint
    | Qt.WindowType.WindowStaysOnTopHint
    | Qt.WindowType.Tool
)
window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
window.setStyleSheet("background: transparent;")

layout = QVBoxLayout()
layout.setContentsMargins(0, 0, 0, 0)
layout.setSpacing(4)

character_label = QLabel()
character_pixmap_right = QPixmap("character.png")
if character_pixmap_right.isNull():
    character_pixmap_right = create_fallback_character(*CHAR_SIZE)
else:
    character_pixmap_right = character_pixmap_right.scaled(
        CHAR_SIZE[0], CHAR_SIZE[1],
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )
character_pixmap_left = character_pixmap_right.transformed(QTransform().scale(-1, 1))
character_label.setPixmap(character_pixmap_right)
character_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
character_label.setStyleSheet("background: transparent;")
layout.addWidget(character_label)


class ShadowWidget(QWidget):
    """A soft elliptical shadow whose size/opacity can be scaled to
    imply how 'off the ground' the character currently is."""

    def __init__(self, width, height):
        super().__init__()
        self.base_width = width
        self.base_height = height
        self.scale = 1.0
        self.setFixedHeight(height + 6)
        self.setStyleSheet("background: transparent;")

    def set_scale(self, scale):
        self.scale = max(0.4, min(1.0, scale))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.base_width * self.scale
        h = self.base_height * self.scale
        cx = self.width() / 2
        cy = self.height() / 2

        alpha = int(90 * self.scale)
        painter.setBrush(QBrush(QColor(0, 0, 0, alpha)))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawEllipse(QRectF(cx - w / 2, cy - h / 2, w, h))


shadow_widget = ShadowWidget(width=70, height=18)
layout.addWidget(shadow_widget, alignment=Qt.AlignmentFlag.AlignHCenter)

chat_label = QLabel("")
chat_label.setWordWrap(True)
chat_label.setAlignment(Qt.AlignmentFlag.AlignTop)
chat_label.setStyleSheet("background: transparent; color: black;")

bubble_container = SpeechBubble()
bubble_container.inner_layout.addWidget(chat_label)

scroll_area = QScrollArea()
scroll_area.setWidget(bubble_container)
scroll_area.setWidgetResizable(True)
scroll_area.setFixedHeight(BUBBLE_MAX_HEIGHT)
scroll_area.setStyleSheet("""
    QScrollArea {
        background-color: transparent;
        border: none;
    }
""")
scroll_area.hide()
scroll_area.viewport().setStyleSheet("background: transparent;")
layout.addWidget(scroll_area)

input_box = QLineEdit()
input_box.setPlaceholderText("How can I help you?")
input_box.setStyleSheet("""
    QLineEdit {
        background-color: rgba(0, 0, 0, 160);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 6px 10px;
    }
""")
input_box.hide()
layout.addWidget(input_box)

window.setLayout(layout)
window.adjustSize()

chat_history = ""
first_question_asked = False
chat_mode = False
walk_direction = 1

dot_states = ["Thinking", "Thinking.", "Thinking..", "Thinking..."]
dot_index = 0

dot_timer = QTimer()


def animate_dots():
    global dot_index
    chat_label.setText(dot_states[dot_index % len(dot_states)])
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

    chat_history += f"<b>Assistant:</b> {answer_text}<br><br>"
    chat_label.setText(chat_history)
    scroll_area.verticalScrollBar().setValue(scroll_area.verticalScrollBar().maximum())
    window.adjustSize()
    position_top_right()


def ask_gemini():
    global chat_history, first_question_asked, current_worker, dot_index
    question = input_box.text()
    if not question:
        return

    if not first_question_asked:
        input_box.setPlaceholderText("Write a message")
        first_question_asked = True

    chat_history += f"<b>You:</b> {question}<br>"
    input_box.clear()
    input_box.hide()

    scroll_area.show()
    dot_index = 0
    chat_label.setText("Thinking")
    dot_timer.start(400)
    window.adjustSize()

    current_worker = GeminiWorker(question)
    current_worker.result_ready.connect(show_answer)
    current_worker.start()


input_box.returnPressed.connect(ask_gemini)


DOCK_OVERLAP = 45


def dock_y():
    screen = app.primaryScreen().availableGeometry()
    return screen.bottom() - window.height() + DOCK_OVERLAP


def position_top_right():
    screen = app.primaryScreen().availableGeometry()
    margin = 20
    x = screen.right() - window.width() - margin
    y = screen.top() + margin
    window.move(x, y)


last_dock_x = None


def wander_step():
    global walk_direction
    screen = app.primaryScreen().availableGeometry()

    if random.random() < 0.01:
        walk_direction *= -1

    new_x = window.x() + walk_direction * WALK_SPEED

    if new_x <= screen.left():
        new_x = screen.left()
        walk_direction = 1
    elif new_x + window.width() >= screen.right():
        new_x = screen.right() - window.width()
        walk_direction = -1

    window.move(new_x, dock_y())

    character_label.setPixmap(
        character_pixmap_right if walk_direction == 1 else character_pixmap_left
    )


wander_timer = QTimer()
wander_timer.timeout.connect(wander_step)


class Bridge(QObject):
    toggle_window_signal = pyqtSignal()
    toggle_input_signal = pyqtSignal()


bridge = Bridge()


def enter_chat_mode():
    global chat_mode, last_dock_x
    chat_mode = True
    last_dock_x = window.x()
    wander_timer.stop()
    shadow_widget.hide()
    input_box.show()
    input_box.setFocus()
    window.adjustSize()
    position_top_right()


def exit_chat_mode():
    global chat_mode
    chat_mode = False
    input_box.hide()
    scroll_area.hide()
    shadow_widget.show()
    window.adjustSize()

    screen = app.primaryScreen().availableGeometry()
    x = last_dock_x if last_dock_x is not None else window.x()
    x = max(screen.left(), min(x, screen.right() - window.width()))
    window.move(x, dock_y())

    wander_timer.start(WALK_TICK_MS)


def toggle_window():
    if not chat_mode:
        enter_chat_mode()
    else:
        exit_chat_mode()


def toggle_input():
    if not chat_mode:
        return
    if input_box.isVisible():
        input_box.hide()
    else:
        input_box.show()
        input_box.setFocus()
    window.adjustSize()


bridge.toggle_window_signal.connect(toggle_window)
bridge.toggle_input_signal.connect(toggle_input)


def on_activate_window():
    bridge.toggle_window_signal.emit()


def on_activate_input():
    bridge.toggle_input_signal.emit()


window_hotkey = keyboard.HotKey(
    keyboard.HotKey.parse('<cmd>+<shift>+a'),
    on_activate_window
)

input_hotkey = keyboard.HotKey(
    keyboard.HotKey.parse('<cmd>+<shift>+m'),
    on_activate_input
)

hotkeys = [window_hotkey, input_hotkey]


def on_press(key):
    canonical_key = l.canonical(key)
    for hk in hotkeys:
        hk.press(canonical_key)


def on_release(key):
    canonical_key = l.canonical(key)
    for hk in hotkeys:
        hk.release(canonical_key)


l = keyboard.Listener(
    on_press=on_press,
    on_release=on_release
)
l.start()

# Allow Ctrl+C in the terminal to actually stop the app.
signal.signal(signal.SIGINT, signal.SIG_DFL)
signal_timer = QTimer()
signal_timer.start(200)
signal_timer.timeout.connect(lambda: None)

# Start her out walking on the dock immediately.
screen_geo = app.primaryScreen().availableGeometry()
window.move(screen_geo.center().x(), dock_y())
window.show()
wander_timer.start(WALK_TICK_MS)

print("Zebraz is wandering the desktop. Cmd+Shift+A: chat mode. Cmd+Shift+M: show/hide message bar.")
sys.exit(app.exec())