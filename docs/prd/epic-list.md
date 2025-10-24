# Epic List

The MVP is structured into **4 sequential epics**, each delivering end-to-end testable functionality that builds upon the previous epic.

## Epic 1: Foundation & Core Dictation Pipeline

**Goal:** Establish project infrastructure and implement the core voice-to-text transcription pipeline (audio capture, VAD, Whisper with GPU acceleration) with a functional CLI interface, proving the technical foundation works and validating performance targets.

**Duration:** 4 weeks (Week 1-4)

**Value Delivered:**
- Developers can dictate via command line and see transcribed text output to terminal
- Validates CUDA/Whisper performance meets <1 second latency target on RTX 4060
- Proves Python architecture is sufficient for performance requirements
- Provides foundation for all subsequent epics

## Epic 2: Desktop Integration & Text Injection

**Goal:** Integrate the dictation engine with the Wayland desktop environment, enabling hotkey-activated dictation that automatically inserts transcribed text into focused applications via Wayland protocols or clipboard fallback.

**Duration:** 4 weeks (Week 5-8)

**Value Delivered:**
- Users can press global hotkey, speak, and see text appear in target applications
- Text injection works in terminals, text editors, browsers, and Claude Code
- Basic system tray icon shows application status
- Deliverable end-to-end user workflow (no CLI required)

## Epic 3: Configuration & Model Management

**Goal:** Provide comprehensive user configuration capabilities through a settings UI, model download/management system, and persistent storage, allowing users to customize the application for their hardware, preferences, and workflow needs.

**Duration:** 3 weeks (Week 9-11)

**Value Delivered:**
- Users can download and switch between Whisper models
- All application settings configurable via GUI
- Settings persist across restarts
- Session history tracks all dictations for text recovery
- First-run setup wizard guides new users

## Epic 4: Production Readiness & Polish

**Goal:** Transform the functional MVP into a production-ready application with diagnostic tools, comprehensive error handling, cross-desktop environment compatibility testing, packaging for distribution, and complete documentation.

**Duration:** 3 weeks (Week 12-14)

**Value Delivered:**
- Users can diagnose and troubleshoot issues independently
- Application handles all common error scenarios gracefully
- Works reliably across GNOME, KDE, Hyprland, and Sway
- Installable via RPM package with clear documentation
- Ready for public release and early adopter community

**Total Timeline:** ~20 weeks (~5 months) including buffer for iteration and testing

---
