# User Interface Design Goals

## Overall UX Vision

Fedora Voice Dictation adopts an "invisible until needed" UX philosophy optimized for power users who value speed and keyboard-centric workflows. The interface prioritizes minimal disruption to workflow while providing clear feedback about system state and actionable error recovery when needed.

**Core Interface Elements:**

1. **System Tray Presence:** Persistent background service with status-aware tray icon providing at-a-glance feedback (idle/listening/processing/error states indicated by icon variations and optional audio cues)
2. **Hotkey-First Interaction:** Primary activation via global keyboard shortcut, enabling users to trigger dictation without breaking focus from current work
3. **CLI Fallback:** Command-line interface providing all critical functions for environments where system tray is unavailable or users prefer terminal interaction
4. **Minimal Configuration UI:** Settings accessible when needed but hidden by default, using clean Qt-native interface matching desktop environment theme

**Interaction Model:**

The core workflow is "speak and forget" - users press hotkey, speak naturally, and return to work while the system handles detection, transcription, and text injection transparently. Visual and audio feedback provide state confirmation without demanding attention. When automation fails (VAD, text injection), the system degrades gracefully with clear error messages and recovery options.

**Key UX Principles:**
- **Zero-interruption dictation:** No modal dialogs during dictation sessions; non-modal settings window
- **Multi-modal feedback:** Visual (icon) + audio (optional beeps) + notifications for state changes
- **Progressive disclosure:** Common functions accessible immediately; advanced features discoverable but not prominent
- **Graceful degradation:** When features fail (hotkey registration, text injection), fallbacks work and explain what happened
- **CLI-first fallback:** All functions accessible via command line for headless, minimal DE, or power user preference

## Key Interaction Paradigms

**1. Hotkey-Triggered Workflow (Primary - 80% of usage)**
- User presses global hotkey (default: TBD after user testing, configurable)
- Audio cue plays (subtle beep, optional, enabled by default)
- System tray icon changes to "listening" state (blue microphone)
- Optional: Simple 3-bar audio level indicator appears in fixed corner position
- VAD automatically detects speech start/end
- Transcription happens transparently, text appears word-by-word in target application
- Audio cue on completion (different tone)
- System returns to idle state
- *Success path:* No windows opened, no focus stolen, entire interaction keyboard-driven + audio feedback

**2. CLI Activation Workflow (Alternative - 15% of usage)**
- User executes `fedora-voice-dictation --start` in terminal
- Same behavior as hotkey activation
- User can `--stop` manually or rely on VAD
- Useful for: Scripting, environments without hotkey support, headless testing
- All settings configurable via CLI flags: `--model base`, `--vad-sensitivity 0.7`

**3. Manual Control Workflow (Fallback - 5% of usage)**
- User clicks system tray icon to open quick menu
- "Start Dictation" menu item triggers listening mode
- User speaks, VAD auto-stops OR user clicks "Stop Dictation" menu item
- Same transparent transcription and text injection
- *Use case:* Compositor doesn't support global hotkeys, user prefers mouse interaction

**4. First-Run Setup (One-time)**
- User launches app for first time
- System tray icon appears, toast notification: "Fedora Voice Dictation - Click to set up"
- User clicks icon → Settings window opens automatically
- **Setup wizard flow:**
  1. Welcome screen: "Select Whisper model (base recommended for RTX 4060)"
  2. Model download with progress bar (shows MB downloaded, speed, ETA)
  3. Audio device selection: "Test your microphone" button with live level meter
  4. Hotkey configuration: "Press your desired hotkey combination" (with conflict warning)
  5. Quick test: "Press your hotkey and say 'testing one two three'" → Shows transcription result
  6. Completion: "Setup complete! See documentation for advanced settings."
- Settings remain open (non-modal) for user to explore or close

**5. Configuration Workflow (Infrequent)**
- User accesses Settings from system tray menu or via `fedora-voice-dictation --settings`
- Non-modal settings window opens (single scrolling page with collapsible sections)
- Changes apply immediately for most settings
- Model changes show "Apply & Reload Model" button
- Settings saved automatically

**6. History Review Workflow**
- User accesses "View History" from system tray menu or via `fedora-voice-dictation --history`
- Dedicated history window opens (non-modal)
- Table view with search/filter, action buttons (Copy, Re-Inject)

**7. Error Recovery Workflow**
- Text injection fails → Toast notification with "Retry" and "Why?" buttons
- CUDA fails → Persistent notification with diagnostic link, CPU fallback enabled
- VAD false trigger → User can undo or adjust sensitivity

**8. Diagnostic Workflow**
- User accesses "Diagnostics" from system tray Help submenu
- Diagnostic window runs automatic tests (GPU/CUDA, Audio, Text Injection, Hotkey, System Tray)
- Results exportable for bug reports

## Core Screens and Views

**MVP Scope (Must Have):**

1. **System Tray Icon & Menu** - Primary interface, always present
2. **Settings Window** - Single scrolling window with 4 collapsible sections
3. **Audio Level Indicator** - Simple 3-bar level meter in fixed corner
4. **Toast Notifications** - Standard desktop notifications
5. **History Viewer** - Table view with search/filter
6. **Model Download Progress** - Toast notification with progress bar
7. **Diagnostic Tools Window** - Test runners with pass/fail results

**Post-MVP / Future:**
- Advanced Waveform Overlay
- Command Palette
- Snippet Manager

## Accessibility: Keyboard Navigation (MVP), WCAG AA (Post-MVP)

**MVP Accessibility Scope:**

✅ **Keyboard Navigation (Fully Implemented):**
- All UI controls accessible via keyboard
- Clear focus indicators
- Logical tab order
- Keyboard shortcuts displayed in menus

✅ **High Contrast Icons (Fully Implemented):**
- System tray icons use shape AND color
- Text labels in all menus

✅ **Screen Reader Basic Support (Best Effort):**
- Qt widgets have accessible names
- State change announcements via D-Bus
- Basic Orca testing

⚠️ **WCAG AA Deferred to Phase 2**

## Branding

**Visual Identity:** Minimal, utilitarian, Linux-native aesthetic

- **Native Qt Theming:** Respects system theme automatically
- **Icon Design:** Simple microphone icon with state variations
- **Color Palette:** Semantic colors only (blue=active, red=error, green=success)
- **Typography:** System default fonts
- **Animations:** Functional only (no decorative effects)
- **Voice & Tone:** Clear, technical, actionable

## Target Device and Platforms: Desktop Linux (Wayland)

**Primary Target:**
- Fedora Linux 38+ on Wayland
- Desktop Environments: GNOME 43+, KDE Plasma 5.27+, Hyprland 0.30+, Sway 1.8+
- 1920x1080 minimum resolution
- Physical keyboard + mouse + microphone required

**Explicitly Out of Scope:**
- X11 desktop environments
- Non-Linux operating systems
- Mobile devices
- Web browsers/interfaces
- Remote desktop scenarios

---
