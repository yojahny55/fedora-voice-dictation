# Introduction

## Overview

Fedora Voice Dictation is a Wayland-native desktop application that solves a critical productivity challenge: enabling fast, privacy-focused speech-to-text conversion for power users without cloud dependencies. The architecture must orchestrate audio capture, Voice Activity Detection, GPU-accelerated Whisper transcription, and Wayland text injection to achieve **<500ms latency** while maintaining UI responsiveness—all within a single-process desktop application.

**The Core Architectural Challenge:**

Achieving sub-500ms end-to-end latency requires careful orchestration of:
- **Audio Pipeline:** sounddevice library capturing 16kHz mono audio with <50ms buffering latency
- **VAD Processing:** silero-vad detecting speech boundaries with <200ms lag and <5% false positive rate
- **GPU Transcription:** Whisper base model with CUDA acceleration processing 5-10s audio clips in 200-500ms
- **Text Injection:** Wayland text-input-unstable-v3 protocol or clipboard fallback with <100ms injection time
- **UI Responsiveness:** Qt event loop remaining responsive throughout, never blocking >16ms (60 FPS)

This architecture document defines how these components integrate while maintaining simplicity, privacy, and performance.

---

## Architectural Principles

All design decisions in this architecture are guided by four core principles:

1. **Privacy-First:** No network calls except initial Whisper model downloads. All audio processing, transcription, and data storage happens locally. No telemetry, no analytics, no cloud dependencies.

2. **Performance-First:** <500ms latency target drives all architectural choices. GPU acceleration is mandatory, not optional. Threading model designed to minimize blocking. Every component has a latency budget.

3. **Single-Process Simplicity:** Avoid distributed system complexity. Single Python process with threaded/async components. No microservices, no separate backend server, no IPC overhead (except D-Bus for system integration).

4. **Wayland-Native:** No X11 dependencies or XWayland compatibility layers. Built specifically for modern Linux desktops (GNOME, KDE, Hyprland, Sway). Embrace Wayland protocols even if unstable—clipboard fallback mitigates risk.

**Critical Design Constraint:** This architecture targets **single-user, local-only operation** on **NVIDIA GPU hardware** with **Fedora 38+ on Wayland**. These constraints enable aggressive simplification.

---

## Architecture Evolution Timeline

This architecture will be validated and refined through prototyping before full implementation:

| Timeframe | Milestone | Key Decisions | Go/No-Go Criteria |
|-----------|-----------|---------------|-------------------|
| **Week 1-2** | Performance Validation Prototype | Python vs whisper.cpp decision | <1s latency achieved = Python GO, >1.5s = whisper.cpp migration |
| **Week 2-3** | Wayland Integration Spike | text-input-unstable-v3 vs clipboard primary method | Protocol works on ≥3/4 DEs = GO, <2/4 = clipboard-first fallback |
| **Week 3** | Architecture Finalization | Lock component design, threading model, interfaces | All prototypes pass = BEGIN Epic 1 implementation |
| **Week 4-20** | Iterative Implementation | Per-epic architecture refinements | Documented in change log below |

**Pending Decisions (Week 1-2 Validation Required):**
- ⚠️ **Python Performance:** If latency >1.5s, architecture migrates to whisper.cpp with Python bindings
- ⚠️ **Threading Model:** Confirm Python asyncio + QThread sufficient, or need multiprocessing
- ⚠️ **Wayland Protocol Reliability:** Validate text-input-unstable-v3 across all target DEs

---

## User Journey → Architecture Mapping

This table maps key user workflows to the architectural components that implement them:

| User Action | Architecture Flow | Components Involved | Latency Budget |
|-------------|-------------------|---------------------|----------------|
| **Press hotkey** | Hotkey listener → State machine → Audio capture start | `HotkeyManager`, `StateMachine`, `AudioCapture` | <50ms |
| **Speak** | Audio buffering → VAD detects speech → Continuous capture | `AudioCapture`, `VADProcessor`, `AudioBuffer` | Real-time |
| **Stop speaking** | VAD detects silence → Audio finalized → Queue for transcription | `VADProcessor`, `AudioBuffer`, `TranscriptionQueue` | <200ms |
| **Transcription** | Whisper processes audio → Streaming word output | `WhisperEngine` (CUDA), `TranscriptionWorker` | <500ms (base model, 5s audio) |
| **Text appears** | Focus target window → Inject via Wayland or clipboard → UI feedback | `WindowFocus`, `TextInjection`, `NotificationManager` | <100ms |
| **Review history** | Open history viewer → Load from JSON → Display table | `HistoryManager`, `HistoryViewer` UI | <200ms |
| **Change settings** | Open settings UI → Update config → Apply changes | `SettingsWindow`, `ConfigManager` | Immediate |

