# Technical Assumptions

## Repository Structure: Monorepo

**Decision:** Single repository containing all application code, packaging specifications, documentation, and tests.

**Structure:**
```
fedora-voice-dictation/
├── src/                          # Application source code
│   ├── __init__.py
│   ├── __main__.py              # CLI entry point
│   ├── audio/                   # Audio capture, VAD processing
│   ├── transcription/           # Whisper integration, model management
│   ├── wayland/                 # Wayland protocol integration, text injection
│   ├── ui/                      # Qt UI components
│   ├── core/                    # Core application logic
│   └── utils/                   # Utilities, logging, diagnostics
├── packaging/                   # RPM spec files, build scripts
├── docs/                        # User and developer documentation
├── tests/                       # Unit and integration tests
├── examples/                    # Example configurations
├── requirements.txt
├── setup.py
├── README.md
└── LICENSE
```

**Rationale:**
- Single repository simplicity aligns with single-user, local-only design
- Clear module separation enables independent testing
- Packaging co-located for easier version management

## Service Architecture: Single-Process with Async/Threaded Architecture

**High-Level Architecture:**

```
┌─────────────────────────────────────────────────────┐
│                  Qt Event Loop (Main Thread)         │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐│
│  │ System Tray  │  │   Settings   │  │  History   ││
│  │     UI       │  │      UI      │  │  Viewer    ││
│  └──────────────┘  └──────────────┘  └────────────┘│
└────────────┬────────────────────────────────────────┘
             │ Qt Signals/Slots
             ▼
┌─────────────────────────────────────────────────────┐
│           Core State Machine (Main Thread)           │
│  Manages: idle → listening → processing → complete  │
└────────────┬────────────────────────────────────────┘
             │ Commands
             ├──────────┬──────────┬──────────┬────────
             ▼          ▼          ▼          ▼
     ┌────────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐
     │   Audio    │ │ Whisper  │ │ Wayland │ │  Config  │
     │   Thread   │ │  Thread  │ │  Thread │ │  Manager │
     │            │ │  (async) │ │         │ │  (Main)  │
     │ sounddevice│ │   CUDA   │ │text-inp │ │   JSON   │
     │    VAD     │ │ streaming│ │clipboard│ │ History  │
     └────────────┘ └──────────┘ └─────────┘ └──────────┘
          │              │            │
          │              │            │
          ▼              ▼            ▼
     [Microphone]   [GPU/VRAM]  [Target App]
```

**Architecture Components:**

1. **Main Thread (Qt Event Loop):** UI rendering, state machine, coordination
2. **Audio Thread (Continuous Background):** sounddevice capture, VAD, buffering
3. **Transcription Worker (On-Demand Async):** Whisper processing, streaming output
4. **Wayland/Text Injection Thread:** Text injection, window focus tracking
5. **Configuration & History Manager:** Settings persistence, history tracking

**Concurrency Model:**
- Qt Signals/Slots for thread-safe communication
- Python asyncio for Whisper transcription
- Threading for audio capture
- Minimal locking (message-passing architecture)

**Rationale:**
- Single-process simplicity (no distributed systems complexity)
- Async for GPU-bound work prevents UI blocking
- Qt signals/slots provide type-safe, thread-safe communication

## Testing Requirements: Unit + Integration + Manual Cross-DE Testing

**Testing Strategy:**

**1. Unit Testing (Automated, 60% code coverage minimum):**
- Framework: pytest with pytest-qt
- Scope: Core logic, audio processing, transcription, text injection, utilities
- Mocking: CUDA/Whisper, audio input, Wayland protocols, Qt UI

**2. Integration Testing (Semi-Automated):**
- Scope: End-to-end workflows, model management, settings persistence, stability
- Requires: GPU, microphone, Wayland session, test applications
- Executed manually on developer's system

**3. Manual Cross-Desktop Environment Testing:**
- Test Matrix: GNOME, KDE, Hyprland, Sway
- Scenarios: Hotkey activation, system tray, text injection, notifications
- Developer tests GNOME+KDE, community tests Hyprland+Sway

**4. Accessibility Testing (Manual, Basic):**
- Keyboard navigation, screen reader (Orca), high contrast, focus indicators

**5. Performance Testing (Manual Benchmarking):**
- Metrics: Transcription latency, model load time, VRAM usage, memory leaks, CPU usage

**6. No End-to-End Automated UI Testing (Out of Scope for MVP)**

## Additional Technical Assumptions and Requests

**Language & Runtime:**
- Python 3.10+ (CPython only)
- System Python or venv (venv recommended for development)

**Core Dependencies:**
- **openai-whisper** with PyTorch CUDA support (torch>=2.0.0+cu118)
- **sounddevice** (PortAudio wrapper, Wayland-compatible)
- **silero-vad** (neural network-based VAD)
- **PyQt5** (5.15.x) - Python bindings for Qt5
- **pywayland** - Wayland protocol bindings
- **pyclip/pyperclip** - Clipboard access
- **dbus-python** - Desktop notifications, system tray

**Version Pinning Strategy:**
- Pin major.minor for critical dependencies
- Allow patch version flexibility

**GPU & CUDA Assumptions:**
- NVIDIA GPU only for MVP (AMD ROCm deferred to Phase 2)
- CUDA compute capability 6.1+ (GTX 1660+ / RTX 3000+)
- Driver version 515+ for CUDA 11.8 support
- Validation: Early prototype tests performance

**Wayland Protocol Assumptions:**
- text-input-unstable-v3 availability varies by compositor
- Clipboard fallback mitigates protocol limitations
- Validation: Early testing on all target DEs

**Performance Assumptions (To Be Validated):**
- Python async/threading sufficient for <500ms target
- Whisper base model achieves 200-500ms on RTX 4060
- GPU acceleration provides 3x+ speedup over CPU

**Development Environment:**
- Primary: Fedora 39+ with GNOME on Wayland
- Hardware: RTX 4060, 32GB RAM
- IDE: VSCode or PyCharm Community

**Deployment & Installation:**
- RPM package via `dnf install`
- Prerequisites check for CUDA
- Models in user's home directory
- User-specific configuration

**Security Considerations:**
- Microphone access via standard permissions
- No network access (except model download)
- Local data only
- Configuration file permissions warnings

**Logging & Debugging:**
- Log location: ~/.local/share/fedora-voice-dictation/logs/app.log
- Log levels: INFO (default), DEBUG (via flag)
- Log rotation: Daily, keep 7 days
- Privacy: Transcribed text NOT logged by default

**Licensing:**
- Application: MIT or GPL v3 (TBD)
- Dependency licenses: Verify compatibility

---
