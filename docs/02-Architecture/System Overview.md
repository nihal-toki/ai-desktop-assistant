# Zebraz — System Overview

> High-level overview of how the current Phase 1 implementation works.

---

## 1. System Purpose

Zebraz is a macOS desktop AI assistant that combines:

- A Shimeji-style desktop pet
- Global keyboard shortcuts
- A floating chat interface
- Google Gemini for AI responses
- Conversation handling
- Local memory storage

The application runs locally on the user's Mac while communicating with the Gemini API when an AI response is required.

---

## 2. Main Components

### Global Hotkey Listener

**Technology:** `pynput`

The listener runs in the background and waits for global keyboard shortcuts.

Current shortcuts:

| Shortcut | Purpose |
|---|---|
| `Cmd + Shift + A` | Toggle full chat mode |
| `Cmd + Shift + M` | Toggle message input |

The listener remains active while the application is running.

---

### PyQt6 Application

**Technology:** PyQt6

PyQt6 manages the application's graphical interface and main event loop.

The Qt application owns the main UI thread.

Main responsibilities include:

- Creating windows
- Displaying the chat interface
- Updating widgets
- Handling UI events
- Running timers
- Rendering the desktop pet

---

### Qt Signal Communication

The `pynput` listener runs outside the Qt UI thread.

The application does not directly modify the UI from the listener thread.

Instead, the listener emits Qt signals.

The Qt main thread receives those signals and performs the required UI update.

This prevents the macOS UI threading crash encountered during development.

---

### Desktop Pet

The desktop pet is implemented as a transparent PyQt6 window.

Characteristics:

- Frameless window
- Transparent background
- PNG-based character
- Horizontal movement
- Screen-edge boundaries
- Direction changes
- Wandering pauses during chat mode

The pet remains active while the application is running.

---

### Chat Interface

The chat interface is implemented using PyQt6 widgets.

The current UI includes:

- Conversation history
- User input
- AI responses
- Scrollable chat area
- Dynamic placeholder text
- Automatic scrolling
- Floating positioning

The chat interface appears when the appropriate hotkey is triggered.

---

### Gemini Integration

The AI component communicates with Google's Gemini API.

The basic interaction is:

1. The user enters a message.
2. The application sends the message to Gemini.
3. Gemini processes the request.
4. Gemini returns an AI response.
5. The response is displayed in the chat interface.

A system instruction is also provided to control the response format.

---

### Memory

The project currently contains:

`zebraz_memory.json`

This file is intended to provide local conversation/memory persistence.

The exact memory behavior and lifecycle still need to be documented and verified.

---

## 3. Threading Model

The current application has two important execution contexts.

### Main Thread

The PyQt6 application owns the main UI thread.

The main thread is responsible for:

- UI
- Windows
- Widgets
- Timers
- Visual updates
- Desktop pet rendering

### Background Listener

The `pynput` listener runs in the background.

It is responsible for:

- Monitoring global keyboard shortcuts
- Detecting hotkey presses
- Triggering actions through Qt signals

### Communication

The background listener communicates with the PyQt6 main thread using Qt signals.

This keeps UI operations inside the Qt main thread.

---

## 4. Application Startup

When Zebraz starts:

1. The PyQt6 application is initialized.
2. The desktop pet is created.
3. The hotkey listener is started.
4. Required UI components are initialized.
5. The Qt application event loop starts.
6. Zebraz remains active until the application is terminated.

---

## 5. Chat Activation

When the user presses:

`Cmd + Shift + A`

the following happens:

1. `pynput` detects the hotkey.
2. The hotkey event is communicated to the Qt main thread.
3. Wandering is paused.
4. The assistant moves to the chat position.
5. The chat interface becomes available.
6. The user can interact with Zebraz.

---

## 6. Message Input Mode

When the user presses:

`Cmd + Shift + M`

the message input mode is toggled.

The user can then enter a message through the input interface.

The message is sent to Gemini when submitted.

---

## 7. AI Response Flow

The current AI interaction consists of:

