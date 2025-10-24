# Requirements

## Functional Requirements

### Core Audio & Transcription

- **FR1:** The system shall capture real-time audio from the user's microphone using the sounddevice library with Wayland compatibility.
- **FR2:** The system shall implement Voice Activity Detection (VAD) to automatically detect when the user begins and ends speaking.
- **FR2.1:** The system shall provide a VAD sensitivity configuration slider in settings allowing users to tune detection threshold for their environment.
- **FR2.2:** The system shall provide a distinct VAD status indicator showing when speech is actively detected (separate from general audio level display).
- **FR2.3:** The system shall provide a manual stop button as backup when VAD auto-detection is unreliable or undesired.
- **FR3:** The system shall integrate OpenAI Whisper speech recognition with CUDA GPU acceleration for local transcription processing.
- **FR3.1:** The system shall provide CPU-only fallback mode when CUDA is unavailable or fails to initialize, with clear performance warnings.
- **FR4:** The system shall support multiple Whisper model sizes (tiny, base, small, medium, large) selectable by the user through the settings interface.
- **FR4.1:** The system shall download Whisper models automatically on first use with progress indication UI showing download status and speed.
- **FR4.2:** The system shall store Whisper models in ~/.local/share/fedora-voice-dictation/models/ with automatic directory creation.
- **FR4.3:** The system shall verify downloaded model integrity using checksums before first use.
- **FR4.4:** The system shall provide model management interface allowing users to delete unused models and check for updates.
- **FR5:** The system shall provide streaming word-by-word transcription output rather than waiting for complete sentence processing.

### Text Injection & Integration

- **FR6:** The system shall inject transcribed text into the currently focused application using the text-input-unstable-v3 Wayland protocol as the primary method.
- **FR7:** The system shall provide clipboard-based text injection as a fallback mechanism when Wayland protocol injection fails.
- **FR7.1:** The system shall allow users to manually select text injection method (Wayland protocol, clipboard, or auto-detect) via settings.
- **FR7.2:** The system shall provide a text injection diagnostic tool that tests both methods against the currently focused application and reports results.
- **FR7.3:** The system shall maintain a compatibility database documenting which applications work with which injection methods, accessible via help menu.

### User Interface & Controls

- **FR8:** The system shall register and respond to a user-configurable global keyboard hotkey to activate voice dictation mode.
- **FR8.1:** The system shall detect and warn users when their chosen hotkey conflicts with known system or desktop environment keybindings.
- **FR8.2:** The system shall provide alternative activation methods (system tray click, CLI command) for compositors that don't support global hotkeys.
- **FR9:** The system shall display a persistent system tray icon showing current status (listening, idle, processing, error).
- **FR10:** The system shall provide a system tray menu with controls for Start/Stop, Settings access, and application Quit.
- **FR11:** The system shall provide a settings window allowing users to configure Whisper model selection, global hotkey, audio input device, VAD sensitivity, and text injection method.
- **FR12:** The system shall persist all settings to a JSON configuration file located at ~/.config/fedora-voice-dictation/config.json.
- **FR12.1:** The system shall validate configuration file on load and restore defaults with user notification if file is corrupted or invalid.
- **FR12.2:** The system shall create backup of configuration file before writing changes to enable recovery from write failures.

### Session History & Data Management

- **FR13:** The system shall track and store recent dictation sessions including timestamp, transcribed text, duration, and target application in a history file.
- **FR13.1:** The system shall limit history retention to the most recent 500 sessions or 90 days (whichever is larger), automatically pruning older entries.
- **FR13.2:** The system shall provide privacy controls allowing users to disable history, clear all history, or exclude specific applications from tracking.
- **FR14:** The system shall make session history accessible through the system tray menu for user review and text recovery.
- **FR14.1:** The system shall provide search and filter capability for session history by date, text content, or target application.
- **FR14.2:** The system shall allow users to export session history to text or JSON format.

### Visual Feedback & Monitoring

