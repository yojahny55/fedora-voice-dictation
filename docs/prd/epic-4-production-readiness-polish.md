# Epic 4: Production Readiness & Polish

**Epic Goal:** Transform the functional MVP into a production-ready application with diagnostic tools, comprehensive error handling, cross-desktop environment compatibility testing, packaging for distribution, and complete documentation. This epic ensures the application is stable, supportable, and ready for public release to the early adopter community.

## Story 4.1: Diagnostic Tools Window

**As a** user,
**I want** built-in diagnostic tools to test GPU/CUDA, audio, text injection, and hotkeys,
**so that** I can troubleshoot issues independently without developer assistance.

**Acceptance Criteria:**

1. Diagnostic window implemented (src/ui/diagnostics.py) as modal dialog
2. Opened via system tray "Help" → "Diagnostics" or CLI: `fedora-voice-dictation --diagnose`
3. 5 diagnostic test categories: GPU/CUDA, Audio Input, Text Injection, Hotkey Registration, System Tray
4. Each test shows status: ⏳ Pending, 🔄 Running, ✅ Pass, ⚠️ Warning, ❌ Fail
5. **GPU/CUDA Test:** Checks CUDA availability, driver, toolkit version, GPU model, VRAM; loads base model
6. **Audio Input Test:** Lists devices, tests selected device with 3s capture and level graph
7. **Text Injection Test:** Instructions to focus window, tests both methods, injects test string
8. **Hotkey Registration Test:** Displays configured hotkey, tests registration success
9. **System Tray Test:** Checks StatusNotifierItem availability
10. "Run All Tests" button executes all sequentially
11. Detailed results panel (scrollable text)
12. Bottom toolbar: "Export Report", "Copy to Clipboard", "Close"
13. Export includes: System info, test results, app version, config summary
14. Integration test: Run diagnostics, verify all tests execute and display correct results

## Story 4.2: Audio Level Indicator Overlay

**As a** user,
**I want** a visual indicator showing audio input levels while listening,
**so that** I know the microphone is capturing my voice.

**Acceptance Criteria:**

1. Audio level indicator implemented (src/ui/audio_indicator.py) as frameless overlay window
2. Appears when state transitions to LISTENING, disappears when PROCESSING or IDLE
3. Simple 3-bar level meter: Low (>0.1), Medium (>0.3), High (>0.6)
4. Bars colored green when lit, gray when unlit
5. Indicator size: 60px wide × 20px tall (compact)
6. Position configurable in settings (bottom-right, bottom-left, top-right, top-left)
7. Semi-transparent background (80% opacity)
8. Stay-on-top without stealing focus
9. Updates at 15 FPS
10. Can be disabled via settings: "Show Audio Indicator" checkbox
11. Position persisted in config
12. Multi-monitor support (best effort)
13. Performance validation: <5% CPU during active dictation
14. Disappears immediately when dictation stops
15. Integration test: Enable indicator, speak at varying volumes, verify bars light up; change position, verify moves

## Story 4.3: Audio Feedback (Beeps)

**As a** user,
**I want** optional audio beeps when dictation starts, completes, or errors,
**so that** I have confirmation without looking at visual indicators.

**Acceptance Criteria:**

