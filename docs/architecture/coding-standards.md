# Coding Standards

## Overview

Fedora Voice Dictation enforces strict coding standards to maintain code quality, readability, and long-term maintainability. These standards apply to all Python code in `src/`, test code in `tests/`, and build scripts. **All code must pass automated linting (ruff, black, mypy) before being committed.**

**Enforcement:**
- **Pre-commit Hooks:** Run `black`, `ruff`, `mypy` automatically on staged files
- **CI Pipeline:** Fail builds if linting checks fail (see `.github/workflows/ci.yml`)
- **Code Review:** PRs must pass linting + 1 reviewer approval before merge

---

## Python Style Guide

### Base Standard: PEP 8 + Black Formatting

- **PEP 8 Compliance:** Follow [PEP 8](https://pep.python.org/pep-0008/) for all Python code
- **Black Formatting:** Use `black` (v23.9.1+) as the authoritative formatter with default settings (88 char line length)
- **No Manual Formatting:** Never manually format code—let `black` handle it

**Example `.pre-commit-config.yaml`:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.0.292
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--strict, --ignore-missing-imports]
```

### Line Length and Wrapping

- **Max Line Length:** 88 characters (black default)
- **Long Signal Connections:** Break after `=` or `.connect(`
  ```python
  # GOOD
  self.audio_capture.speechDetected.connect(
      self.state_machine.on_speech_detected
  )

  # BAD (exceeds 88 chars)
  self.audio_capture.speechDetected.connect(self.state_machine.on_speech_detected)
  ```

### Imports

**Order (enforced by `ruff --select I`):**
1. Standard library imports
2. Third-party imports (PyQt5, numpy, torch, etc.)
3. Local application imports

**Format:**
```python
# 1. Standard library
import logging
import time
from pathlib import Path
from typing import Optional

# 2. Third-party
import numpy as np
import torch
from PyQt5.QtCore import QObject, pyqtSignal

# 3. Local
from src.audio.vad_processor import VADProcessor
from src.core.config_manager import ConfigManager
```

**Rules:**
- ✅ Absolute imports only (`from src.audio.capture import AudioCapture`)
- ❌ No relative imports (`from ..audio.capture import AudioCapture`)
- ✅ One import per line for `from` imports
- ✅ Group by import type, separated by blank lines

---

## Type Hints Policy

**Requirement:** All public functions/methods must have complete type hints (Python 3.10+ syntax).

### Function Signatures

```python
# GOOD: Complete type hints
def process_audio(
    self, audio_data: np.ndarray, sample_rate: int
) -> tuple[bool, float]:
    """Process audio chunk and return (is_speech, confidence)."""
    ...

# BAD: Missing return type
def process_audio(self, audio_data: np.ndarray, sample_rate: int):
    ...

# BAD: Missing parameter types
def process_audio(self, audio_data, sample_rate) -> tuple[bool, float]:
    ...
```

### Class Attributes

Use `typing` annotations for class-level attributes:
```python
from typing import Optional
from PyQt5.QtCore import QObject

class AudioCapture(QObject):
    # Type hints for class attributes
    _stream: Optional[sd.InputStream] = None
    _is_capturing: bool = False
    _buffer: list[bytes] = []

    def __init__(self, config: ConfigManager):
        super().__init__()
        self._config: ConfigManager = config  # Instance attribute
```

### Qt Signal Types

**Always annotate signal types:**
```python
from PyQt5.QtCore import pyqtSignal

class WhisperEngine(QObject):
    # GOOD: Signal type annotated
    transcriptionComplete: pyqtSignal = pyqtSignal(str, int)  # (text, latency_ms)
    errorOccurred: pyqtSignal = pyqtSignal(str)  # (error_message)

    # BAD: No type annotation
    transcriptionComplete = pyqtSignal(str, int)
```

### Union and Optional

Use Python 3.10+ syntax:
```python
# GOOD (Python 3.10+)
def get_model(self, name: str) -> torch.nn.Module | None:
    ...

# BAD (old syntax)
from typing import Union, Optional
def get_model(self, name: str) -> Optional[torch.nn.Module]:
    ...
```

### TypedDict for Complex Dicts

Use `TypedDict` for configuration dicts:
```python
from typing import TypedDict

class AudioConfig(TypedDict):
    device_index: int
    sample_rate: int
    channels: int
    buffer_duration_ms: int

def configure_audio(self, config: AudioConfig) -> None:
    sample_rate = config["sample_rate"]  # Type-safe access
```

### NumPy Array Type Hints

**CRITICAL:** Use `numpy.typing` to specify array dtype and document shape in docstrings.

```python
import numpy as np
import numpy.typing as npt

# GOOD: Specify dtype for type safety
def process_audio(self, audio: npt.NDArray[np.float32]) -> str:
    """Process audio chunk.

    Args:
        audio: Audio samples, shape (n_samples,), mono 16kHz float32.
    """
    assert audio.ndim == 1, "Audio must be mono (1D array)"
    assert audio.dtype == np.float32, "Audio must be float32"
    ...

# BAD: Generic np.ndarray (accepts any shape/dtype)
def process_audio(self, audio: np.ndarray) -> str:
    ...  # Runtime error if user passes stereo or int16!
```

**Shape Validation:**
```python
def validate_audio_shape(audio: npt.NDArray[np.float32]) -> None:
    """Validate audio array shape and dtype.

    Raises:
        ValueError: If audio is not mono float32.
    """
    if audio.ndim != 1:
        raise ValueError(f"Audio must be mono (1D), got shape {audio.shape}")
    if audio.dtype != np.float32:
        raise ValueError(f"Audio must be float32, got {audio.dtype}")
    if len(audio) == 0:
        raise ValueError("Audio array is empty")
```

### Mypy Configuration

**`pyproject.toml`:**
```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
disallow_subclassing_any = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true

# Allow untyped imports for third-party libs without stubs
[[tool.mypy.overrides]]
module = [
    "sounddevice",
    "silero_vad",
    "openai_whisper",
]
ignore_missing_imports = true
```

---

## Naming Conventions

### Files and Modules

- **Snake_case:** All Python files use `snake_case.py`
  - `audio_capture.py`, `whisper_engine.py`, `text_injection.py`
- **Test Files:** Prefix with `test_`, match source file name
  - `test_audio_capture.py`, `test_whisper_engine.py`

### Classes

- **PascalCase:** All class names
  ```python
  class AudioCapture(QObject): ...
  class WhisperEngine(QObject): ...
  class StateMachine(QStateMachine): ...
  ```

- **Qt Classes:** Inherit from Qt base classes, suffix with widget type if UI component
  ```python
  class SettingsWindow(QWidget): ...  # UI widget
  class AudioIndicator(QLabel): ...   # UI label
  class VADProcessor(QObject): ...    # Non-UI Qt object
  ```

### Functions and Methods

- **Snake_case:** All functions/methods
  ```python
  def start_capture(self): ...
  def process_audio_chunk(self, data: bytes): ...
  def _validate_config(self): ...  # Private method
  ```

- **Private Methods:** Prefix with single underscore `_`
  ```python
  class AudioCapture:
      def start_capture(self):  # Public
          self._initialize_stream()  # Private

      def _initialize_stream(self):  # Private helper
          ...
  ```

### Constants

- **UPPER_SNAKE_CASE:** Module-level constants
  ```python
  # src/audio/capture.py
  DEFAULT_SAMPLE_RATE = 16000
  BUFFER_DURATION_MS = 500
  MAX_AUDIO_LENGTH_S = 30
  ```

### Qt Signals and Slots

**Signals:** Use `camelCase` matching Qt convention:
```python
class WhisperEngine(QObject):
    transcriptionComplete = pyqtSignal(str, int)  # camelCase
    errorOccurred = pyqtSignal(str)
    modelLoaded = pyqtSignal(str)
```

**Slots:** Use `snake_case` with `on_` prefix for signal handlers:
```python
class MainWindow(QWidget):
    def __init__(self):
        self.whisper.transcriptionComplete.connect(self.on_transcription_complete)

    @pyqtSlot(str, int)
    def on_transcription_complete(self, text: str, latency_ms: int):
        """Handle transcription completion signal."""
        ...
```

### Variables

- **Snake_case:** All variables
  ```python
  audio_data = np.zeros(1024)
  sample_rate = 16000
  is_capturing = True
  ```

- **Avoid Single Letters:** Except for loop counters (`i`, `j`) or mathematical operations (`x`, `y`)
  ```python
  # GOOD
  for sample in audio_samples:
      process(sample)

  # BAD (unclear)
  for s in audio_samples:
      process(s)
  ```

---

## Docstring Standards

**Format:** Google-style docstrings for all public classes, methods, functions.

### Function Docstrings

```python
def transcribe_audio(
    self, audio_data: np.ndarray, model_name: str = "base"
) -> tuple[str, int]:
    """Transcribe audio using Whisper model.

    Runs Whisper inference on GPU if available, falls back to CPU.
    Releases GIL during inference to prevent blocking Qt event loop.

    Args:
        audio_data: Audio samples as float32 numpy array (16kHz mono).
        model_name: Whisper model size ("tiny", "base", "small", "medium", "large").

    Returns:
        Tuple of (transcribed_text, inference_latency_ms).

    Raises:
        ModelNotLoadedError: If model not loaded or download failed.
        CUDAOutOfMemoryError: If GPU runs out of VRAM during inference.
        TranscriptionTimeoutError: If inference exceeds 10s timeout.

    Example:
        >>> audio = load_audio("test.wav")
        >>> text, latency = engine.transcribe_audio(audio, model_name="base")
        >>> print(f"Transcribed: {text} ({latency}ms)")
    """
    ...
```

### Class Docstrings

```python
class AudioCapture(QObject):
    """Captures audio from microphone in background thread.

    Manages continuous audio capture via sounddevice, performs Voice Activity
    Detection (VAD) to detect speech segments, and emits Qt signals when
    speech is detected or ends.

    Thread Safety:
        - Audio callback runs in separate thread (not Qt event loop)
        - Emits signals via queued connection for thread safety
        - All public methods are thread-safe

    Signals:
        speechDetected(bytes): Emitted when VAD detects speech start.
        speechEnded(bytes): Emitted when VAD detects speech end.
        audioLevelChanged(float): Emitted periodically with RMS level (0.0-1.0).
        deviceDisconnected(): Emitted if microphone is unplugged.
        error(str): Emitted on audio capture errors.

    Attributes:
        is_capturing (bool): True if currently capturing audio.
        current_device (str): Name of current audio input device.

    Example:
        >>> capture = AudioCapture(config_manager, vad_processor)
        >>> capture.speechDetected.connect(on_speech_start)
        >>> capture.start_capture()
    """

    # Signals
    speechDetected = pyqtSignal(bytes)
    speechEnded = pyqtSignal(bytes)
    audioLevelChanged = pyqtSignal(float)
    deviceDisconnected = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, config: ConfigManager, vad: VADProcessor):
        """Initialize audio capture with configuration and VAD processor.

        Args:
            config: Global configuration manager.
            vad: Voice Activity Detection processor instance.
        """
        super().__init__()
        ...
