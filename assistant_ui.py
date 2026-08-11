import sys
import os
import random
import signal
import json
import tempfile
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit,
    QScrollArea, QPushButton, QSystemTrayIcon, QMenu
)
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QPainterPath, QBrush, QPen, QTransform,
    QIcon, QAction
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread, QTimer, QRectF
from pynput import keyboard

try:
    import objc
    from AppKit import NSWindowCollectionBehaviorCanJoinAllSpaces
    HAS_PYOBJC = True
except ImportError:
    HAS_PYOBJC = False


APP_NAME = "Zebraz"


def bundled_resource_path(filename):
    """Return an asset path that works in both source and py2app builds."""
    if getattr(sys, "frozen", False):
        # py2app copies data_files to Contents/Resources.
        base_dir = os.path.normpath(
            os.path.join(os.path.dirname(sys.executable), "..", "Resources")
        )
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)


def application_data_path(filename):
    """Return a persistent, user-owned path shared by terminal and app runs."""
    app_support_dir = os.path.join(
        os.path.expanduser("~/Library/Application Support"), APP_NAME
    )
    os.makedirs(app_support_dir, exist_ok=True)
    return os.path.join(app_support_dir, filename)


# Assets are read from the app bundle; user data is never stored in the bundle.
load_dotenv(bundled_resource_path(".env"))
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MEMORY_FILE = application_data_path("zebraz_memory.json")
# Preserve conversations created by earlier terminal-only versions on first run.
LEGACY_MEMORY_FILE = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "zebraz_memory.json")
    if not getattr(sys, "frozen", False)
    else None
)


def load_conversation_log():
    """Load the saved conversation log from Zebraz's Application Support folder."""
    source_path = MEMORY_FILE
    if not os.path.exists(source_path):
        if LEGACY_MEMORY_FILE and os.path.exists(LEGACY_MEMORY_FILE):
            source_path = LEGACY_MEMORY_FILE
        else:
            return []
    try:
        with open(source_path, "r", encoding="utf-8") as memory_file:
            log = json.load(memory_file)
        if not isinstance(log, list):
            raise ValueError("memory file does not contain a conversation list")
        if source_path != MEMORY_FILE:
            save_conversation_log(log)
            print(f"Migrated existing memory to {MEMORY_FILE}")
        return log
    except Exception as error:
        print(f"Could not load memory file ({error}) - starting fresh.")
        return []


def save_conversation_log(log):
    """Atomically save conversation history, avoiding corruption on app exit."""
    try:
        directory = os.path.dirname(MEMORY_FILE)
        fd, temporary_path = tempfile.mkstemp(
            prefix=".zebraz_memory_", suffix=".json", dir=directory
        )
        with os.fdopen(fd, "w", encoding="utf-8") as memory_file:
            json.dump(log, memory_file, indent=2, ensure_ascii=False)
        os.replace(temporary_path, MEMORY_FILE)
    except Exception as error:
        print(f"Could not save memory file: {error}")
        try:
            if "temporary_path" in locals() and os.path.exists(temporary_path):
                os.unlink(temporary_path)
        except OSError:
            pass


def build_gemini_history(log):
    """Convert saved turns to the format Gemini expects for restored chats."""
    history = []
    for turn in log:
        if not isinstance(turn, dict) or "role" not in turn or "text" not in turn:
            continue
        role = "user" if turn["role"] == "user" else "model"
        history.append({"role": role, "parts": [{"text": turn["text"]}]})
    return history


conversation_log = load_conversation_log()
archived_snapshot = list(conversation_log)

try:
    chat_session = client.chats.create(
        model="gemini-3.6-flash",
        config={
            "system_instruction": (
                "Keep answers concise. Use bullet points or numbered lists "
                "only when the content is naturally a list, steps, or "
                "comparison. Otherwise answer in short plain sentences. "
                "Avoid long paragraphs."
            )
        },
        history=build_gemini_history(conversation_log),
    )
    if conversation_log:
        print(f"Loaded {len(conversation_log)} past messages from memory.")
except Exception as error:
    print(f"Could not restore chat history ({error}) - starting a fresh session.")
    conversation_log = []
    chat_session = client.chats.create(
        model="gemini-3.6-flash",
        config={
            "system_instruction": (
                "Keep answers concise. Use bullet points or numbered lists "
                "only when the content is naturally a list, steps, or "
                "comparison. Otherwise answer in short plain sentences. "
                "Avoid long paragraphs."
            )
        },
    )


