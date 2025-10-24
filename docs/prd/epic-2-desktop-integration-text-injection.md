# Epic 2: Desktop Integration & Text Injection

**Epic Goal:** Integrate the dictation engine with the Wayland desktop environment, enabling hotkey-activated dictation that automatically inserts transcribed text into focused applications via Wayland protocols or clipboard fallback. This epic transforms the CLI tool from Epic 1 into a seamless desktop application that power users can integrate into their daily workflow.

## Story 2.1: Wayland Window Focus Detection

**As a** user,
**I want** the application to detect which window/application is currently focused,
**so that** dictated text can be inserted into the correct target application.

**Acceptance Criteria:**

1. Wayland integration module implemented (src/wayland/window_focus.py)
2. Application tracks currently focused window
3. Focused window information: application name, window title, process ID
4. Focus information updated in real-time when user switches windows
5. When dictation activated, focused window at that moment is recorded as target
6. If window focus changes during transcription, text still injected to original target
7. Edge cases handled: No windows focused, multiple monitors, compositor doesn't expose focus
8. CLI debug command: `fedora-voice-dictation --show-focus` displays focused window info
9. Unit tests verify focus tracking with mocked Wayland responses
10. Integration test: Switch between windows, verify focus detection follows correctly

## Story 2.2: Clipboard-Based Text Injection (Fallback Method)

**As a** user,
**I want** transcribed text automatically copied to clipboard when direct injection fails,
**so that** I can manually paste it into my target application as a reliable fallback.

**Acceptance Criteria:**

1. Clipboard injection module implemented (src/wayland/clipboard_fallback.py)
2. Text injection function accepts transcribed text and target window info
3. Clipboard method copies text to system clipboard
4. Returns success status indicating "clipboard_fallback_used"
5. Tested on GNOME Wayland and works reliably
6. Clear notification: "Text copied to clipboard (Ctrl+V to paste)"
7. Notification includes reason why direct injection failed
8. Previous clipboard content NOT backed up (acceptable trade-off)
9. Empty transcriptions do not overwrite clipboard
10. Unicode text handled correctly
11. Performance: <50ms completion time
12. Integration test: Trigger fallback, verify text in clipboard, paste to confirm

## Story 2.3: Wayland text-input Protocol Implementation

**As a** user,
**I want** transcribed text directly injected into focused applications using Wayland protocols,
**so that** text appears automatically without manual pasting.

**Acceptance Criteria:**

1. Wayland text-input module implemented (src/wayland/text_input.py) using text-input-unstable-v3
2. Application establishes Wayland compositor connection on startup
3. Text injection via protocol attempted as primary method
4. Protocol implementation handles manager acquisition, text-input object creation, text commit
5. Tested and working on GNOME 43+ with gedit, GNOME Terminal, Firefox
6. Gracefully falls back to clipboard if protocol unavailable
7. Returns status: "success", "protocol_unavailable", "application_unsupported"
8. Diagnostic logging when protocol fails
9. Performance: <100ms completion time when successful
10. Edge cases: Multiple text fields, fullscreen apps, XWayland apps
11. Configuration option: text_injection_method (auto/protocol_only/clipboard_only)
12. Integration test: Inject text into gedit and terminal, verify appears without paste

## Story 2.4: Text Injection Orchestration and Method Selection

**As a** user,
**I want** the application to intelligently choose between Wayland protocol and clipboard injection,
**so that** text insertion works reliably across different applications.

**Acceptance Criteria:**

1. Text injection orchestrator implemented (src/wayland/text_injection.py)
2. Injection flow based on config: protocol_only, clipboard_only, or auto (try protocol, fallback clipboard)
3. Timeout: If protocol takes >500ms, abort and fallback to clipboard
4. Success/failure tracked per application for optimization
5. Application compatibility database tracks which apps work with which method
6. User notifications: Protocol success (silent), Clipboard fallback (notify), Both failed (error)
7. Injected text is exactly as produced by Whisper
8. Empty transcriptions do not trigger injection
9. Logging captures injection method, success/failure, target app, latency
10. CLI test command: `fedora-voice-dictation --test-injection "test text"`
11. Integration test: Test injection into 5 different applications
12. Performance: Total injection latency <150ms for 95% of cases

## Story 2.5: Global Hotkey Registration

**As a** user,
**I want** to activate dictation using a global keyboard shortcut,
**so that** I can start dictating without switching to the app window or clicking a button.

**Acceptance Criteria:**

1. Hotkey registration module implemented (src/core/hotkey.py)
2. Application registers global keyboard shortcut on startup
3. Default hotkey TBD after user testing
4. Hotkey configurable via config file
5. Compositor-specific registration methods: GNOME Shell D-Bus, KDE KGlobalAccel, fallback methods
6. Confirmation logged if registration succeeds
7. Warning if registration fails: "Global hotkeys unavailable. Use system tray or CLI."
8. Hotkey activation triggers state transition: idle → listening
9. Hotkey captured even when application not focused
10. Conflict detection suggests alternative hotkeys
11. Pressing hotkey while listening stops dictation (toggle)
12. Application unregisters hotkey on shutdown
13. Configuration includes enable_hotkey boolean
14. Integration test: Register hotkey, press it, verify dictation activates