```

### Property Docstrings

```python
@property
def is_capturing(self) -> bool:
    """True if audio capture is currently active.

    This property is thread-safe and can be checked from any thread.

    Returns:
        True if microphone stream is open and capturing.
    """
    return self._is_capturing
```

### Module Docstrings

```python
"""Audio capture and Voice Activity Detection module.

This module provides the AudioCapture class for continuous microphone monitoring
and the VADProcessor class for detecting speech segments using silero-vad.

Classes:
    AudioCapture: Manages microphone input and emits speech signals.
    VADProcessor: Processes audio chunks for voice activity detection.
    CircularAudioBuffer: Ring buffer for efficient audio storage.

Example:
    >>> from src.audio.capture import AudioCapture
    >>> from src.audio.vad_processor import VADProcessor
    >>>
    >>> vad = VADProcessor(config)
    >>> capture = AudioCapture(config, vad)
    >>> capture.start_capture()
"""
```

---

## Error Handling Patterns

### Custom Exception Hierarchy

**Define in `src/utils/exceptions.py`:**
```python
class FedoraVoiceError(Exception):
    """Base exception for all application errors."""
    pass

class AudioError(FedoraVoiceError):
    """Base exception for audio-related errors."""
    pass

class DeviceNotFoundError(AudioError):
    """Audio input device not found or inaccessible."""
    pass

