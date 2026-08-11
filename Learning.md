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

## Day 5 (cont.) — [Aug 7 2026]
- Removed setMask()-based window shaping after realizing it broke smooth
  alpha edges; reverted to WA_TranslucentBackground + native PNG alpha
- Spent significant time debugging a persistent "checkerboard/white box"
  transparency bug. Root cause: character.png's "transparent" areas were
  baked-in checkerboard pixels at full opacity (alpha=255), not real
  alpha=0 — despite Preview's "Has Alpha: 1" field, which only confirms
  the file format supports alpha, not that pixels use it correctly
- Learned to debug this properly by bisecting: isolated a minimal
  transparent QWidget test (worked), then a QLabel+QPixmap with a
  programmatically drawn shape (worked), then the real PNG file
  specifically (failed) — proving the bug was in the file, not the code
- Used Pillow (PIL) to read raw pixel RGBA values directly rather than
  trusting any app's summary/preview — confirmed alpha=255 everywhere,
  including "empty" checkerboard areas
- Fixed by detecting neutral gray/white pixels (both checkerboard colors)
  and setting their alpha to 0 programmatically
- Simplified the wandering animation: removed the bounce/hop + shadow
  pulse effect, kept flat horizontal walking bounded by the two screen
  edges (the visual dock boundaries)

## Day 6 — [Aug 11 2026]

- Packaged Zebraz as a standalone macOS app with `py2app`
- Learned: a packaged app does not run from the same working folder as a Terminal command, so relative file paths like `zebraz_memory.json` can point to different locations
- Fixed persistent memory by storing it in a stable macOS user-data location:
  `~/Library/Application Support/Zebraz/zebraz_memory.json`
- Learned to separate bundled resources from user data:
  - `character.png` and `.env` are read from the app bundle’s `Resources` folder
  - conversation history is saved outside the bundle so it survives rebuilds and app updates
- Added atomic memory saving: write to a temporary file first, then replace the previous file, reducing the chance of corrupted chat history
- Fixed the desktop pet disappearing when another app became active by removing Qt’s `Tool` window flag; macOS treats Tool windows as utility panels and hides them when the app loses focus
- Added a menu-bar tray icon with:
  - Chat / cancel chat
  - Show / hide Zebraz
  - Quit Zebraz
- Learned that macOS permissions apply separately to the packaged app and the Python interpreter, so Input Monitoring must be granted to `Zebraz.app` for global hotkeys to work
- Updated `.gitignore` to protect `.env`, generated build files, and local conversation-memory files from Git commits

