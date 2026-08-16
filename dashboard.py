"""The full-window workspace for Zebraz Phase 2."""

import json
import os
from datetime import datetime

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox, QPushButton, QStackedWidget,
    QTextBrowser, QVBoxLayout, QWidget,
)


# --- Dark theme palette -----------------------------------------------------
# Everything below reads from this single palette so contrast stays
# consistent across pages instead of drifting per-widget.
BG_MAIN = "#181a24"
BG_SIDEBAR = "#12131b"
BG_CARD = "#232636"
BG_INPUT = "#1f212c"
BORDER = "#333648"
ACCENT = "#c0503b"
ACCENT_HOVER = "#a8402d"
TEXT_PRIMARY = "#f2f0ec"
TEXT_SECONDARY = "#9a95a3"
USER_BUBBLE_BG = "#2c2436"
USER_BUBBLE_BORDER = "#4a3a52"
USER_NAME_COLOR = "#d998a0"
ASSISTANT_BUBBLE_BG = "#20222e"
ASSISTANT_BUBBLE_BORDER = "#333648"
ASSISTANT_NAME_COLOR = "#e8e6e0"
WARNING_BG = "#3a2c22"
WARNING_TEXT = "#f0c8a8"
WARNING_BORDER = "#6b4a32"
MISSING_FILE_COLOR = "#e07a6b"


class DashboardWorker(QThread):
    answer_ready = pyqtSignal(str)

    def __init__(self, question, send_message):
        super().__init__()
        self.question = question
        self.send_message = send_message

    def run(self):
        try:
            self.answer_ready.emit(self.send_message(self.question))
        except Exception as error:
            self.answer_ready.emit(f"I couldn't reach Gemini: {error}")