class VADError(AudioError):
    """Voice Activity Detection failed."""
    pass

class TranscriptionError(FedoraVoiceError):
    """Base exception for transcription errors."""
    pass

class ModelNotLoadedError(TranscriptionError):
    """Whisper model not loaded or download failed."""
    pass

class CUDAOutOfMemoryError(TranscriptionError):
    """GPU VRAM exhausted during inference."""
    pass

class WaylandError(FedoraVoiceError):
    """Base exception for Wayland integration errors."""
    pass

class TextInjectionFailedError(WaylandError):
    """Failed to inject text via Wayland or clipboard."""
    pass
```

### Exception Handling Best Practices

**1. Catch Specific Exceptions:**
```python
# GOOD
try:
    model = self.model_manager.load_model("base")
except ModelNotLoadedError as e:
    logger.error(f"Model loading failed: {e}")
    self.error.emit(str(e))
except CUDAOutOfMemoryError:
    logger.warning("CUDA OOM, falling back to CPU")
    self.switch_to_cpu_mode()

# BAD: Bare except
try:
    model = self.model_manager.load_model("base")
except Exception as e:  # Too broad!
    logger.error(f"Error: {e}")
```

**2. Use Context Managers:**
```python
# GOOD
def _audio_callback(self, indata, frames, time_info, status):
    try:
        with self._buffer_lock:
            self._buffer.append(indata.copy())
    except Exception as e:
        logger.exception("Audio callback error")
        self.error.emit(str(e))

# GOOD: File operations
def save_config(self, config: dict):
    config_path = Path(self._config_file)
    temp_path = config_path.with_suffix(".tmp")

    try:
        with temp_path.open("w") as f:
            json.dump(config, f, indent=2)
        temp_path.rename(config_path)  # Atomic write
    except OSError as e:
        logger.error(f"Failed to save config: {e}")
        raise ConfigWriteError(f"Could not write config to {config_path}") from e
