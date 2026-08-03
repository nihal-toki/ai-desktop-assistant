# Learning Log

## Day 1 — [Jul 5 2026]
- Set up GitHub repo + cloned into PyCharm
- Created virtual environment (venv)
- Learned: what a virtual environment is and why it isolates dependencies
- Learned: what .gitignore does and why .env should never be committed
- Ran my first Python script successfully

## Day 2 — [Aug 1 2026]
- Built global hotkey listener using pynput (Cmd+Shift+A triggers a callback)
- Learned: listener/callback pattern — pynput watches in the background and 
  calls your function when the event happens, instead of writing a loop that checks
- Hit a macOS Accessibility permission gotcha: PyCharm needed to be explicitly 
  enabled in System Settings > Privacy & Security > Accessibility, then restarted 
  before the hotkey listener worked reliably
- Confirmed Gemini API connection also works end-to-end (gemini-3.6-flash model — 
  had to switch off gemini-2.5-flash which is being deprecated)

## Day 3 — [Aug 2 2026]
- Combined hotkey listener + Gemini call into assistant.py
- Learned: input() pauses execution and waits for typed text
- Confirmed the hotkey works repeatedly (not just once) — 
  the listener stays alive and re-triggers ask_gemini() each press

## Day 4 — [Aug 3 2026]
- Built the floating PyQt6 widget: QApplication, QWidget, QLabel, QLineEdit, QScrollArea
- Learned: PyQt6 owns the main thread (app.exec()); pynput's listener runs on a
  background thread automatically via l.start()
- Hit a real threading crash: calling window.show()/hide() directly from the
  pynput thread crashed with NSException (macOS only allows UI updates from
  the main thread)
- Fixed with Qt signals: pynput thread emits a signal, Qt safely delivers it
  to the main thread where the window update happens
- Positioned the widget using app.primaryScreen().availableGeometry() to snap
  it to the top-right corner
- Built a simple chat-style UI: growing history + fixed input box at the bottom,
  changing placeholder text after first message, auto-scroll to latest
- Used system_instruction in the Gemini API call to control response formatting
  (concise, bullets only when genuinely list-shaped)