# Epic 3: Configuration & Model Management

**Epic Goal:** Provide comprehensive user configuration capabilities through a settings UI, model download/management system, and persistent storage, allowing users to customize the application for their hardware, preferences, and workflow needs. This epic transforms the working application from Epic 2 into a fully configurable tool that adapts to individual user requirements.

## Story 3.1: Settings Window UI Framework

**As a** user,
**I want** a graphical settings window to configure all application options,
**so that** I can customize the application without editing configuration files manually.

**Acceptance Criteria:**

1. Settings window implemented (src/ui/settings_window.py) using PyQt5 QWidget
2. Window is non-modal
3. Window layout: Single scrolling page with 4 collapsible sections (Dictation, System, History & Privacy, Advanced)
4. Each section implemented as collapsible widget
5. Window size: 700x600 default, resizable, minimum 600x500
6. Window title: "Fedora Voice Dictation - Settings"
7. Respects desktop environment theme
8. Opened via system tray menu "Settings" action
9. Can also be opened via CLI: `fedora-voice-dictation --settings`
10. "Apply" and "Close" buttons at bottom
11. If already open, brings existing window to front
12. Window position remembered across sessions
13. Keyboard navigation works throughout
14. Unit tests verify window creation, section expansion/collapse
15. Integration test: Open settings, navigate with keyboard, verify all sections accessible

## Story 3.2: Dictation Settings Section

**As a** user,
**I want** to configure Whisper model, hotkey, and VAD sensitivity,
**so that** I can optimize dictation for my hardware and speaking style.

**Acceptance Criteria:**

1. Dictation section includes: Model selection (radio buttons), Model info, Manage Models button, Hotkey configuration, VAD sensitivity slider, Manual stop option checkbox
2. Model selection shows comparison info (size, speed, accuracy)
3. Changing model triggers confirmation if not downloaded
4. If model already loaded, shows "Apply & Reload Model" button
5. Hotkey capture widget displays current hotkey, "Change" and "Clear" buttons
6. Hotkey validates (must include modifier, warns about conflicts)
7. VAD sensitivity slider (0.1-1.0, step 0.1) with live audio level preview showing threshold
8. Settings saved to config file immediately when changed
9. Integration test: Change each setting, restart application, verify settings persisted

## Story 3.3: System Settings Section

**As a** user,
**I want** to configure audio device, text injection method, and feedback preferences,
**so that** I can optimize the application for my hardware and desktop environment.

**Acceptance Criteria:**

1. System section includes: Audio input device dropdown with refresh button, Test Audio button, Text injection method (radio buttons), Audio feedback checkboxes, GPU/CUDA display with Unload Model button, Show Audio Indicator checkbox
2. Audio device dropdown shows device name and type, default marked, refresh button re-scans
3. Test Audio opens modal dialog with live audio level meter
4. Text injection method options: Auto-detect, Protocol Only, Clipboard Only with help text
5. Audio feedback checkboxes: "Beep on start", "Beep on completion", "Beep on error"
6. GPU/CUDA display shows: GPU model, CUDA version, VRAM usage, "Unload Model" button
7. Settings changes apply immediately where possible
8. Integration test: Change audio device, verify dictation uses new device; change injection method, verify behavior changes

## Story 3.4: History & Privacy Settings Section

**As a** user,
**I want** to control session history tracking and privacy settings,
**so that** I can manage sensitive data and storage usage.

**Acceptance Criteria:**

1. History & Privacy section includes: Enable History checkbox, Retention Policy spinboxes, Excluded Applications list, Clear All History button, Export History button
2. Enable History checkbox with description and warning when disabled
3. Retention policy: "Keep last [500] sessions or [90] days"
4. Excluded Applications list with "Add" and "Remove" buttons
5. Clear All History with confirmation dialog
6. Export History opens file dialog for JSON or text format
7. Privacy warning displayed about sensitive data
8. Settings saved to config file immediately
9. Integration test: Disable history, dictate, verify no session saved; enable history, verify sessions saved

## Story 3.5: Advanced Settings Section

**As a** power user,
**I want** access to advanced configuration options like notifications, logging, and performance tuning,
**so that** I can fine-tune the application for my specific needs.

**Acceptance Criteria:**

1. Advanced section includes: Notification preferences (radio buttons), Audio level indicator position (dropdown), CPU fallback checkbox, Debug logging checkbox with warning, Log file location with "Open Folder" button
2. Notification preferences: All notifications, Errors only, None
3. Audio level indicator position: Bottom-right/left, Top-right/left
4. CPU fallback: "Enable CPU fallback if GPU fails" with help text
5. Debug logging with privacy warning about log file size
6. Log file location read-only with "Open Folder" button
7. All settings saved to config file
8. Integration test: Enable debug logging, dictate, verify debug entries in log; change indicator position, verify overlay moves

## Story 3.6: Model Download Manager

**As a** user,
**I want** to download, view, and delete Whisper models,
**so that** I can manage disk space and choose models appropriate for my hardware.