class ZebrazDashboard(QWidget):
    """A compact workspace for chatting, browsing history, and managing files."""

    def __init__(
        self, conversation_log, save_conversation, send_message, data_path,
        reset_chat, set_companion_visible, companion_is_visible, quit_app,
    ):
        super().__init__()
        self.conversation_log = conversation_log
        self.save_conversation = save_conversation
        self.send_message = send_message
        self.data_path = data_path
        self.reset_chat = reset_chat
        self.set_companion_visible = set_companion_visible
        self.companion_is_visible = companion_is_visible
        self.quit_app = quit_app
        self.worker = None
        self.knowledge_file = self.data_path("zebraz_knowledge_files.json")
        self.knowledge_files = self.load_knowledge_files()

        self.setWindowTitle("Zebraz")
        self.setObjectName("dashboard")
        self.setMinimumSize(920, 620)
        self.resize(1040, 700)
        self.setStyleSheet(f"""
            QWidget#dashboard {{ background: {BG_MAIN}; color: {TEXT_PRIMARY}; font-family: "Helvetica Neue", Arial; }}
            QLabel {{ background: transparent; color: {TEXT_PRIMARY}; }}
            QFrame#sidebar {{ background: {BG_SIDEBAR}; border: none; border-right: 3px solid {ACCENT}; }}
            QFrame#sidebar QLabel {{ background: transparent; }}
            QLabel#brand {{ color: {TEXT_PRIMARY}; font-size: 25px; font-weight: 700; }}
            QLabel#tagline {{ color: {TEXT_SECONDARY}; font-size: 12px; }}
            QPushButton#nav {{ color: {TEXT_PRIMARY}; background: transparent; border: none; border-radius: 7px; padding: 11px 12px; text-align: left; font-size: 14px; }}
            QPushButton#nav:hover {{ background: #232842; }}
            QPushButton#nav:checked {{ background: {ACCENT}; color: white; }}
            QPushButton#primary {{ background: {ACCENT}; color: white; border: none; border-radius: 8px; padding: 11px 16px; font-weight: 700; }}
            QPushButton#primary:hover {{ background: {ACCENT_HOVER}; }}
            QPushButton#secondary {{ background: {BG_CARD}; color: {TEXT_PRIMARY}; border: 1px solid {BORDER}; border-radius: 8px; padding: 9px 13px; }}
            QPushButton#secondary:hover {{ background: #2a2d3d; }}
            QLineEdit {{ background: {BG_INPUT}; color: {TEXT_PRIMARY}; border: 1px solid {BORDER}; border-radius: 8px; padding: 13px 14px; font-size: 14px; }}
            QLineEdit:focus {{ border: 2px solid {ACCENT}; }}
            QTextBrowser, QListWidget {{ background: {BG_CARD}; color: {TEXT_PRIMARY}; border: 1px solid {BORDER}; border-radius: 10px; padding: 12px; }}
            QListWidget::item {{ border-radius: 7px; padding: 9px; color: {TEXT_PRIMARY}; }}
            QListWidget::item:selected {{ background: {ACCENT}; color: white; }}
            QListWidget::item:hover {{ background: #2a2d3d; }}
            QCheckBox {{ padding: 6px 0; color: {TEXT_PRIMARY}; }}
            QScrollBar:vertical {{ background: {BG_MAIN}; width: 10px; }}
            QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 5px; min-height: 24px; }}
            QScrollBar::handle:vertical:hover {{ background: {ACCENT}; }}
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self.make_sidebar())

        self.pages = QStackedWidget()
        self.pages.addWidget(self.make_chat_page())
        self.pages.addWidget(self.make_history_page())
        self.pages.addWidget(self.make_knowledge_page())
        self.pages.addWidget(self.make_settings_page())
        root.addWidget(self.pages, 1)
        self.show_page(0)

    def make_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 22, 16, 18)
        brand = QLabel("Zebraz")
        brand.setObjectName("brand")
        layout.addWidget(brand)
        tagline = QLabel("Your quiet desktop companion")
        tagline.setObjectName("tagline")
        tagline.setWordWrap(True)
        layout.addWidget(tagline)
        layout.addSpacing(26)
        self.nav_buttons = []
        for label, index in (("✦  New chat", 0), ("◷  History", 1), ("▣  Knowledge", 2), ("⚙  Settings", 3)):
            button = QPushButton(label)
            button.setObjectName("nav")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, i=index: self.show_page(i))
            layout.addWidget(button)
            self.nav_buttons.append(button)
        layout.addStretch()
        companion = QLabel("Desktop companion\nready to wander")
        companion.setObjectName("tagline")
        companion.setWordWrap(True)
        layout.addWidget(companion)
        return sidebar

    def page_layout(self, title, subtitle):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(36, 30, 36, 30)
        layout.setSpacing(14)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {TEXT_PRIMARY};")
        layout.addWidget(title_label)
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)
        return page, layout

    def make_chat_page(self):
        page, layout = self.page_layout("Chat with Zebraz", "Ask anything. Your conversations are saved privately on this Mac.")
        self.chat_view = QTextBrowser()
        self.chat_view.setOpenExternalLinks(True)
        layout.addWidget(self.chat_view, 1)
        row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Message Zebraz…")
        self.chat_input.returnPressed.connect(self.ask_question)
        row.addWidget(self.chat_input, 1)
        send = QPushButton("Send")
        send.setObjectName("primary")
        send.clicked.connect(self.ask_question)
        row.addWidget(send)
        layout.addLayout(row)
        self.refresh_chat()
        return page

    def make_history_page(self):
        page, layout = self.page_layout("History", "Browse conversations saved by date.")
        body = QHBoxLayout()
        self.history_days = QListWidget()
        self.history_days.setFixedWidth(235)
        self.history_days.currentItemChanged.connect(self.show_history_day)
        body.addWidget(self.history_days)
        self.history_view = QTextBrowser()
        body.addWidget(self.history_view, 1)
        layout.addLayout(body, 1)
        return page

    def make_knowledge_page(self):
        page, layout = self.page_layout("Knowledge", "Add PDFs, text files, or Markdown notes that Zebraz will search in the next step of Phase 2.")
        upload = QPushButton("Upload files")
        upload.setObjectName("primary")
        upload.clicked.connect(self.upload_knowledge_files)
        layout.addWidget(upload, alignment=Qt.AlignmentFlag.AlignLeft)
        note = QLabel("Files stay on your Mac. Uploading creates your local knowledge library; document search will be connected next.")
        note.setWordWrap(True)
        note.setStyleSheet(f"background: {WARNING_BG}; color: {WARNING_TEXT}; border: 1px solid {WARNING_BORDER}; border-radius: 8px; padding: 12px;")
        layout.addWidget(note)
        self.knowledge_list = QListWidget()
        layout.addWidget(self.knowledge_list, 1)
        remove = QPushButton("Remove selected file")
        remove.setObjectName("secondary")
        remove.clicked.connect(self.remove_selected_knowledge_file)
        layout.addWidget(remove, alignment=Qt.AlignmentFlag.AlignLeft)
        self.refresh_knowledge_list()
        return page

    def make_settings_page(self):
        page, layout = self.page_layout("Settings", "Control how Zebraz appears and manage your local data.")
        tray_section = QLabel("Menu bar and companion")
        tray_section.setStyleSheet(f"font-size: 17px; font-weight: 650; margin-top: 12px; color: {TEXT_PRIMARY};")
        layout.addWidget(tray_section)
        tray_note = QLabel("Zebraz stays available in the menu bar so you can open the workspace, show or hide the companion, or quit safely.")
        tray_note.setWordWrap(True)
        tray_note.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(tray_note)
        self.companion_toggle = QCheckBox("Show desktop companion")
        self.companion_toggle.setChecked(self.companion_is_visible())
        self.companion_toggle.toggled.connect(self.set_companion_visible)
        layout.addWidget(self.companion_toggle)
        layout.addSpacing(12)
        character_section = QLabel("Character")
        character_section.setStyleSheet(f"font-size: 17px; font-weight: 650; color: {TEXT_PRIMARY};")
        layout.addWidget(character_section)
        character_card = QLabel("Zebraz\nYour current desktop companion. More characters will be available in Phase 3.")
        character_card.setWordWrap(True)
        character_card.setStyleSheet(f"background: {BG_CARD}; color: {TEXT_PRIMARY}; border: 1px solid {BORDER}; border-radius: 12px; padding: 14px;")
        layout.addWidget(character_card)
        layout.addSpacing(12)
        data_section = QLabel("Local data")
        data_section.setStyleSheet(f"font-size: 17px; font-weight: 650; color: {TEXT_PRIMARY};")
        layout.addWidget(data_section)
        clear_button = QPushButton("Clear conversation history")
        clear_button.setObjectName("secondary")
        clear_button.clicked.connect(self.clear_history)
        layout.addWidget(clear_button, alignment=Qt.AlignmentFlag.AlignLeft)
        quit_button = QPushButton("Quit Zebraz")
        quit_button.setObjectName("secondary")
        quit_button.clicked.connect(self.quit_app)
        layout.addWidget(quit_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        return page

    def show_page(self, index):
        self.pages.setCurrentIndex(index)
        for button_index, button in enumerate(self.nav_buttons):
            button.setChecked(button_index == index)
        if index == 0:
            self.refresh_chat()
            self.chat_input.setFocus()
        elif index == 1:
            self.refresh_history()
        elif index == 2:
            self.refresh_knowledge_list()
        elif index == 3:
            self.companion_toggle.setChecked(self.companion_is_visible())

    def open_workspace(self):
        self.refresh_chat()
        self.show()
        self.raise_()
        self.activateWindow()

    def refresh_chat(self):
        html = ""
        for turn in self.conversation_log:
            is_user = turn.get("role") == "user"
            name = "You" if is_user else "Zebraz"
            name_color = USER_NAME_COLOR if is_user else ASSISTANT_NAME_COLOR
            background = USER_BUBBLE_BG if is_user else ASSISTANT_BUBBLE_BG
            border = USER_BUBBLE_BORDER if is_user else ASSISTANT_BUBBLE_BORDER
            text = str(turn.get("text", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            html += (
                f"<div style='background:{background}; border:1px solid {border}; "
                f"border-radius:12px; padding:11px 13px; margin:8px 4px;'>"
                f"<b style='color:{name_color}'>{name}</b><br><span style='color:{TEXT_PRIMARY}'>{text}</span></div>"
            )
        self.chat_view.setHtml(html or f"""
            <div style='margin: 88px 28px; text-align: center;'>
              <div style='font-size: 42px; color:{ACCENT};'>✿</div>
              <h2 style='color:{TEXT_PRIMARY};'>Hello, I'm Zebraz</h2>
              <p style='color:{TEXT_SECONDARY}; font-size:14px;'>Ask a question, plan something, or upload files in Knowledge<br>when you're ready to build your local library.</p>
            </div>
        """)
        self.chat_view.verticalScrollBar().setValue(self.chat_view.verticalScrollBar().maximum())

    def ask_question(self):
        question = self.chat_input.text().strip()
        if not question or self.worker is not None:
            return
        self.chat_input.clear()
        self.conversation_log.append({"role": "user", "text": question, "timestamp": datetime.now().isoformat()})
        self.save_conversation(self.conversation_log)
        self.refresh_chat()
        self.chat_input.setPlaceholderText("Zebraz is thinking…")
        self.chat_input.setEnabled(False)
        self.worker = DashboardWorker(question, self.send_message)
        self.worker.answer_ready.connect(self.show_answer)
        self.worker.finished.connect(self.finish_answer)
        self.worker.start()

    def show_answer(self, answer):
        self.conversation_log.append({"role": "model", "text": answer, "timestamp": datetime.now().isoformat()})
        self.save_conversation(self.conversation_log)
        self.refresh_chat()

    def finish_answer(self):
        self.worker = None
        self.chat_input.setEnabled(True)
        self.chat_input.setPlaceholderText("Message Zebraz…")
        self.chat_input.setFocus()

    def refresh_history(self):
        self.history_days.clear()
        groups = {}
        for turn in self.conversation_log:
            groups.setdefault(turn.get("timestamp", "Earlier")[:10], []).append(turn)
        for day, turns in sorted(groups.items(), reverse=True):
            topic = next((turn.get("text", "") for turn in turns if turn.get("role") == "user"), "Conversation")
            try:
                label = datetime.strptime(day, "%Y-%m-%d").strftime("%b %d, %Y")
            except ValueError:
                label = "Earlier"
            item = QListWidgetItem(f"{label}\n{topic[:42]}{'…' if len(topic) > 42 else ''}")
            item.setData(Qt.ItemDataRole.UserRole, turns)
            self.history_days.addItem(item)
        if self.history_days.count():
            self.history_days.setCurrentRow(0)
        else:
            self.history_view.setHtml(f"<p style='color:{TEXT_SECONDARY}'>No saved conversations yet.</p>")

    def show_history_day(self, item):
        if item is None:
            return
        html = ""
        for turn in item.data(Qt.ItemDataRole.UserRole):
            is_user = turn.get("role") == "user"
            name = "You" if is_user else "Zebraz"
            name_color = USER_NAME_COLOR if is_user else ASSISTANT_NAME_COLOR
            text = str(turn.get("text", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            html += f"<p><b style='color:{name_color}'>{name}:</b><br><span style='color:{TEXT_PRIMARY}'>{text}</span></p>"
        self.history_view.setHtml(html)

    def load_knowledge_files(self):
        try:
            with open(self.knowledge_file, "r", encoding="utf-8") as file:
                files = json.load(file)
            return [path for path in files if isinstance(path, str)]
        except (OSError, json.JSONDecodeError):
            return []

    def save_knowledge_files(self):
        with open(self.knowledge_file, "w", encoding="utf-8") as file:
            json.dump(self.knowledge_files, file, indent=2)

    def refresh_knowledge_list(self):
        self.knowledge_list.clear()
        for path in self.knowledge_files:
            name = os.path.basename(path)
            status = "Ready" if os.path.exists(path) else "File not found"
            item = QListWidgetItem(f"{name}\n{status} · {path}")
            item.setData(Qt.ItemDataRole.UserRole, path)
            if not os.path.exists(path):
                item.setForeground(QColor(MISSING_FILE_COLOR))
            self.knowledge_list.addItem(item)
        if not self.knowledge_files:
            self.knowledge_list.addItem("No files yet. Upload a PDF, TXT, or Markdown file to begin.")

    def upload_knowledge_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Add knowledge files", "", "Knowledge files (*.pdf *.txt *.md *.markdown)"
        )
        for path in paths:
            if path not in self.knowledge_files:
                self.knowledge_files.append(path)
        self.save_knowledge_files()
        self.refresh_knowledge_list()

    def remove_selected_knowledge_file(self):
        item = self.knowledge_list.currentItem()
        if item is None:
            return
        path = item.data(Qt.ItemDataRole.UserRole)
        if path in self.knowledge_files:
            self.knowledge_files.remove(path)
            self.save_knowledge_files()
            self.refresh_knowledge_list()

    def clear_history(self):
        choice = QMessageBox.question(
            self, "Clear conversation history", "Remove all saved conversations from this Mac?",
            QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.Cancel,
        )
        if choice == QMessageBox.StandardButton.Yes:
            self.conversation_log.clear()
            self.save_conversation(self.conversation_log)
            self.reset_chat()
            self.refresh_chat()
            self.refresh_history()