- **FR15:** The system shall display visual feedback (waveform or audio level indicator) showing audio input and current listening/processing state.
- **FR15.1:** The system shall allow users to disable visual feedback via settings to reduce CPU/GPU overhead.
- **FR16:** The system shall display toast notifications when transitioning between states (listening started, processing, text inserted, errors occurred).
- **FR16.1:** The system shall provide detailed error messages when text injection fails, including suggested troubleshooting steps and link to compatibility database.
- **FR16.2:** The system shall display persistent error notification when CUDA initialization fails, with guidance on driver installation and CPU fallback option.

### Device & Resource Management

- **FR17:** The system shall allow users to select from available audio input devices through the settings interface.
- **FR17.1:** The system shall detect when the selected audio device is disconnected and prompt user to select a new device.
- **FR18:** The system shall load the selected Whisper model into GPU memory on application startup and keep it loaded for instant availability.
- **FR18.1:** The system shall provide "Unload Model" option allowing users to reclaim VRAM when needed for other GPU-intensive tasks.
- **FR18.2:** The system shall support model switching without application restart, automatically unloading the current model and loading the newly selected one.
- **FR18.3:** The system shall monitor GPU VRAM usage and warn users when approaching memory limits (>90% VRAM utilization).

### Diagnostics & Setup

- **FR19:** The system shall provide a GPU/CUDA diagnostic tool that validates CUDA installation, driver version, and available VRAM, reporting detailed results.
- **FR20:** The system shall provide an audio diagnostic tool that tests microphone input, displays audio levels, and validates sounddevice library compatibility.

## Non-Functional Requirements

### Performance

- **NFR1:** The system shall achieve transcription latency under 500ms from speech end to text appearance in target applications (MVP acceptance: <1 second).
- **NFR1.1:** The system shall measure and log actual latency for each dictation session to enable performance monitoring and optimization.
- **NFR2:** The system shall operate 100% offline with no cloud connectivity required after initial Whisper model download.
- **NFR3:** The system shall not transmit any audio data, transcriptions, or usage telemetry to external servers.
- **NFR4:** The system shall achieve Word Error Rate (WER) below 10% for general conversational speech and below 15% for technical content (code, commands, LLM prompts) using base model.
- **NFR7:** The system shall utilize GPU VRAM efficiently, keeping usage under 4GB for the base Whisper model.
- **NFR8:** The system shall launch and load the Whisper model in under 5 seconds on target hardware (RTX 4060, 32GB RAM).

### Reliability & Stability

- **NFR9:** The system shall complete 99%+ of dictation sessions without application crashes or freezes.
- **NFR10:** The system shall run continuously for a full workday (8+ hours) and handle 50+ consecutive dictation sessions without memory leaks or performance degradation.
- **NFR10.1:** The system shall gracefully handle system suspend/resume, reacquiring audio device and GPU context as needed.
- **NFR15:** The system shall achieve VAD accuracy with <5% false positive rate in typical office environment (background conversation, keyboard typing, ambient noise).
- **NFR16:** The system shall provide meaningful error messages for all failure scenarios, avoiding generic "Error occurred" messages.

### Compatibility

- **NFR5:** The system shall successfully inject text into 80% of tested Wayland applications across GNOME, KDE Plasma, Hyprland, and Sway desktop environments (target: 95% post-MVP).
- **NFR5.1:** The system shall maintain a living compatibility matrix documenting text injection success across major applications (browsers, terminals, editors, IDEs).
- **NFR11:** The system shall support Fedora Linux 38+ and be compatible with Fedora-based distributions (Nobara, Ultramarine).
- **NFR12:** The system shall operate exclusively on Wayland compositors without any X11 or XWayland dependencies.

### Hardware & System Requirements

- **NFR6:** The system shall require NVIDIA GPU with CUDA support (RTX 3000 series or newer recommended, GTX 1660+ minimum) for GPU-accelerated mode.
- **NFR6.1:** The system shall function in CPU-only mode on systems without NVIDIA GPU, with degraded performance (3-5x slower).
- **NFR13:** The system shall require minimum hardware specifications of 16GB system RAM, 4GB+ VRAM (GPU mode), and 4+ core CPU.

### Usability & Setup

- **NFR14:** The system shall provide setup and first successful dictation achievable within 30 minutes following documentation for users with CUDA pre-installed.
- **NFR14.1:** The system shall provide clear installation documentation covering CUDA setup, RPM installation, and first-run configuration.

---