```

**3. Always Log Exceptions:**
```python
import logging

logger = logging.getLogger(__name__)

def transcribe_audio(self, audio: np.ndarray) -> str:
    try:
        result = self._model.transcribe(audio)
        return result["text"]
    except CUDAOutOfMemoryError as e:
        logger.error(f"CUDA OOM during transcription: {e}", exc_info=True)
        self.error.emit("GPU out of memory. Try smaller model.")
        raise
    except Exception as e:
        logger.exception("Unexpected transcription error")  # Full traceback
        raise TranscriptionError("Transcription failed") from e
```

**4. Emit Qt Signals on Errors:**
```python
class WhisperEngine(QObject):
    errorOccurred = pyqtSignal(str)  # User-facing error message

    def transcribe_async(self, audio: bytes):
        try:
            text = self._transcribe(audio)
            self.transcriptionComplete.emit(text)
        except ModelNotLoadedError as e:
            logger.error(f"Model not loaded: {e}")
            self.errorOccurred.emit("Whisper model not loaded. Check settings.")
        except CUDAOutOfMemoryError:
            logger.error("CUDA OOM")
            self.errorOccurred.emit("GPU memory full. Try CPU mode or smaller model.")
```

**5. Circuit Breaker for GPU Failures:**
```python
class WhisperEngine(QObject):
    def __init__(self):
        self._cuda_failures = 0
        self._cuda_disabled = False

    def transcribe_audio(self, audio: np.ndarray) -> str:
        # Circuit breaker: Disable CUDA after 3 consecutive failures
        if self._cuda_failures >= 3:
            if not self._cuda_disabled:
                logger.warning("CUDA circuit breaker activated, switching to CPU")
                self._switch_to_cpu()
                self._cuda_disabled = True

        try:
            result = self._model.transcribe(audio)
            self._cuda_failures = 0  # Reset on success
            return result["text"]
        except CUDAOutOfMemoryError:
            self._cuda_failures += 1
            logger.error(f"CUDA failure {self._cuda_failures}/3")
            raise
```

**6. Timeout Standards:**

**CRITICAL:** All I/O operations and long-running tasks must have timeouts to prevent hangs.

```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds: int, error_message: str):
    """Context manager for operation timeout (Unix only).

    Args:
        seconds: Timeout duration in seconds.
        error_message: Error message if timeout occurs.

    Raises:
        TimeoutError: If operation exceeds timeout.
    """
    def timeout_handler(signum, frame):
        raise TimeoutError(error_message)

    # Set the signal handler and alarm
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

# Usage example:
try:
    with timeout(10, "Whisper inference timeout after 10s"):
        result = self._model.transcribe(audio)
except TimeoutError as e:
    logger.error(f"Operation timed out: {e}")
    raise TranscriptionTimeoutError("Transcription took too long") from e
```

**Standard Timeout Values:**
| Operation | Timeout | Rationale |
|-----------|---------|-----------|
| Model download (network) | 30s | Allow for slow connections |
| Model loading (disk I/O) | 10s | Large model files (~150MB) |
| Whisper inference | 10s | Fallback to error if too slow |
| Wayland protocol calls | 1s | Should be near-instant |
| Config file read/write | 5s | Disk I/O should be fast |
| Database queries (SQLite) | 2s | Local DB should be fast |

**7. Error Message UX Standards:**

**Rule:** Separate user-facing messages from developer-facing details.

```python
class FedoraVoiceError(Exception):
    """Base exception with dual messages for UX and debugging.

    Attributes:
        user_message: Friendly message shown in UI.
        dev_message: Technical details for logs.
    """

    def __init__(self, user_message: str, dev_message: str | None = None):
        self.user_message = user_message
        self.dev_message = dev_message or user_message
        super().__init__(self.dev_message)

# Example usage:
class ModelNotLoadedError(TranscriptionError):
    pass

# In code:
try:
    model = self._load_model(model_path)
except FileNotFoundError as e:
    raise ModelNotLoadedError(
        user_message="Could not load speech recognition model. Please check your internet connection and try downloading again.",
        dev_message=f"Model file not found: {model_path}, error: {e}"
    ) from e

# In UI error handler:
def show_error(error: Exception):
    if isinstance(error, FedoraVoiceError):
        error_dialog.setText(error.user_message)  # User-friendly
        logger.error(error.dev_message)  # Technical details
    else:
        error_dialog.setText("An unexpected error occurred")
        logger.exception("Unexpected error")
```

**8. Configuration Validation Standards:**

**MANDATORY:** Use Pydantic for runtime configuration validation to prevent invalid states.

```python
from pydantic import BaseModel, validator, Field

