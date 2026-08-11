# Phase 1 — Core Desktop Assistant

## Objective

Build a functional macOS desktop AI assistant that can be activated globally and interacted with through a lightweight desktop companion interface.

---

## Phase 1 Goal

The user should be able to:

1. Have Zebraz running in the background.
2. See Zebraz wandering along the bottom of the desktop.
3. Activate the assistant using a global hotkey.
4. Open the chat interface.
5. Enter a message.
6. Send the message to Gemini.
7. Receive and display the AI response.
8. Continue the conversation through the chat interface.

---

## Core Components

### 1. Global Hotkey System

- `Cmd + Shift + A` → activate/toggle chat mode
- `Cmd + Shift + M` → activate message input
- Global listener implemented using `pynput`
- Multiple hotkeys handled through a shared listener

### 2. AI Integration

- Google Gemini API
- Gemini Flash model
- System instruction for response formatting
- User input → Gemini → response

### 3. Desktop Pet

- Shimeji-style character
- Frameless transparent window
- Native PNG alpha transparency
- Horizontal wandering
- Direction changes at screen boundaries
- Wandering pauses during chat mode

### 4. Chat Interface

- Built with PyQt6
- Conversation history
- User input
- AI responses
- Scrollable chat area
- Floating desktop interface

### 5. Threading

- PyQt6 owns the main UI thread
- `pynput` listener runs in the background
- Qt signals communicate between the listener and UI
- UI updates are performed safely on the Qt main thread

### 6. Memory

Current project contains:

`zebraz_memory.json`

Memory implementation still needs to be fully documented and verified.

---

## Phase 1 Status

| Component | Status |
|---|---|
| Python project setup | ✅ Complete |
| Git repository | ✅ Complete |
| Virtual environment | ✅ Complete |
| Global hotkey | ✅ Complete |
| Gemini API | ✅ Complete |
| PyQt6 chat UI | ✅ Complete |
| Thread-safe UI communication | ✅ Complete |
| Desktop pet | ✅ Complete |
| Transparent rendering | ✅ Complete |
| Wandering animation | ✅ Complete |
| Chat mode | ✅ Complete |
| Message input mode | ✅ Complete |
| Conversation memory | 🟡 Needs verification |
| Phase 1 testing | 🟡 In progress |
| Phase 1 finalization | 🟡 In progress |

---

## Phase 1 Completion Criteria

Phase 1 will be considered complete when:

- [ ] Global hotkeys work reliably
- [ ] Zebraz can run continuously without crashing
- [ ] Desktop pet renders correctly with transparency
- [ ] Wandering works reliably
- [ ] Chat mode works reliably
- [ ] Message input works reliably
- [ ] Gemini responses work reliably
- [ ] Conversation history behaves correctly
- [ ] Memory behavior is verified
- [ ] Major known bugs are resolved
- [ ] Phase 1 architecture is documented
- [ ] Phase 1 test plan is completed