# Epic 1: Foundation & Core Dictation Pipeline

**Epic Goal:** Establish project infrastructure and implement the core voice-to-text transcription pipeline (audio capture, VAD, Whisper with GPU acceleration) with a functional CLI interface. This epic proves the technical foundation works, validates that Python architecture can achieve performance targets (<1 second latency on RTX 4060), and delivers an immediately usable CLI tool for developer testing and daily workflow integration.

## Story 1.1: Project Setup and Repository Initialization

**As a** developer,
**I want** the project repository initialized with proper structure, dependencies, and development tooling,
**so that** I can begin implementing features with a solid foundation and establish good development practices from the start.

**Acceptance Criteria:**

1. GitHub repository created with name `fedora-voice-dictation` and initial README describing project purpose
2. Repository structure follows Technical Assumptions monorepo layout (src/, tests/, docs/, packaging/, examples/)
3. Python virtual environment setup documented in README with Python 3.10+ requirement
4. Core dependencies installed and pinned in requirements.txt
5. Git .gitignore configured for Python projects
6. Basic logging utility implemented in src/utils/logger.py with configurable log levels
7. Project can be installed in development mode: `pip install -e .` works without errors
8. Simple health check script runs successfully: `python -m src --version` prints version number
9. GitHub Actions workflow configured to run unit tests on every commit
10. LICENSE file added (MIT or GPL v3, as determined by user)

## Story 1.2: Audio Device Enumeration and Selection

**As a** user,
**I want** the application to detect available audio input devices and allow me to select my microphone,
**so that** I can use my preferred microphone for dictation.

**Acceptance Criteria:**

1. Audio device manager module implemented (src/audio/device_manager.py) using sounddevice library
2. Application can enumerate all available audio input devices on the system
3. Each device listing includes: device ID, name, sample rates supported, channel count
4. Default input device is automatically detected and selected if user hasn't configured a preference
5. Configuration file stores selected device ID
6. If configured device is not available, application falls back to default device and logs warning
7. CLI test command: `fedora-voice-dictation --list-audio-devices` prints all devices
8. Validation: Application warns if selected device doesn't support 16kHz sample rate
9. Error handling: Graceful error message if no audio input devices found
10. Unit tests verify device enumeration logic with mocked sounddevice responses

## Story 1.3: Audio Capture Pipeline

**As a** user,
**I want** the application to continuously capture audio from my microphone in the background,
**so that** it's ready to process my speech when I activate dictation.

**Acceptance Criteria:**

1. Audio capture module implemented (src/audio/capture.py) using sounddevice InputStream
2. Audio captured at 16kHz sample rate, mono channel
3. Audio capture runs in separate thread
4. Audio data stored in circular buffer (5-second capacity)
5. Buffer implements thread-safe read/write operations
6. Audio capture can be started and stopped programmatically
7. Audio levels monitored in real-time (RMS calculation)
8. Clear exceptions raised when audio capture errors occur
9. CLI test command: `fedora-voice-dictation --test-audio` captures 5 seconds and displays audio level
10. Memory leak validation: Capture runs for 10 minutes without memory growth >10MB
11. Unit tests verify buffer behavior with simulated audio data

## Story 1.4: Voice Activity Detection Integration

**As a** user,
**I want** the application to automatically detect when I start and stop speaking,
**so that** I don't need to manually indicate when my speech is complete.

**Acceptance Criteria:**

1. VAD module implemented (src/audio/vad.py) integrating silero-vad library
2. VAD processes audio chunks in real-time
3. VAD triggers "speech_started" event when detecting voice activity
4. VAD triggers "speech_ended" event when detecting silence for configurable duration (default 500ms)
5. VAD sensitivity configurable via config parameter (0.1-1.0 range, default 0.5)
6. Audio buffering starts when "speech_started" fires, stops when "speech_ended" fires
7. Buffered audio packaged and queued for transcription
8. VAD false positive mitigation: Ignores audio bursts shorter than 300ms
9. Configuration file stores VAD sensitivity and end-of-speech timeout settings
10. CLI test command: `fedora-voice-dictation --test-vad` shows real-time VAD state
11. Performance validation: VAD processing adds <50ms latency per audio chunk
12. Unit tests verify VAD event triggering with fixture audio files

## Story 1.5: Whisper Model Download and Loading

**As a** user,
**I want** the application to automatically download the Whisper model on first run and load it into GPU memory,
**so that** I can start using dictation without manual model management.

**Acceptance Criteria:**

1. Model management module implemented (src/transcription/model_downloader.py)
2. On first run, base model automatically downloaded if not present
3. Models stored in ~/.local/share/fedora-voice-dictation/models/
4. Download progress displayed in terminal
5. Downloaded model integrity verified via checksum
6. Clear error message if download fails, with retry option
7. Whisper model loading module implemented (src/transcription/whisper_engine.py)
8. Application attempts CUDA acceleration, falls back to CPU with warning
9. Model remains loaded in memory for instant availability
10. VRAM usage logged on model load
11. Configuration file stores selected model type
12. CLI command: `fedora-voice-dictation --download-model medium` downloads specific model
13. CLI command: `fedora-voice-dictation --model-info` displays loaded model info
14. Error handling: If model fails to load, application exits with diagnostic information