class AudioConfig(BaseModel):
    """Audio configuration with automatic validation.

    All config classes must inherit from BaseModel for validation.
    """
    device_index: int = Field(
        default=-1,
        ge=-1,
        description="Audio device index (-1 for default)"
    )
    sample_rate: int = Field(
        default=16000,
        ge=8000,
        le=48000,
        description="Sample rate in Hz"
    )
    channels: int = Field(
        default=1,
        ge=1,
        le=2,
        description="1=mono, 2=stereo"
    )
    buffer_duration_ms: int = Field(
        default=500,
        ge=100,
        le=5000,
        description="Audio buffer duration"
    )

    @validator('sample_rate')
    def validate_sample_rate(cls, v):
        """Ensure sample rate is a common value."""
        allowed = [8000, 16000, 22050, 44100, 48000]
        if v not in allowed:
            raise ValueError(
                f"Sample rate {v} not supported. Use one of {allowed}"
            )
        return v

    class Config:
        """Pydantic config."""
        validate_assignment = True  # Validate on attribute assignment

# Usage:
try:
    config = AudioConfig(**user_config_dict)  # Validates automatically
except ValidationError as e:
    logger.error(f"Invalid audio configuration: {e}")
    raise ConfigurationError(
        user_message="Audio settings are invalid. Please reset to defaults.",
        dev_message=f"Audio config validation failed: {e.errors()}"
    ) from e
```

---

## Qt-Specific Conventions

### Thread Safety Rules

**CRITICAL RULE #1: NEVER access Qt widgets from non-main thread.**

This is the most common cause of crashes in Qt applications. Qt widgets are NOT thread-safe.

```python
# ❌ FATAL ERROR - Will cause segfault/crash:
class TranscriptionWorker(QObject):
    def transcribe(self, audio: bytes):
        text = self._model.transcribe(audio)
        self.status_label.setText(text)  # CRASH! Widget access from worker thread

# ✅ CORRECT - Use signals to cross thread boundary:
class TranscriptionWorker(QObject):
    transcriptionComplete = pyqtSignal(str)  # Signal is thread-safe

    def transcribe(self, audio: bytes):
        text = self._model.transcribe(audio)
        self.transcriptionComplete.emit(text)  # Signal crosses thread safely

# In main thread:
worker.transcriptionComplete.connect(self.on_transcription_complete)

@pyqtSlot(str)
def on_transcription_complete(self, text: str):
    self.status_label.setText(text)  # OK - on main thread
```

**Thread-Safe Qt Operations:**
- ✅ Emitting signals from any thread
- ✅ Accessing `QThread`, `QMutex`, `QObject` (non-widget)
- ✅ Logging with `logging` module
- ❌ Accessing ANY `QWidget` subclass (QLabel, QPushButton, etc.)
- ❌ Creating widgets outside main thread
- ❌ Calling `QApplication` methods from worker threads

### Signal/Slot Connections

**1. Use New-Style Connections:**
```python
# GOOD: Type-safe, compile-time checked
self.audio_capture.speechDetected.connect(self.on_speech_detected)

# BAD: Old-style (deprecated)
self.connect(self.audio_capture, SIGNAL("speechDetected(bytes)"), self.on_speech_detected)
```

**2. Annotate Slots with `@pyqtSlot`:**
```python
from PyQt5.QtCore import pyqtSlot

class MainWindow(QWidget):
    @pyqtSlot(str, int)
    def on_transcription_complete(self, text: str, latency_ms: int):
        """Handle Whisper transcription completion."""
        logger.info(f"Transcription: {text} ({latency_ms}ms)")
        self.status_label.setText(text)
```

**3. Always Specify Connection Type for Cross-Thread Signals:**

**CRITICAL:** Use `Qt.QueuedConnection` for signals crossing thread boundaries.

```python
from PyQt5.QtCore import Qt

# GOOD: Explicit queued connection (thread-safe)
self.audio_worker.speechDetected.connect(
    self.on_speech_detected,
    Qt.QueuedConnection  # REQUIRED for cross-thread safety
)

# GOOD: Explicit direct connection (same thread, performance-critical)
self.button.clicked.connect(
    self.on_button_click,
    Qt.DirectConnection  # OK - both on main thread
)

# BAD: Auto connection (unclear behavior, potential race conditions)
self.audio_worker.speechDetected.connect(
    self.on_speech_detected  # Auto - may be direct or queued!
)
```

**Connection Type Decision Matrix:**
| Scenario | Connection Type | Reason |
|----------|----------------|--------|
| Worker thread → Main thread UI update | `Qt.QueuedConnection` | Thread-safe, queues event |
| Same thread, not performance-critical | `Qt.AutoConnection` | OK - Qt chooses correctly |
| Same thread, performance-critical | `Qt.DirectConnection` | Avoids event queue overhead |
| **NEVER use** | `Qt.BlockingQueuedConnection` | Can cause deadlocks |

**4. Signal Connection Lifecycle:**

```python
# RULE: Connect in __init__, disconnect in cleanup