## Story 2.6: System Tray Icon and Basic Menu

**As a** user,
**I want** a system tray icon showing application status,
**so that** I can see at a glance if the app is idle, listening, or processing.

**Acceptance Criteria:**

1. System tray module implemented (src/ui/system_tray.py) using PyQt5 QSystemTrayIcon
2. System tray icon appears on application startup
3. Uses StatusNotifierItem protocol for Wayland support
4. Four icon states: Idle (gray), Listening (blue), Processing (blue + spinner), Error (red)
5. Icon state updates automatically based on state machine transitions
6. Icons provided as SVG files for crisp rendering
7. Icons tested on light and dark themes
8. System tray menu: "Start Dictation", "Stop Dictation", "Quit"
9. Menu actions connected to state machine via Qt signals/slots
10. Tooltip shows current state
11. Left-click toggles dictation
12. Tested on GNOME 43+ (requires AppIndicator extension)
13. If tray unavailable, warning logged, app continues without tray
14. Integration test: Launch app, verify icon appears, click "Start Dictation"

## Story 2.7: Application State Machine

**As a** developer,
**I want** a centralized state machine managing application states,
**so that** UI, audio pipeline, and transcription coordination is clean and bug-free.

**Acceptance Criteria:**

1. State machine implemented (src/core/state_machine.py)
2. States defined: IDLE, LISTENING, PROCESSING, INJECTING, ERROR
3. Valid state transitions defined and enforced
4. Invalid transitions rejected with logged warning
5. Emits Qt signals on state changes: stateChanged(oldState, newState)
6. UI components subscribe to stateChanged signal
7. State transitions logged at INFO level
8. Thread-safe implementation
9. Timeout mechanisms: LISTENING >60s auto-idle, PROCESSING >10s auto-error
10. Current state exposed via get_state() method
11. Unit tests verify all valid transitions, invalid rejection, timeout behavior
12. Integration test: Trigger full workflow, verify states transition correctly

## Story 2.8: End-to-End Dictation Workflow Integration

**As a** user,
**I want** to press my hotkey, speak, and see text automatically appear in my focused application,
**so that** I can use voice dictation seamlessly in my daily workflow.

**Acceptance Criteria:**

1. Main application loop (src/core/main_loop.py) orchestrates all components
2. Startup sequence: Load config, initialize logging, load model, start audio, register hotkey, initialize tray, enter Qt event loop
3. Hotkey activation workflow: Press → Listening → Audio buffering → VAD active
4. Speech detection workflow: VAD detects silence → Processing → Audio sent to Whisper
5. Transcription and injection workflow: Whisper returns text → Injecting → Text injection → Idle
6. Total workflow latency: <2 seconds from speech end to text appearing (MVP target)
7. Edge cases handled: User switches windows, empty result, injection failure, multiple hotkey presses
8. All workflow steps logged
9. Integration test: Open gedit, press hotkey, speak test phrase, verify text appears in gedit within 2 seconds, verify system tray states transition correctly

## Story 2.9: Toast Notifications for State Changes

**As a** user,
**I want** desktop notifications when dictation starts, completes, or encounters errors,
**so that** I have confirmation of system activity.

**Acceptance Criteria:**

1. Notification module implemented using D-Bus org.freedesktop.Notifications
2. Notifications triggered: Listening started (optional), Text injection via clipboard, Error occurred
3. Notification durations: Success 3s auto-dismiss, Error persist until dismissed or 30s
4. Notifications include application icon
5. Error notifications include action buttons: "Retry", "Details", "Dismiss"
6. Configuration option: notification_level (all/errors_only/none)
7. Notifications respect system Do Not Disturb mode
8. If notification service unavailable, app continues without notifications
9. Notification text is concise and actionable
10. Integration test: Trigger dictation, verify notification appears, test action buttons

## Story 2.10: Multi-Desktop Environment Testing and Compatibility

**As a** user on KDE, Hyprland, or Sway,
**I want** the application to work on my desktop environment,
**so that** I'm not limited to GNOME.

**Acceptance Criteria:**

1. Testing matrix established for GNOME, KDE, Hyprland, Sway
2. Application tested on KDE Plasma 5.27+: System tray, hotkey (KGlobalAccel), text injection in Kate/Konsole/Dolphin, notifications
3. Application tested on Hyprland 0.30+: System tray (waybar), hotkey method determined, text injection tested
4. Application tested on Sway 1.8+: System tray (waybar/swaybar), hotkey method, text injection tested
5. Compatibility matrix documented in docs/compatibility.md with feature support per DE
6. Known issues and workarounds per DE documented
7. Setup instructions for each DE documented
8. README updated with supported desktop environments
9. GitHub issue templates include "Desktop Environment" field
10. Integration test: On each DE, run full dictation workflow

---