class SpeechBubble(QWidget):
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
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(QColor("#F7B6C2")))
    painter.setPen(QPen(QColor("#5A4038"), 3))
    painter.drawEllipse(width // 4, height // 8, width // 2, width // 2)
    painter.setBrush(QBrush(QColor("#A9C7E8")))
    body_top = height // 8 + width // 2 - 10
    painter.drawRoundedRect(width // 3, body_top, width // 3, height - body_top - 10, 12, 12)
    painter.end()
    return pixmap


app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
CHAR_SIZE, BUBBLE_MAX_HEIGHT, WALK_SPEED, WALK_TICK_MS = (160, 160), 220, 3, 40
window = QWidget()
window.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
window.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
window.setStyleSheet("background: transparent;")
layout = QVBoxLayout()
layout.setContentsMargins(0, 0, 0, 0)
layout.setSpacing(4)
character_label = QLabel()
character_pixmap_right = QPixmap(bundled_resource_path("character.png"))
if character_pixmap_right.isNull():
    character_pixmap_right = create_fallback_character(*CHAR_SIZE)
else:
    character_pixmap_right = character_pixmap_right.scaled(*CHAR_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
character_pixmap_left = character_pixmap_right.transformed(QTransform().scale(-1, 1))
character_label.setPixmap(character_pixmap_right)
character_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
character_label.setStyleSheet("background: transparent;")
layout.addWidget(character_label)


class ShadowWidget(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.base_width, self.base_height, self.scale = width, height, 1.0
        self.setFixedHeight(height + 6)
        self.setStyleSheet("background: transparent;")

    def set_scale(self, scale):
        self.scale = max(0.4, min(1.0, scale))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width, height = self.base_width * self.scale, self.base_height * self.scale
        cx, cy = self.width() / 2, self.height() / 2
        painter.setBrush(QBrush(QColor(0, 0, 0, int(90 * self.scale))))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawEllipse(QRectF(cx - width / 2, cy - height / 2, width, height))


shadow_widget = ShadowWidget(70, 18)
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
scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
scroll_area.hide()
scroll_area.viewport().setStyleSheet("background: transparent;")
layout.addWidget(scroll_area)
HISTORY_BOX_WIDTH, HISTORY_SIDEBAR_WIDTH, HISTORY_BOX_HEIGHT = 460, 150, 260
history_box = QWidget()
history_box.setFixedSize(HISTORY_BOX_WIDTH, HISTORY_BOX_HEIGHT)
history_box.setStyleSheet("QWidget#historyBox { background-color: white; border-radius: 16px; }")
history_box.setObjectName("historyBox")
history_box_layout = QHBoxLayout()
history_box_layout.setContentsMargins(0, 0, 0, 0)
history_box_layout.setSpacing(0)
history_box.setLayout(history_box_layout)
history_sidebar_scroll = QScrollArea()
history_sidebar_scroll.setFixedWidth(HISTORY_SIDEBAR_WIDTH)
history_sidebar_scroll.setWidgetResizable(True)
history_sidebar_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; border-right: 1px solid #e5e5e5; }")
history_sidebar = QWidget()
history_sidebar.setStyleSheet("background: transparent;")
history_sidebar_layout = QVBoxLayout()
history_sidebar_layout.setContentsMargins(8, 8, 8, 8)
history_sidebar_layout.setSpacing(4)
history_sidebar_layout.addStretch()
history_sidebar.setLayout(history_sidebar_layout)
history_sidebar_scroll.setWidget(history_sidebar)
history_content_label = QLabel("Select a day to view that conversation.")
history_content_label.setWordWrap(True)
history_content_label.setAlignment(Qt.AlignmentFlag.AlignTop)
history_content_label.setStyleSheet("background: transparent; color: black; padding: 12px;")
history_content_scroll = QScrollArea()
history_content_scroll.setWidget(history_content_label)
history_content_scroll.setWidgetResizable(True)
history_content_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
history_content_scroll.viewport().setStyleSheet("background: transparent;")
history_box_layout.addWidget(history_sidebar_scroll)
history_box_layout.addWidget(history_content_scroll)
history_box.hide()
layout.addWidget(history_box)
input_box = QLineEdit()
input_box.setPlaceholderText("How can I help you?")
input_box.setStyleSheet("QLineEdit { background-color: rgba(0, 0, 0, 160); color: white; border: none; border-radius: 10px; padding: 6px 10px; }")
input_box.hide()
layout.addWidget(input_box)
window.setLayout(layout)
window.adjustSize()
chat_history = ""
chat_label.setText(chat_history)
first_question_asked = history_view_active = chat_mode = False
walk_direction, dot_index = 1, 0
dot_states = ["Thinking", "Thinking.", "Thinking..", "Thinking..."]
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
        try:
            self.result_ready.emit(chat_session.send_message(self.question).text)
        except Exception as error:
            self.result_ready.emit(f"I couldn't reach Gemini: {error}")


current_worker = None


def show_answer(answer_text):
    global chat_history
    dot_timer.stop()
    chat_history += f"<b>Assistant:</b> {answer_text}<br><br>"
    chat_label.setText(chat_history)
    scroll_area.verticalScrollBar().setValue(scroll_area.verticalScrollBar().maximum())
    window.adjustSize()
    position_top_right()
    conversation_log.append({"role": "model", "text": answer_text, "timestamp": datetime.now().isoformat()})
    save_conversation_log(conversation_log)


def ask_gemini():
    global chat_history, first_question_asked, current_worker, dot_index
    question = input_box.text().strip()
    if not question:
        return
    if not first_question_asked:
        input_box.setPlaceholderText("Write a message")
        first_question_asked = True
    chat_history += f"<b>You:</b> {question}<br>"
    input_box.clear()
    input_box.hide()
    conversation_log.append({"role": "user", "text": question, "timestamp": datetime.now().isoformat()})
    save_conversation_log(conversation_log)
    scroll_area.show()
    dot_index = 0
    chat_label.setText("Thinking")
    dot_timer.start(400)
    window.adjustSize()
    current_worker = GeminiWorker(question)
    current_worker.result_ready.connect(show_answer)
    current_worker.start()


input_box.returnPressed.connect(ask_gemini)
DOCK_OVERLAP = 35


def dock_y():
    return app.primaryScreen().availableGeometry().bottom() - window.height() + DOCK_OVERLAP


def position_top_right():
    screen, margin = app.primaryScreen().availableGeometry(), 20
    window.move(screen.right() - window.width() - margin, screen.top() + margin)


last_dock_x = None


def wander_step():
    global walk_direction
    screen = app.primaryScreen().availableGeometry()
    if random.random() < 0.01:
        walk_direction *= -1
    new_x = window.x() + walk_direction * WALK_SPEED
    if new_x <= screen.left():
        new_x, walk_direction = screen.left(), 1
    elif new_x + window.width() >= screen.right():
        new_x, walk_direction = screen.right() - window.width(), -1
    window.move(new_x, dock_y())
    character_label.setPixmap(character_pixmap_right if walk_direction == 1 else character_pixmap_left)


wander_timer = QTimer()
wander_timer.timeout.connect(wander_step)


class Bridge(QObject):
    toggle_window_signal = pyqtSignal()
    toggle_input_signal = pyqtSignal()
    toggle_history_signal = pyqtSignal()


bridge = Bridge()


def enter_chat_mode():
    global chat_mode, last_dock_x
    chat_mode, last_dock_x = True, window.x()
    update_chat_action()
    wander_timer.stop()
    shadow_widget.hide()
    input_box.show()
    input_box.setFocus()
    window.adjustSize()
    position_top_right()


def exit_chat_mode():
    global chat_mode
    chat_mode = False
    update_chat_action()
    input_box.hide()
    scroll_area.hide()
    history_box.hide()
    shadow_widget.show()
    window.adjustSize()
    screen = app.primaryScreen().availableGeometry()
    x = last_dock_x if last_dock_x is not None else window.x()
    window.move(max(screen.left(), min(x, screen.right() - window.width())), dock_y())
    wander_timer.start(WALK_TICK_MS)


def toggle_window():
    exit_chat_mode() if chat_mode else enter_chat_mode()


def toggle_input():
    if not chat_mode:
        return
    input_box.setVisible(not input_box.isVisible())
    if input_box.isVisible():
        input_box.setFocus()
    window.adjustSize()


def group_history_by_day(log):
    groups = {}
    for turn in log:
        groups.setdefault(turn.get("timestamp", "unknown")[:10], []).append(turn)
    return groups


def format_day_label(day_key, turns):
    try:
        date_str = datetime.strptime(day_key, "%Y-%m-%d").strftime("%b %d, %Y")
    except ValueError:
        date_str = "Earlier"
    topic = next((turn["text"] for turn in turns if turn.get("role") == "user"), "")
    return date_str, topic[:34] + ("..." if len(topic) > 34 else "")


def show_history_day(day_key, turns):
    history_content_label.setText("".join(
        f"<b>{'You' if turn['role'] == 'user' else 'Assistant'}:</b> {turn['text']}<br>"
        + ("<br>" if turn['role'] != 'user' else "") for turn in turns
    ))
    history_content_scroll.verticalScrollBar().setValue(0)


def populate_history_sidebar():
    while history_sidebar_layout.count() > 1:
        item = history_sidebar_layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
    groups = group_history_by_day(conversation_log)
    day_keys = sorted(groups, reverse=True)
    if not day_keys:
        empty_label = QLabel("No past\nconversations yet.")
        empty_label.setStyleSheet("color: #999; font-size: 12px; background: transparent;")
        history_sidebar_layout.insertWidget(0, empty_label)
        history_content_label.setText("")
        return
    for day_key in day_keys:
        turns = groups[day_key]
        date_str, topic = format_day_label(day_key, turns)
        button = QPushButton(f"{date_str}\n{topic}")
        button.setStyleSheet("QPushButton { text-align: left; background: transparent; border: none; border-radius: 8px; padding: 6px; color: #222; font-size: 11px; } QPushButton:hover { background-color: #f0f0f0; }")
        button.clicked.connect(lambda checked=False, k=day_key, t=turns: show_history_day(k, t))
        history_sidebar_layout.insertWidget(history_sidebar_layout.count() - 1, button)
    show_history_day(day_keys[0], groups[day_keys[0]])


def toggle_history():
    global history_view_active
    if not chat_mode:
        return
    history_view_active = not history_view_active
    if history_view_active:
        scroll_area.hide()
        populate_history_sidebar()
        history_box.show()
    else:
        history_box.hide()
        scroll_area.setVisible(bool(chat_history))
    window.adjustSize()
    position_top_right()


bridge.toggle_window_signal.connect(toggle_window)
bridge.toggle_input_signal.connect(toggle_input)
bridge.toggle_history_signal.connect(toggle_history)
window_hotkey = keyboard.HotKey(keyboard.HotKey.parse('<cmd>+<shift>+a'), bridge.toggle_window_signal.emit)
input_hotkey = keyboard.HotKey(keyboard.HotKey.parse('<cmd>+<shift>+m'), bridge.toggle_input_signal.emit)
history_hotkey = keyboard.HotKey(keyboard.HotKey.parse('<cmd>+<shift>+h'), bridge.toggle_history_signal.emit)
hotkeys = [window_hotkey, input_hotkey, history_hotkey]


def on_press(key):
    canonical_key = listener.canonical(key)
    for hotkey in hotkeys:
        hotkey.press(canonical_key)


def on_release(key):
    canonical_key = listener.canonical(key)
    for hotkey in hotkeys:
        hotkey.release(canonical_key)


listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()


def create_tray_plus_icon():
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(QColor("#0A84FF")))
    painter.setPen(QPen(QColor("#0066CC"), 1))
    painter.drawEllipse(1, 1, 22, 22)
    pen = QPen(QColor("white"), 3)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    center, inset = pixmap.width() // 2, 7
    painter.drawLine(center, inset, center, pixmap.height() - inset)
    painter.drawLine(inset, center, pixmap.width() - inset, center)
    painter.end()
    return QIcon(pixmap)


tray_icon = QSystemTrayIcon(create_tray_plus_icon())
tray_icon.setToolTip("Zebraz")
tray_menu = QMenu()
chat_action = QAction("Chat with Buddy")
chat_action.triggered.connect(toggle_window)
tray_menu.addAction(chat_action)


def update_chat_action():
    chat_action.setText("Cancel Chat with Buddy" if chat_mode else "Chat with Buddy")


visibility_action = QAction("Hide Buddy")


def toggle_visibility():
    if window.isVisible():
        window.hide()
        wander_timer.stop()
        visibility_action.setText("Show Buddy")
    else:
        window.show()
        if not chat_mode:
            wander_timer.start(WALK_TICK_MS)
        visibility_action.setText("Hide Buddy")


visibility_action.triggered.connect(toggle_visibility)
tray_menu.addAction(visibility_action)
tray_menu.addSeparator()


def quit_app():
    listener.stop()
    tray_icon.hide()
    app.quit()


quit_action = QAction("Quit Zebraz")
quit_action.triggered.connect(quit_app)
tray_menu.addAction(quit_action)
tray_icon.setContextMenu(tray_menu)
tray_icon.show()
signal.signal(signal.SIGINT, signal.SIG_DFL)
signal_timer = QTimer()
signal_timer.start(200)
signal_timer.timeout.connect(lambda: None)
screen_geo = app.primaryScreen().availableGeometry()
window.move(screen_geo.center().x(), dock_y())
window.show()
wander_timer.start(WALK_TICK_MS)
sys.exit(app.exec())
