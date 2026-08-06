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

## Day 5 — [Aug 5 2026]
- Converted the widget into a Shimeji-style wandering desktop pet:
  frameless, transparent window (WA_TranslucentBackground) with no
  title bar, walking left-right along the bottom of the screen
- Learned: QTimer-driven animation loop (wander_step) recalculates
  position every ~40ms; direction flips at screen edges and randomly
  mid-walk for natural movement
- Added a bounce + shadow illusion for pseudo-3D depth: sine-wave
  vertical offset for hopping motion, paired with a custom-painted
  elliptical shadow that inversely scales (smaller/fainter when she's
  "up", larger/darker when she's "down") — classic 2D game depth trick
- Learned: QPixmap.transformed(QTransform().scale(-1,1)) mirrors an
  image, used to flip her sprite based on walking direction
- Split hotkeys: Cmd+Shift+A toggles full chat mode (she snaps to
  top-right corner, wandering pauses); Cmd+Shift+M toggles just the
  message input bar. Implemented via two separate pynput HotKey
  objects fed through one shared listener
- Fixed Ctrl+C not terminating the app: PyQt6's event loop blocks
  Python's normal signal handling; fixed with
  signal.signal(SIGINT, SIG_DFL) plus a small recurring QTimer that
  lets the interpreter check for signals
- Iterated on the character image itself: first version had a white
  "sticker" outline that looked like a background box once floating
  on the desktop; regenerated without the outline for true
  per-pixel transparency