1. Audio feedback module implemented (src/utils/audio_feedback.py)
2. Three distinct beeps: Start (rising tone ~200ms, 800Hz→1000Hz), Complete (descending ~200ms, 1000Hz→800Hz), Error (two short ~100ms, 600Hz)
3. Beeps generated programmatically using numpy and sounddevice
4. Beeps played through system default audio output
5. Beep volume uses system volume
6. Beeps triggered by state transitions: IDLE→LISTENING (start), INJECTING→IDLE (complete), →ERROR (error)
7. Settings in Advanced section: Checkboxes for each beep type (all enabled by default)
8. Beeps respect system audio settings (muted system = no beeps)
9. Beeps play asynchronously (don't block dictation)
10. If beep playback fails, failure logged but app continues
11. Performance: Beep generation and playback adds <10ms latency
12. Integration test: Enable all beeps, perform dictation, verify beeps at correct times; disable, verify silent

## Story 4.4: Comprehensive Error Handling and Recovery

**As a** user,
**I want** clear error messages and recovery options when things go wrong,
**so that** I can resolve issues quickly or report them effectively.

**Acceptance Criteria:**

1. Error handling module (src/core/error_handler.py) centralizes error management
2. All error scenarios have defined messages and recovery workflows:
   - CUDA initialization failure
   - Audio device disconnected
   - Text injection failure
   - Hotkey registration failure
   - Model download failure
   - Configuration file corruption
   - Disk space exhausted
   - Network timeout during model download
3. **CUDA failure:** "GPU acceleration unavailable. Running in CPU mode." with Details and Fix Guide buttons
4. **Audio disconnected:** "Microphone disconnected. Select another device in Settings." with auto-retry
5. **Text injection failure:** "Text injection failed. Text copied to clipboard." with Retry and Why? buttons
6. **Hotkey failure:** "Global hotkeys unavailable. Use system tray or CLI." with workarounds in settings
7. **Model download failure:** Specific error (network, disk full, corruption) with Retry action
8. **Config corruption:** Backup created, defaults restored, notification displayed
9. **Disk space exhausted:** "Disk space low. Free up space or history/logs may be lost."
10. All errors logged at ERROR level with full context
11. Critical errors include diagnostic info in notification
12. Integration test: Simulate each error scenario, verify appropriate message and recovery displayed

## Story 4.5: Cross-Desktop Environment Compatibility Fixes

**As a** user on KDE, Hyprland, or Sway,
**I want** the application to work reliably on my desktop environment,
**so that** I'm not forced to use GNOME.

**Acceptance Criteria:**

1. Testing performed on all 4 target DEs (GNOME, KDE, Hyprland, Sway)
2. **KDE Plasma 5.27+ specific fixes:** System tray, hotkey (KGlobalAccel), text injection in Kate/Konsole/Dolphin, Qt theme (Breeze)
3. **Hyprland 0.30+ specific fixes:** System tray (waybar), hotkey method, text injection (likely clipboard-only), configuration requirements documented
4. **Sway 1.8+ specific fixes:** System tray (waybar/swaybar), hotkey (swaymsg bindsym), text injection tested
5. Compatibility matrix updated in docs/compatibility.md with feature support table per DE
6. Known issues and workarounds documented per DE
7. Setup instructions for each DE added to docs/
8. Critical feature failures documented clearly with alternative workflows
9. Community testing solicited via GitHub issue templates
10. Integration test: On each DE, run full dictation workflow, document results

## Story 4.6: RPM Packaging for Fedora

**As a** Fedora user,
**I want** to install the application via an RPM package,
**so that** installation is standardized and dependencies are managed automatically.

**Acceptance Criteria:**

1. RPM spec file created (packaging/fedora-voice-dictation.spec) following Fedora guidelines
2. Spec includes: Metadata, dependencies, build requirements, installation scripts, post-install scripts
3. Package installs to standard locations: /usr/bin/, /usr/share/applications/, /usr/share/icons/, /usr/share/doc/
4. Desktop entry file created for application launchers
5. Build script created (packaging/build.sh): Cleans, runs rpmbuild, produces RPM
6. Installation script (packaging/install.sh) for local testing
7. RPM post-install checks for CUDA and displays appropriate message
8. RPM uninstall decision on user data (keep or clean)
9. Version number managed in single location
10. RPM tested on clean Fedora 39: Install, launch, verify works, uninstall
11. README updated with RPM installation instructions
12. GitHub release includes RPM as downloadable asset

## Story 4.7: User Documentation

**As a** user,
**I want** comprehensive documentation covering installation, configuration, and troubleshooting,
**so that** I can use the application effectively without developer support.

**Acceptance Criteria:**

1. Documentation files created: installation.md, configuration.md, troubleshooting.md, compatibility.md, faq.md
2. **installation.md:** System requirements, RPM installation, CUDA setup, first-run wizard, verification
3. **configuration.md:** Settings window overview with screenshots, hotkey examples, model selection guidance, VAD tuning tips, text injection guide, history settings
4. **troubleshooting.md:** Common issues by category (CUDA/GPU, audio, text injection, hotkeys, performance) with symptoms, causes, solutions
5. **compatibility.md:** Desktop environment support matrix, per-DE setup instructions, application compatibility database, known limitations
6. **faq.md:** Common questions (cloud data, model selection, performance, accuracy)
7. All documentation clear and concise, assuming technical competence
8. Screenshots included for UI-heavy sections
9. README.md updated with: Project description, quick start, links to detailed docs, contributing guidelines, license
10. Documentation reviewed for accuracy
11. Integration test: Follow installation.md from scratch on clean Fedora VM, verify instructions work

## Story 4.8: Developer Documentation

**As a** contributor or future maintainer,
**I want** architecture documentation and contributing guidelines,
**so that** I can understand the codebase and contribute effectively.

**Acceptance Criteria:**

1. Developer documentation files created: architecture.md, contributing.md, development.md, testing.md
2. **architecture.md:** High-level architecture diagram, component descriptions, threading model, state machine, data flow, technology stack, key design decisions
3. **contributing.md:** Code of conduct, bug reporting, feature requests, pull request process, code style guidelines, commit conventions
4. **development.md:** Prerequisites, clone and setup steps, run in development mode, run tests, code formatting, linting, type checking
5. **testing.md:** Testing philosophy, how to run tests, how to write new tests, coverage requirements, manual testing checklist
6. All documentation uses consistent Markdown formatting
7. Code comments reviewed and enhanced (docstrings for all public functions, complex algorithms explained, TODOs marked)
8. Type hints added throughout codebase
9. Integration test: New contributor follows development.md, sets up environment, runs tests

## Story 4.9: Performance Optimization and Validation

**As a** user,
**I want** the application to meet or exceed performance targets,
**so that** dictation feels responsive and doesn't slow down my workflow.

**Acceptance Criteria:**

1. Performance benchmarking from Story 1.9 re-run with full application
2. End-to-end latency measured: Hotkey press → Text appears
3. Performance targets validated: P95 <500ms (PASS), <1000ms (ACCEPTABLE), ≥1000ms (needs optimization)
4. Performance optimization areas: Audio capture latency, VAD latency, Whisper latency, UI responsiveness, memory leaks
5. CPU usage profiled: Idle <5%, Listening <10%, Processing <30%
6. GPU utilization monitored: VRAM stable, compute spikes during transcription
7. Startup time measured: Target <5 seconds on RTX 4060 with 32GB RAM
8. Profiling data collected using cProfile, hotspots identified and optimized
9. Performance optimization changes documented
10. If targets not met, recommendations documented
11. Final benchmark results included in README or docs/performance.md
12. Integration test: Run 50 dictations, verify P95 latency meets MVP target (<1000ms)

## Story 4.10: Final Integration Testing and Release Preparation

**As a** developer,
**I want** comprehensive integration testing across all features and desktop environments,
**so that** the MVP release is stable and ready for early adopters.

**Acceptance Criteria:**

1. Integration test suite expanded to cover all Epic 1-4 functionality
2. **Full workflow tests:** Hotkey dictation on GNOME/KDE, manual tray activation, CLI mode
3. **Settings persistence tests:** Change all settings, restart, verify persisted; corrupt config, verify defaults restored
4. **Model management tests:** Download, switch, delete models
5. **History tests:** 600 dictations verify pruning, search history, export history
6. **Error handling tests:** Unplug mic, fill disk, disable CUDA
7. **Cross-DE tests:** Run on GNOME, KDE, Hyprland, Sway, verify system tray, hotkeys, text injection
8. **Stress tests:** 100 consecutive dictations, 8 hours running, rapid hotkey presses
9. **Accessibility tests:** Keyboard navigation, Orca screen reader, focus indicators
10. All critical bugs (P0/P1) fixed before release
11. Known issues documented in docs/known-issues.md
12. CHANGELOG.md created documenting all v1.0.0 features
13. VERSION set to "1.0.0"
14. Git tag created: `v1.0.0`
15. GitHub release prepared with release notes, assets (RPM, source tarball)
16. README updated with screenshot and demo GIF (optional but recommended)
17. Final code review: All TODOs resolved or documented
18. Integration test: Install from RPM on clean Fedora 39, complete wizard, perform 10 dictations, verify all works

---