**Total End-to-End Latency Budget:** 850ms (target: <500ms requires optimization in Week 1-2 prototypes)

---

## How to Read This Document

This architecture document serves different audiences:

**For Developers (implementing Epic 1-4 stories):**
- Focus on: **Components**, **Threading Model** (Backend Architecture), **Data Flow** (Core Workflows)
- Key sections: Tech Stack, Database Schema, Project Structure, Coding Standards
- Skip: High-level diagrams, deployment details (until Epic 4)

**For Contributors (understanding codebase to submit PRs):**
- Focus on: **Architectural Patterns**, **Component Diagrams**, **Coding Standards**, **Testing Strategy**
- Key sections: Components, Error Handling, Development Workflow
- Reference: Technical Summary for quick orientation

**For Packagers/Distributors (creating RPM, Flatpak):**
- Focus on: **Deployment Architecture**, **Environment Configuration**, **Prerequisites**
- Key sections: Platform and Infrastructure, Unified Project Structure, Development Workflow
- Note: Epic 4 will finalize packaging specifications

**For Architecture Reviewers (validating design decisions):**
- Read full document linearly
- Pay special attention to: Architectural Principles, Architectural Patterns, Core Workflows, Performance Optimization
- Review decisions against PRD requirements (docs/prd.md)

---

## Testing Philosophy

Architecture designed for testability from the start:

**Unit Testing (60%+ coverage):**
- All components have clear interfaces for mocking
- Audio/Whisper/Wayland dependencies mocked in unit tests
- pytest with pytest-qt for Qt component testing
- CI/CD runs on CPU-only (uses mocked GPU for basic validation)

**Integration Testing (Manual, GPU-required):**
- End-to-end workflows on developer system (RTX 4060 + Wayland)
- Performance benchmarking with fixture audio files
- Cross-DE testing (GNOME, KDE, Hyprland, Sway)

**Performance Testing (Automated Benchmarking):**
- Latency measurement at each pipeline stage
- Statistical analysis (mean, median, p95, p99)
- Regression detection across commits

**Testability Requirements:**
- Components communicate via defined interfaces (not tight coupling)
- State machine enables deterministic testing of transitions
- Configuration injectable (not hardcoded) for test scenarios

---

## Starter Template or Existing Project

**Status:** Greenfield Desktop Application

Fedora Voice Dictation is built from scratch to leverage modern technologies unavailable in legacy Linux voice dictation tools:
- **Modern GPU Acceleration:** CUDA support for Whisper (2020s hardware)
- **Wayland Protocols:** text-input-unstable-v3, native desktop integration (no X11)
- **Contemporary ML Models:** OpenAI Whisper (2022), silero-vad (2021)

**No Starter Templates Used:**
- Standard Python project structure with PyQt5
- No desktop application frameworks (Qt Creator templates, Electron, Tauri)
- No pre-built voice dictation libraries (all integration custom)

**Architectural Constraints from Technology Choices:**
- **PyQt5:** Proven cross-DE system tray support (GNOME, KDE, Hyprland, Sway)
- **openai-whisper:** CUDA acceleration mandatory, model loading strategy critical
- **Wayland Protocols:** text-input-unstable-v3 primary, clipboard fallback required
- **Single-Process:** Simplicity for MVP, may refactor to multi-process in Phase 2 if stability issues emerge

**Decision Point (Week 1-2):** If Python performance insufficient, architecture may migrate to whisper.cpp (C++) with Python bindings while keeping PyQt5 UI.

---

## Documentation Note: Template Adaptation

This architecture document uses the BMAD full-stack template adapted for desktop application context. Where the template references "frontend" and "backend" as separate services, we treat them as **logical layers within a single application process**:

- **"Frontend" layer:** Qt-based UI components (system tray, settings windows, visual indicators)
- **"Backend" layer:** Core processing logic (audio capture, VAD, Whisper transcription, Wayland integration)
- **No separate API layer:** Components communicate via Qt signals/slots and threaded message passing (not HTTP/REST)
- **No cloud deployment:** Application runs entirely on user's local machine with GPU acceleration

This adaptation maintains the template's comprehensive coverage of cross-cutting concerns (performance, security, testing, deployment) while fitting desktop application patterns. Desktop-specific sections added: Threading Model, Desktop Integration, IPC Mechanisms.

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-22 | v1.0 | Initial architecture document creation | Winston (Architect) |

---