class AudioCapture(QObject):
    speechDetected = pyqtSignal(bytes)

    def __init__(self, vad_processor: VADProcessor):
        super().__init__()
        self._vad = vad_processor
        self._setup_connections()  # Centralize connections

    def _setup_connections(self):
        """Centralize all signal connections."""
        # Connect VAD signals
        self._vad.speechStarted.connect(self._on_speech_start, Qt.QueuedConnection)
        self._vad.speechEnded.connect(self._on_speech_end, Qt.QueuedConnection)

    def cleanup(self):
        """Clean up signal connections before destruction."""
        try:
            self._vad.speechStarted.disconnect(self._on_speech_start)
            self._vad.speechEnded.disconnect(self._on_speech_end)
        except (RuntimeError, TypeError):
            # Already disconnected or C++ object deleted
            pass

    def __del__(self):
        """Ensure cleanup on destruction."""
        self.cleanup()
```

**5. Disconnect Signals in Widget Cleanup:**
```python
def closeEvent(self, event):
    """Override QWidget.closeEvent to clean up signals."""
    # Disconnect signals to prevent dangling references
    self.audio_capture.speechDetected.disconnect()
    self.whisper_engine.transcriptionComplete.disconnect()

    # Stop threads
    self.audio_capture.stop_capture()
    self.whisper_worker_thread.quit()
    self.whisper_worker_thread.wait()

    event.accept()
```

### Thread Safety with QMutex

```python
from PyQt5.QtCore import QMutex, QMutexLocker

class CircularAudioBuffer:
    def __init__(self, max_size: int):
        self._buffer: list[bytes] = []
        self._mutex = QMutex()
        self._max_size = max_size

    def append(self, data: bytes):
        """Thread-safe append."""
        with QMutexLocker(self._mutex):  # RAII lock
            self._buffer.append(data)
            if len(self._buffer) > self._max_size:
                self._buffer.pop(0)

    def get_all(self) -> list[bytes]:
        """Thread-safe get all data."""
        with QMutexLocker(self._mutex):
            return self._buffer.copy()
```

### QThread Usage

**1. Move Objects to Threads (Preferred):**
```python
# GOOD: Move object to QThread
class TranscriptionWorker(QObject):
    transcriptionComplete = pyqtSignal(str)

    @pyqtSlot(bytes)
    def transcribe(self, audio: bytes):
        text = self._model.transcribe(audio)
        self.transcriptionComplete.emit(text)

# In main thread:
worker = TranscriptionWorker()
thread = QThread()
worker.moveToThread(thread)

# Connect signals
audio_capture.speechEnded.connect(worker.transcribe)
worker.transcriptionComplete.emit(self.on_transcription_complete)

thread.start()
```

**2. Avoid Subclassing QThread:**
```python
# BAD: Subclassing QThread (old Qt4 style)
class TranscriptionThread(QThread):
    def run(self):
        # Run method executes in thread
        ...

# GOOD: Use moveToThread pattern above
```

---

## File and Module Organization

### Project Structure

```
src/
├── __init__.py
├── __main__.py                 # Entry point
├── audio/
│   ├── __init__.py
│   ├── capture.py             # AudioCapture class
│   ├── vad_processor.py       # VADProcessor class
│   └── circular_buffer.py     # CircularAudioBuffer class
├── transcription/
│   ├── __init__.py
│   ├── whisper_engine.py      # WhisperEngine class
│   ├── model_manager.py       # ModelManager class
│   └── model_downloader.py    # ModelDownloader class
├── wayland/
│   ├── __init__.py
│   ├── text_injection.py      # TextInjection class
│   ├── protocol.py            # WaylandProtocol class
│   └── clipboard_fallback.py  # ClipboardFallback class
├── ui/
│   ├── __init__.py
│   ├── system_tray.py         # SystemTray class
│   ├── settings_window.py     # SettingsWindow class
│   ├── history_viewer.py      # HistoryViewer class
│   └── audio_indicator.py     # AudioIndicator class
├── core/
│   ├── __init__.py
│   ├── state_machine.py       # StateMachine class
│   ├── config_manager.py      # ConfigManager class
│   ├── history_manager.py     # HistoryManager class
│   └── hotkey_manager.py      # HotkeyManager class
└── utils/
    ├── __init__.py
    ├── logger.py              # Logging configuration
    ├── exceptions.py          # Custom exception hierarchy
    ├── notification.py        # NotificationManager class
    └── error_handler.py       # ErrorHandler class
```

### Module-Level Exports

**Use `__all__` in `__init__.py`:**
```python
# src/audio/__init__.py
"""Audio capture and processing module."""

