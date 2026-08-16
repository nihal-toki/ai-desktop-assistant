# ai-desktop-assistant

A macOS desktop AI assistant with hotkey activation and voice — built from scratch while learning Python and AI engineering fundamentals.

## Status

✅ Phase 1 complete — Core Desktop Assistant

Zebraz is a floating PyQt6 desktop companion with hotkey-activated chat (`Cmd+Shift+A`), persistent conversation memory, a transparent speech-bubble UI, and a menu-bar control with Show/Hide and Quit options.
The companion now stays where you place it instead of wandering. You can drag it around the screen, and its position is saved between launches. It also has playful click, pickup, and drop animations, plus a custom transparent puppy character image.

### Current features

- Global hotkeys using `pynput`
- Gemini-powered chat
- Persistent conversation history
- Chat history grouped by day
- Transparent floating PyQt6 window
- Draggable, pinned companion position
- Saved position in `~/Library/Application Support/Zebraz/zebraz_position.json`
- Click, pickup, and drop animations
- Custom PNG character with real per-pixel transparency
- Menu-bar controls for opening chat, showing/hiding the companion, and quitting
- macOS Accessibility and Input Monitoring support
- macOS packaging with `py2app`

## Roadmap

- [x] Phase 1: Core desktop assistant — hotkeys, chat, persistent memory, and menu-bar controls
- [ ] Phase 2: RAG knowledge assistant
- [ ] Phase 3: Agent tool use (AutoGen)
- [ ] Phase 4: Multi-agent collaboration
- [ ] Phase 5: AI code review agent
- [ ] Phase 6: Face recognition + memory