**Acceptance Criteria:**

1. Model management dialog implemented (src/ui/model_manager.py) as modal dialog
2. Opened from "Manage Models" button in Dictation section
3. Shows table of available models: Model Name, Size, Status, Action
4. Status shows: Downloaded (green checkmark), Not Downloaded, Downloading with progress, Download Failed
5. Action buttons: Download, Verify, Delete (with confirmation)
6. Download happens in background, updates dialog with progress
7. Toast notifications for completion and failure
8. HTTP resume capability for interrupted downloads
9. Models stored in ~/.local/share/fedora-voice-dictation/models/
10. Verify button checks file size and checksum
11. Cannot delete currently loaded model
12. "Close" button dismisses dialog
13. Integration test: Download small model, verify in list; delete model, verify removed

## Story 3.7: First-Run Setup Wizard

**As a** new user,
**I want** a guided setup wizard on first launch,
**so that** I can configure the application correctly without reading documentation.

**Acceptance Criteria:**

1. Setup wizard implemented (src/ui/setup_wizard.py) as modal multi-page dialog
2. Automatically appears on first launch (missing config file detected)
3. Can also be launched: `fedora-voice-dictation --setup-wizard`
4. 5 pages: Welcome, Model Selection, Audio Setup, Hotkey Configuration, Test Dictation
5. **Page 1 - Welcome:** Introduction, system requirements check (CUDA, microphone), "Next" button
6. **Page 2 - Model Selection:** Radio buttons for model, size/performance info, download with progress
7. **Page 3 - Audio Setup:** Device dropdown, live audio level meter, "Test" button
8. **Page 4 - Hotkey Configuration:** Key capture, conflict warnings, "Skip" option
9. **Page 5 - Test Dictation:** "Start Test" button, text box shows result, "Finish" button
10. Wizard navigation: "Back", "Next", "Cancel" buttons
11. Wizard state persisted if closed mid-setup
12. Config marked setup_complete: true when finished
13. Integration test: Delete config, launch app, complete wizard, verify app configured

## Story 3.8: Session History Tracking

**As a** user,
**I want** all my dictations automatically tracked in session history,
**so that** I can review or recover text if I accidentally lose it.

**Acceptance Criteria:**

1. History tracking module implemented (src/core/history.py)
2. Each dictation creates entry: Timestamp, text, target app, duration, latency, injection method, status
3. History saved to ~/.local/share/fedora-voice-dictation/history.json as JSON array
4. History file created automatically on first dictation
5. New entries appended atomically (temp file, rename)
6. Respects exclusion list and enable_history config
7. Automatic pruning on startup (>500 sessions OR oldest >90 days)
8. Empty transcriptions not saved
9. History entries include privacy flag
10. History file size monitored, warning if exceeds 50MB
11. Thread-safe history writes
12. Unit tests verify entry creation, pruning, atomic writes
13. Integration test: Perform 10 dictations, verify all in history.json with correct data

## Story 3.9: History Viewer UI

**As a** user,
**I want** to view, search, and export my dictation history,
**so that** I can find and recover past transcriptions.

**Acceptance Criteria:**

1. History viewer window implemented (src/ui/history_viewer.py) as non-modal window
2. Opened via system tray "View History" action
3. Window size: 900x600 default, resizable
4. Layout: Top toolbar (search, filter, refresh, export), main table, bottom panel (full text)
5. Table columns: Date/Time (sortable), Text Preview (first 100 chars), Application, Duration, Method
6. Table supports sorting by column headers
7. Clicking row displays full text in bottom panel
8. Search box filters rows by text content in real-time
9. Filter dropdown: All Sessions, Today, This Week, Last 30 Days, By Application
10. Each row includes action buttons: "Copy Text", "Re-Inject"
11. Bottom toolbar: "Export Filtered Results", "Clear All History", session count
12. Export to JSON or TXT formats
13. History auto-refreshes when new session added
14. Keyboard navigation support
15. Integration test: Open viewer, search for text, verify filtering; export history, verify file created

## Story 3.10: Settings Window Integration and Polish

**As a** user,
**I want** the settings window to be polished, intuitive, and well-integrated,
**so that** configuring the app is a pleasant experience.

**Acceptance Criteria:**

1. All settings sections (Stories 3.2-3.5) integrated into single window
2. Section collapsing/expanding animations smooth
3. Form validation implemented (constraints enforced)
4. Help tooltips added to all non-obvious controls
5. "Reset to Defaults" button with confirmation
6. Responsive UI updates (model changed → VRAM display updates)
7. Settings window accessible via: System tray, CLI, optional hotkey
8. "Documentation" button opens browser to GitHub docs
9. Visual polish: Consistent spacing, proper tab order, focus indicators
10. Settings requiring restart clearly indicated
11. All settings accessible via keyboard
12. Integration test: Open settings, navigate with Tab only, change every setting, verify all saved and applied

---