from .capture import AudioCapture
from .vad_processor import VADProcessor
from .circular_buffer import CircularAudioBuffer

__all__ = ["AudioCapture", "VADProcessor", "CircularAudioBuffer"]
```

### One Class Per File

**Rule:** Each file should contain ONE primary class (exceptions for small helper classes).

```python
# GOOD: src/audio/capture.py contains only AudioCapture
class AudioCapture(QObject):
    ...

# GOOD: Small helper class in same file
class _AudioStreamConfig:
    """Internal helper for stream configuration."""
    ...

# BAD: Multiple unrelated classes in one file
class AudioCapture(QObject): ...
class WhisperEngine(QObject): ...  # Should be in separate file!
```

---

## Code Review Requirements

### Pre-Commit Checklist

Before committing code, ensure:

- [ ] **Linting passes:** `ruff check src/ tests/` (no errors)
- [ ] **Formatting passes:** `black --check src/ tests/` (no changes needed)
- [ ] **Type checking passes:** `mypy src/` (no errors)
- [ ] **Tests pass:** `pytest tests/` (all tests green)
- [ ] **Test coverage:** New code has ≥60% coverage (`pytest --cov=src`)
- [ ] **Docstrings added:** All public functions/classes have docstrings
- [ ] **No debug code:** Remove `print()`, `breakpoint()`, commented code
- [ ] **Signals/slots connected:** Check for proper cleanup in `closeEvent()`

### Pull Request Requirements

**Before creating PR:**

1. **Run full test suite:**
   ```bash
   pytest tests/ --cov=src --cov-report=html
   ```

2. **Check for type errors:**
   ```bash
   mypy src/ --strict
   ```

3. **Run linters:**
   ```bash
   ruff check src/ tests/ --fix
   black src/ tests/
   ```

4. **Manual testing:**
   - Test on GNOME and KDE (or document skipped DEs)
   - Verify GPU and CPU modes work
   - Check latency meets targets (<1000ms MVP, <500ms goal)

**PR Description Must Include:**
- **What:** Brief summary of changes
- **Why:** Motivation and context (link to issue/epic)
- **How:** Technical approach overview
- **Testing:** Manual testing performed + screenshots/videos
- **Latency Impact:** If touching critical path, include benchmark results

**Example PR Description:**
```markdown
# What
Implement Whisper model download with progress bar (Epic 1, Story 1.2)

# Why
Users need to download base.pt model (~150MB) on first launch. Currently no feedback during download.

# How
- Added `ModelDownloader` class with Qt signals for progress
- Integrated progress bar in `SettingsWindow`
- Added retry logic with exponential backoff (3 attempts)
- Model stored in `~/.local/share/fedora-voice-dictation/models/`

# Testing
- [x] Manual test on fresh Fedora 40 install (no model)
- [x] Download completes successfully (~2min on 10Mbps)
- [x] Progress bar updates every 500ms
- [x] Retry works after simulated network failure
- [x] Unit tests added (`test_model_downloader.py`, 75% coverage)

# Screenshots
[Screenshot of progress bar at 45%]

# Latency Impact
No impact (download happens once during setup, not in dictation path)
```

### Code Review Criteria

**Reviewers must check:**

1. **Correctness:** Does code do what it claims?
2. **Thread safety:** Are Qt signals used correctly? QMutex for shared state?
3. **Error handling:** Are exceptions caught and logged? Circuit breakers for GPU?
4. **Performance:** Does it meet latency budget? Any blocking calls in main thread?
5. **Test coverage:** Are critical paths tested?
6. **Documentation:** Are docstrings complete and accurate?
7. **Style:** Does it pass linting? Follow naming conventions?

**Approval Criteria:**
- ✅ At least 1 approving review from team member
- ✅ All CI checks pass (linting, tests, type checking)
- ✅ No unresolved comments from reviewers
- ✅ Test coverage does not decrease (or justification provided)

---

## Linting Configuration

### Ruff Configuration

**`pyproject.toml`:**
```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort (import sorting)
    "N",   # pep8-naming
    "UP",  # pyupgrade (modern Python syntax)
    "B",   # flake8-bugbear (common bugs)
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
    "RET", # flake8-return
]
ignore = [
    "E501",  # Line too long (handled by black)
    "B008",  # Do not perform function calls in argument defaults (needed for Qt signals)
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]  # Allow assert in tests

