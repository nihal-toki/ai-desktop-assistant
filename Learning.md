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