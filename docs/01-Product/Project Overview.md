# Zebraz — Project Overview

## What is Zebraz?

Zebraz is a macOS desktop AI assistant built from scratch in Python.

The assistant combines an AI chatbot with a Shimeji-style desktop pet that lives on the user's screen. The pet can wander along the bottom of the desktop and can be activated through global keyboard shortcuts to interact with the AI.

The project is being developed while learning Python, AI engineering, desktop application development, and software architecture.

---

## Core Idea

The goal is to make an AI assistant feel like a **desktop companion**, rather than a traditional chatbot window.

Instead of opening a separate application every time the user wants to interact with the assistant:

1. Zebraz stays on the desktop.
2. The character continuously wanders along the bottom of the screen.
3. A global hotkey can activate the assistant.
4. The user can interact through a floating chat interface.
5. Gemini processes the user's request and generates the response.
6. The conversation can be maintained through the assistant's memory system.

---

## Platform

**Current platform:** macOS

The project currently depends on macOS-specific behavior including:

- Accessibility permissions for global hotkeys
- macOS desktop/window behavior
- PyQt6 transparent windows
- Native screen geometry

---

## Current Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| Desktop UI | PyQt6 |
| LLM | Google Gemini API |
| Global Hotkeys | pynput |
| Image Processing | Pillow |
| Platform | macOS |
| Memory | JSON-based storage |

---

## Current Features

### Global Hotkey

The assistant can be activated using:

`Cmd + Shift + A`

A separate hotkey is used for the message input mode:

`Cmd + Shift + M`

---

### Gemini Integration

The assistant can send user input to Google's Gemini API and receive an AI-generated response.

The current implementation uses the Gemini Flash model.

---

### Chat Interface

The assistant has a floating PyQt6 chat interface containing:

- Conversation history
- User input
- AI responses
- Scrollable conversation area
- Dynamic input behavior

---

### Desktop Pet

Zebraz behaves like a Shimeji-style desktop companion.

The character:

- Has a transparent background
- Wanders horizontally across the bottom of the screen
- Changes direction at screen boundaries
- Can be paused while chat mode is active

---

### Transparent Rendering

The desktop pet uses:

- Frameless windows
- `WA_TranslucentBackground`
- PNG alpha transparency

The transparency implementation required debugging the source PNG and correcting invalid alpha values.

---

## Current Development Phase

### Phase 1 — Core Desktop Assistant

**Status:** Nearing completion

Phase 1 focuses on establishing the core desktop assistant:

```text
Global Hotkey
      ↓
User Interaction
      ↓
Chat Interface
      ↓
Gemini API
      ↓
AI Response
      ↓
Desktop Companion