[tool.ruff.lint.isort]
known-first-party = ["src"]
```

### Black Configuration

**`pyproject.toml`:**
```toml
[tool.black]
line-length = 88
target-version = ["py311"]
include = '\.pyi?$'
extend-exclude = '''
/(
  # Exclude vendored dependencies
  | vendor
  # Exclude virtual environments
  | venv
  | .venv
)/
'''
```

---

## Performance Guidelines

### Critical Path Optimization

**Rule:** Any code in the dictation path (hotkey press → text injected) must be optimized for latency.

**Latency Budget Reminders:**
| Component | Budget | Optimization |
|-----------|--------|-------------|
| Audio Capture | 50ms | Use circular buffer, no blocking I/O |
| VAD Processing | 100ms | GPU-accelerated if possible, batch processing |
| Whisper Inference | 500-800ms | CUDA + FP16, release GIL during inference |
| Text Injection | 50ms | Async Wayland calls, clipboard is faster |
| **Total** | **<1000ms MVP** | Profile with `cProfile`, `line_profiler` |

### Avoid Blocking Main Thread

```python
# BAD: Blocking call in main thread
def on_hotkey_press(self):
    text = self.whisper.transcribe(self.audio_buffer)  # BLOCKS UI!
    self.inject_text(text)

# GOOD: Async with signals
def on_hotkey_press(self):
    self.state_machine.trigger_hotkey()  # Non-blocking state change
    # WhisperEngine runs in separate QThread, emits signal when done

@pyqtSlot(str)
def on_transcription_complete(self, text: str):
    self.text_injection.inject_async(text)  # Non-blocking
```

### GPU Memory Management

```python
# GOOD: Clear GPU cache after inference
def transcribe_audio(self, audio: np.ndarray) -> str:
    try:
        with torch.no_grad():  # Disable gradient computation
            result = self._model.transcribe(audio)
    finally:
        torch.cuda.empty_cache()  # Free unused GPU memory
    return result["text"]
```

---

## Logging Standards

### Logger Configuration

**Use module-level loggers:**
```python
import logging

logger = logging.getLogger(__name__)  # Use __name__ for module path

class AudioCapture(QObject):
    def start_capture(self):
        logger.info("Starting audio capture on device %s", self._device_name)
        try:
            self._stream.start()
        except Exception as e:
            logger.exception("Failed to start audio capture")
            raise
```

### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| `DEBUG` | Verbose diagnostic info (off by default) | `"VAD confidence: 0.87"` |
| `INFO` | Important state changes | `"Audio capture started"`, `"Model loaded: base.pt"` |
| `WARNING` | Recoverable issues | `"CUDA not available, using CPU"`, `"Clipboard fallback used"` |
| `ERROR` | Errors that prevent operation | `"Failed to load model"`, `"Microphone not found"` |
| `CRITICAL` | Application cannot continue | `"Fatal: Config file corrupted"` |

### Logging Best Practices

```python
# GOOD: Use lazy formatting (% operator, not f-strings)
logger.info("Transcription complete: %s (%dms)", text[:50], latency_ms)

# BAD: Eager formatting (always evaluates, even if log level disabled)
logger.debug(f"Audio data: {audio_data}")  # Expensive if DEBUG disabled!

# GOOD: Include exception info with exc_info=True or logger.exception()
try:
    model = load_model("base")
except Exception as e:
    logger.exception("Model loading failed")  # Includes full traceback

# GOOD: Structured logging with extra fields (for future JSON logging)
logger.info(
    "Dictation session completed",
    extra={
        "session_id": session.id,
        "latency_ms": session.latency_ms,
        "model": session.model_used,
    },
)
```

### Logger Setup (src/utils/logger.py)

```python
import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: Path | None = None):
    """Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional file path for log output.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console handler (stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
```

---

## Git Commit Message Standards

### Format

```
<type>(<scope>): <short summary>

<body>

<footer>
```

**Example:**
```
feat(audio): Add VAD processor with silero-vad integration

Implement VADProcessor class to detect speech segments in audio stream.
Uses silero-vad model with 95% confidence threshold. Emits Qt signals
for speech_detected and speech_ended events.

Closes #12
```

### Commit Types

| Type | Usage |
|------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code restructuring (no behavior change) |
| `perf` | Performance improvement |
| `test` | Add/update tests |
| `docs` | Documentation changes |
| `chore` | Build, CI, or tooling changes |
| `style` | Code formatting (not functional changes) |

### Scopes

Common scopes for this project:
- `audio` - Audio capture, VAD, buffers
- `transcription` - Whisper engine, model management
- `wayland` - Text injection, protocol, clipboard
- `ui` - System tray, settings, history viewer
- `core` - State machine, config, history, hotkeys
- `tests` - Test infrastructure
- `ci` - GitHub Actions, pre-commit hooks

**Example Commits:**
```
feat(transcription): Add CUDA circuit breaker for GPU failures
fix(audio): Prevent deadlock in circular buffer append
perf(transcription): Enable FP16 for 2x faster inference
test(wayland): Add integration tests for text injection
docs(architecture): Update threading model diagram
chore(ci): Add mypy strict mode to CI pipeline
```

---