## Story 1.6: Audio Transcription with Whisper

**As a** user,
**I want** the application to transcribe my speech using Whisper with GPU acceleration,
**so that** I get fast and accurate text output from my voice input.

**Acceptance Criteria:**

1. Transcription engine implemented (src/transcription/whisper_engine.py)
2. Transcription accepts audio buffer and returns transcribed text
3. Whisper processes audio using GPU acceleration when available
4. Optimal parameters configured (language: "en", fp16: True, beam_size: 5)
5. Word-level timestamps enabled for future streaming support
6. Transcription latency measured and logged
7. Performance validation on RTX 4060: 5s audio <500ms, 10s audio <800ms, 30s audio <2000ms
8. Warning logged if latency exceeds targets
9. Error handling: Graceful failure for poor audio quality, CUDA OOM, model unloaded
10. Empty/no-speech audio returns empty string
11. Integration test: Pre-recorded test audio transcribed with >90% accuracy
12. Unit tests verify transcription API with mocked Whisper responses

## Story 1.7: CLI Interface for Dictation

**As a** developer or power user,
**I want** a command-line interface to activate dictation and see transcribed text output,
**so that** I can use voice dictation in my terminal-based workflow or test the system.

**Acceptance Criteria:**

1. CLI entry point implemented (src/__main__.py) with argparse
2. Command: `fedora-voice-dictation --cli` starts CLI dictation mode
3. CLI workflow: Displays prompts, listens continuously, outputs transcribed text
4. Real-time feedback: Audio level indicator while listening
5. Latency measurement displayed
6. Exit gracefully on Ctrl+C
7. CLI supports options: `--model`, `--vad-sensitivity`, `--device`
8. Error handling: Prints diagnostic info if initialization fails
9. Help text: `fedora-voice-dictation --help` shows all commands
10. Integration test: Run CLI mode, speak test phrase, verify transcription appears within 2 seconds

## Story 1.8: Configuration Management and Persistence

**As a** user,
**I want** my settings to persist across application restarts,
**so that** I don't need to reconfigure the application every time I use it.

**Acceptance Criteria:**

1. Configuration manager implemented (src/core/config.py)
2. Configuration file created at ~/.config/fedora-voice-dictation/config.json on first run
3. Configuration directory created automatically if needed
4. Default configuration includes: model, audio_device_id, vad_sensitivity, vad_end_timeout_ms, log_level
5. Configuration loaded on application startup
6. Settings updated via config.set() and saved immediately
7. Configuration file validated on load
8. If corrupted, backup created and defaults restored
9. Configuration file is human-readable JSON with comments
10. Unit tests verify config load/save, validation, default restoration
11. CLI command: `fedora-voice-dictation --show-config` prints current configuration

## Story 1.9: Performance Benchmarking and Validation

**As a** developer,
**I want** to measure end-to-end dictation latency and validate performance targets,
**so that** I can confirm the Python architecture meets requirements.

**Acceptance Criteria:**

1. Benchmarking script implemented (tests/integration/benchmark_latency.py)
2. Script performs 20 test dictations using pre-recorded audio (5s, 10s, 30s)
3. Latency measured at each pipeline stage
4. Results logged with timestamps, audio lengths, latencies
5. Statistical summary calculated: mean, median, p95, p99
6. Validation against NFR1 target: PASS (<500ms), ACCEPTABLE (<1000ms), FAIL (≥1000ms)
7. Benchmark results displayed with color coding
8. Recommendations displayed if benchmarks fail
9. VRAM usage measured and logged
10. CPU usage measured (should be <50% if GPU used)
11. Benchmark can be re-run: `fedora-voice-dictation --benchmark`
12. Results saved to ~/.local/share/fedora-voice-dictation/benchmark-results.json

## Story 1.10: Error Handling and Logging Framework

**As a** developer and user,
**I want** comprehensive error handling and logging throughout the application,
**so that** I can diagnose issues quickly and the application fails gracefully.

**Acceptance Criteria:**

1. Logging framework configured in src/utils/logger.py
2. Log file created at ~/.local/share/fedora-voice-dictation/logs/app.log
3. Log directory created automatically
4. Log rotation: Daily rotation, keep last 7 days, max 10MB per file
5. Log levels configurable via config or CLI flag
6. All modules use logger consistently (DEBUG, INFO, WARNING, ERROR)
7. Log format includes: timestamp, level, module name, message
8. Exception handling framework with try/except in all public functions
9. User-facing error messages are clear and actionable
10. Privacy: Transcribed text NOT logged by default
11. CLI flag: `fedora-voice-dictation --debug` enables DEBUG level
12. Integration test: Trigger known errors, verify appropriate error logged

---
