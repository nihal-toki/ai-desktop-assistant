# 🤖 Zebraz — AI Desktop Assistant

> A macOS desktop AI assistant with a Shimeji-style desktop pet, hotkey activation, conversational UI, and Gemini-powered responses.

---

## 🚦 Current Status

**Phase:** Phase 1 — Core Desktop Assistant  
**Status:** 🟡 Nearing completion

### Currently working

- Global hotkey activation
- Gemini API integration
- PyQt6 chat interface
- Shimeji-style desktop pet
- Transparent character rendering
- Desktop wandering
- Chat mode
- Message input mode
- Conversation UI
- macOS-safe UI threading
- Native PNG transparency

---

## 🛠️ Technology

- **Language:** Python
- **UI:** PyQt6
- **AI:** Google Gemini API
- **Hotkeys:** pynput
- **Image processing:** Pillow
- **Platform:** macOS

---

## 🧭 Project Documentation

### Product

- [[01 - Product/Project Overview]]
- [[01 - Product/Phase 1]]
- [[01 - Product/Roadmap]]

### Architecture

- [[02 - Architecture/System Overview]]
- [[02 - Architecture/HLD]]
- [[02 - Architecture/LLD]]

### Features

- [[03 - Features/Hotkey System]]
- [[03 - Features/Chat UI]]
- [[03 - Features/Desktop Pet]]
- [[03 - Features/Memory]]

### AI

- [[04 - AI/Gemini Integration]]
- [[04 - AI/Prompt Design]]
- [[04 - AI/Memory System]]

### Development

- [[06 - Development/Learning Log]]
- [[06 - Development/Setup]]
- [[06 - Development/Technical Decisions]]
- [[06 - Development/TODO]]

### Testing

- [[07 - Testing/Test Plan]]
- [[07 - Testing/Bugs]]

---

## 📈 Development Timeline

**Day 1** — Project setup, Git, venv, Python fundamentals  
**Day 2** — Global hotkey + Gemini API  
**Day 3** — Hotkey → Gemini integration  
**Day 4** — PyQt6 chat UI + threading architecture  
**Day 5** — Shimeji desktop pet + animation + hotkey modes  
**Day 5 (continued)** — Transparency debugging and PNG alpha fix

---

## 🎯 Current Focus

> Complete and stabilize Phase 1 before moving to Phase 2.

### Next

- [ ] Finalize Phase 1 scope
- [ ] Document current architecture
- [ ] Document memory implementation
- [ ] Complete Phase 1 testing
- [ ] Stabilize current build

---

## 🗺️ Roadmap

- 🟡 **Phase 1:** Core Desktop Assistant
- ⚪ **Phase 2:** RAG Knowledge Assistant
- ⚪ **Phase 3:** Agent Tool Use
- ⚪ **Phase 4:** Multi-Agent Collaboration
- ⚪ **Phase 5:** AI Code Review Agent
- ⚪ **Phase 6:** Face Recognition + Memory

---

## 💻 Source Code

Project:

`ai-desktop-assistant/`

Key files:

- `assistant.py`
- `assistant_ui.py`
- `main.py`
- `hotkey_test.py`
- `widget_test.py`
- `zebraz_memory.json`
- `requirements.txt`
- `setup.py`