1. User enters a message.
2. The chat interface receives the message.
3. The application prepares the Gemini request.
4. The request is sent to the Gemini API.
5. Gemini generates the response.
6. The application receives the response.
7. The response is displayed in the chat history.

---

## 8. Desktop Pet Behavior

The desktop pet continuously wanders horizontally along the bottom of the available screen area.

The wandering system:

- Updates the character position repeatedly.
- Keeps the character within screen boundaries.
- Changes direction at screen edges.
- Mirrors the character image according to movement direction.
- Pauses wandering when chat mode is active.

The movement is driven by a `QTimer`.

---

## 9. Transparency System

The desktop pet uses native PNG alpha transparency.

The implementation uses:

- `WA_TranslucentBackground`
- Frameless window
- PNG alpha channel

During development, a transparency bug was discovered.

The character PNG contained checkerboard pixels that were visually intended to represent transparency but were actually stored with full opacity.

The issue was isolated by testing:

1. A minimal transparent QWidget.
2. A QLabel with a programmatically generated transparent image.
3. The actual character PNG.

The first two tests worked correctly, while the real PNG failed.

Pillow was then used to inspect the raw RGBA pixel values.

The checkerboard pixels were found to have `alpha = 255`.

They were corrected programmatically by detecting the unwanted background pixels and setting their alpha value to `0`.

---

## 10. Screen Positioning

The application uses:

`app.primaryScreen().availableGeometry()`

to determine the available screen area.

This allows the application to position the desktop pet and chat interface relative to the user's screen.

The pet currently walks horizontally along the bottom area of the available screen.

---

## 11. Current Phase 1 Architecture

The current system consists of these major parts:

- `pynput` global hotkey listener
- PyQt6 application and UI
- Qt signal-based communication
- Desktop pet
- Chat interface
- Gemini API integration
- Local JSON memory
- Pillow-based image processing where required

The components work together to provide the core desktop assistant experience.

---

## 12. Current Architecture Boundaries

### Input Layer

Responsible for receiving user actions.

Current implementation:

- Global keyboard shortcuts
- Chat text input

### Application Layer

Responsible for coordinating the assistant.

Current implementation:

- Python application logic
- Hotkey handling
- UI state changes
- Gemini request handling

### Presentation Layer

Responsible for what the user sees.

Current implementation:

- PyQt6 chat interface
- Desktop pet
- Transparent rendering
- Animation

### AI Layer

Responsible for generating AI responses.

Current implementation:

- Gemini API
- System instruction
- User message processing

### Persistence Layer

Responsible for local stored information.

Current implementation:

- `zebraz_memory.json`

The persistence architecture still needs further documentation.

---

## 13. Related Documentation

- [[01 - Product/Project Overview]]
- [[01 - Product/Phase 1]]
- [[01 - Product/Roadmap]]
- [[02 - Architecture/HLD]]
- [[02 - Architecture/LLD]]

OVERVIEW

                              USER
                                │
                    ┌───────────┴───────────┐
                    │                       │
              Global Hotkey              Chat Input
                    │                       │
                    ▼                       │
              ┌───────────┐                 │
              │  pynput   │                 │
              │  Listener │                 │
              └─────┬─────┘                 │
                    │                       │
               Qt Signal                   │
                    │                       │
                    ▼                       │
             ┌──────────────┐              │
             │    PyQt6     │◄─────────────┘
             │  Main Thread │
             └──────┬───────┘
                    │
          ┌─────────┼─────────┐
          │         │         │
          ▼         ▼         ▼
     Desktop Pet  Chat UI   App Logic
          │         │         │
          │         │         ▼
          │         │    ┌─────────────┐
          │         └───►│   Gemini    │
          │              │     API     │
          │              └──────┬──────┘
          │                     │
          │                     ▼
          │                AI Response
          │                     │
          │                     ▼
          │                  Chat UI
          │
          ▼
     Screen / Desktop

                    ┌─────────────────┐
                    │ Local Memory    │
                    │ zebraz_memory   │
                    │     .json       │
                    └─────────────────┘