# Testing Strategy

This section defines the comprehensive testing approach covering unit tests, integration tests, performance benchmarks, and quality assurance processes.

---

## Testing Philosophy

**Core Principles:**

1. **Test Pyramid:** 60% unit tests, 30% integration tests, 10% end-to-end tests
2. **Test-Driven Development:** Write tests before implementation where feasible (especially for Core/Utils components)
3. **Continuous Testing:** All tests run on every commit via CI/CD
4. **Performance Regression Prevention:** Automated latency benchmarks track performance over time
5. **GPU-Independent CI:** Unit tests run on CPU-only CI runners; GPU tests manual on dev systems

**Testing Goals:**

- ✅ **60%+ code coverage** across all modules (measured by pytest-cov)
- ✅ **Zero failing tests** in main branch at all times
- ✅ **<1000ms p95 latency** verified by automated benchmarks
- ✅ **All components mockable** for isolated testing
- ✅ **Type safety** enforced by mypy strict mode

---

## Test Categories

| Category | Coverage Target | Tools | Execution Context | Frequency |
|----------|----------------|-------|-------------------|-----------|
| **Unit Tests** | 70%+ | pytest, pytest-qt, pytest-mock | CI (CPU only) | Every commit |
| **Integration Tests** | Key workflows | pytest, pytest-qt | Manual (GPU required) | Before merge to main |
| **Performance Benchmarks** | Latency targets | pytest-benchmark, custom scripts | Manual (GPU required) | Weekly, before releases |
| **Type Checking** | 100% coverage | mypy --strict | CI | Every commit |
| **Linting** | All rules pass | ruff | CI | Every commit |
| **Code Formatting** | 100% formatted | black --check | CI | Every commit |

---

## Unit Testing

**Scope:** Test individual components in isolation with mocked dependencies.

**Framework:** pytest 7.4+ with pytest-qt 4.2+ for PyQt5 components

**Mocking Strategy:** Use pytest-mock (wrapper around unittest.mock) for all external dependencies

---

### Unit Test Structure

**Directory Layout:**

```
tests/unit/
├── test_audio/
│   ├── test_audio_capture.py        # AudioCapture unit tests
│   ├── test_vad_processor.py        # VAD unit tests
│   └── test_circular_buffer.py      # CircularAudioBuffer tests
├── test_transcription/
│   ├── test_whisper_engine.py       # WhisperEngine with mocked model
│   ├── test_model_manager.py        # ModelManager tests
│   └── test_model_downloader.py     # ModelDownloader with mocked requests
├── test_wayland/
│   ├── test_text_injection.py       # TextInjection orchestrator
│   ├── test_text_input_protocol.py  # Protocol with mocked Wayland
│   └── test_clipboard_fallback.py   # Clipboard with mocked pyperclip
├── test_ui/
│   ├── test_system_tray.py          # SystemTray with qtbot
│   ├── test_settings_window.py      # SettingsWindow with qtbot
│   └── test_history_viewer.py       # HistoryViewer with qtbot
├── test_core/
│   ├── test_state_machine.py        # StateMachine with signal spy
│   ├── test_config_manager.py       # ConfigManager with temp files
│   ├── test_history_manager.py      # HistoryManager with temp files
│   └── test_hotkey_manager.py       # HotkeyManager with mocked D-Bus
└── test_utils/
    ├── test_logger.py               # Logger with temp log files
    ├── test_notifications.py        # NotificationManager with mocked D-Bus
    └── test_error_handler.py        # ErrorHandler with simulated exceptions
```

---

### Example Unit Test: AudioCapture

```python
# tests/unit/test_audio/test_audio_capture.py

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from PyQt5.QtTest import QSignalSpy

from src.audio.capture import AudioCapture
from src.audio.vad import VADProcessor
from src.core.config import ConfigManager


@pytest.fixture
def mock_config():
    """Mock configuration manager."""
    config = Mock(spec=ConfigManager)
    config.get.side_effect = lambda key: {
        "audio.device_id": "default",
        "audio.sample_rate": 16000,
        "audio.channels": 1,
        "audio.buffer_duration_ms": 5000,
        "audio.buffer_max_duration_ms": 30000,
    }[key]
    return config


@pytest.fixture
def mock_vad():
    """Mock VAD processor."""
    vad = Mock(spec=VADProcessor)
    vad.process_chunk.return_value = True  # Always detect speech
    return vad


@pytest.fixture
def audio_capture(mock_config, mock_vad):
    """Create AudioCapture with mocked dependencies."""
    return AudioCapture(mock_config, mock_vad)


def test_audio_capture_initialization(audio_capture, mock_config):
    """Test AudioCapture initializes with correct configuration."""
    assert audio_capture.device_id == "default"
    assert audio_capture.sample_rate == 16000
    assert audio_capture.channels == 1
    assert not audio_capture.capturing  # Not capturing initially


@patch('src.audio.capture.sounddevice.InputStream')
def test_start_capture_creates_stream(mock_stream_class, audio_capture):
    """Test start_capture creates sounddevice InputStream."""
    # Arrange
    mock_stream = MagicMock()
    mock_stream_class.return_value.__enter__.return_value = mock_stream

    # Act
    audio_capture.start_capture()

    # Assert
    mock_stream_class.assert_called_once_with(
        device="default",
        channels=1,
        samplerate=16000,
        callback=audio_capture._audio_callback,
        blocksize=audio_capture.block_size
    )
    assert audio_capture.capturing


def test_audio_callback_emits_level_signal(audio_capture, qtbot):
    """Test _audio_callback emits audioLevelChanged signal."""
    # Arrange
    spy = QSignalSpy(audio_capture.audioLevelChanged)
    audio_data = np.random.rand(1024).astype(np.float32) * 0.5  # 50% level

    # Act
    audio_capture._audio_callback(audio_data, 1024, None, None)

    # Assert
    assert len(spy) == 1
    emitted_level = spy[0][0]
    assert 0.0 <= emitted_level <= 1.0


def test_audio_callback_detects_speech(audio_capture, mock_vad, qtbot):
    """Test _audio_callback detects speech via VAD and emits signal."""
    # Arrange
    spy = QSignalSpy(audio_capture.speechDetected)
    audio_data = np.random.rand(1024).astype(np.float32)
    mock_vad.process_chunk.return_value = True  # Speech detected

    # Act
    audio_capture._audio_callback(audio_data, 1024, None, None)

    # Assert
    assert len(spy) == 1  # speechDetected emitted


def test_audio_callback_detects_silence_after_speech(audio_capture, mock_vad, qtbot):
    """Test _audio_callback emits speechEnded after silence following speech."""
    # Arrange
    spy = QSignalSpy(audio_capture.speechEnded)

    # Simulate speech
    audio_capture.was_speaking = True
    audio_capture.silence_duration = 600  # > vad_timeout (500ms)

    # Mock VAD to return non-speech
    mock_vad.process_chunk.return_value = False

    audio_data = np.random.rand(1024).astype(np.float32) * 0.01  # Low level (silence)

    # Act
    audio_capture._audio_callback(audio_data, 1024, None, None)

    # Assert
    assert len(spy) == 1  # speechEnded emitted
    assert not audio_capture.was_speaking  # Reset after speech end


def test_stop_capture_finalizes_buffer(audio_capture):
    """Test stop_capture sets capturing flag to False."""
    # Arrange
    audio_capture.capturing = True

    # Act
    audio_capture.stop_capture()

    # Assert
    assert not audio_capture.capturing


def test_list_devices_returns_device_list(audio_capture):
    """Test list_devices returns available audio devices."""
    with patch('src.audio.capture.sounddevice.query_devices') as mock_query:
        # Arrange
        mock_query.return_value = [
            {'name': 'Default Microphone', 'max_input_channels': 1},
            {'name': 'USB Mic', 'max_input_channels': 2}
        ]

        # Act
        devices = audio_capture.list_devices()

        # Assert
        assert len(devices) == 2
        assert devices[0]['name'] == 'Default Microphone'


def test_get_current_level_returns_float(audio_capture):
    """Test get_current_level returns audio level as float."""
    # Arrange
    audio_capture._current_level = 0.75

    # Act
    level = audio_capture.get_current_level()

    # Assert
    assert isinstance(level, float)
    assert level == 0.75
```

---

### Example Unit Test: StateMachine

```python
# tests/unit/test_core/test_state_machine.py

import pytest
from unittest.mock import Mock
from PyQt5.QtCore import QStateMachine
from PyQt5.QtTest import QSignalSpy

from src.core.state_machine import StateMachine, ApplicationState
from src.core.config import ConfigManager


@pytest.fixture
def mock_config():
    config = Mock(spec=ConfigManager)
    return config


@pytest.fixture
def state_machine(mock_config, qtbot):
    """Create StateMachine instance."""
    sm = StateMachine(mock_config)
    sm.start()  # Start state machine
    qtbot.waitUntil(sm.started, timeout=1000)
    return sm


def test_state_machine_starts_in_idle(state_machine):
    """Test state machine initializes in IDLE state."""
    assert state_machine.idle_state.active()


def test_hotkey_triggers_transition_to_listening(state_machine, qtbot):
    """Test hotkey press transitions from IDLE to LISTENING."""
    # Arrange
    spy = QSignalSpy(state_machine.stateChanged)

    # Act
    state_machine.trigger_hotkey()

    # Wait for transition
    qtbot.waitUntil(lambda: state_machine.listening_state.active(), timeout=1000)

    # Assert
    assert state_machine.listening_state.active()
    assert len(spy) >= 1  # State changed at least once


def test_speech_ended_transitions_to_processing(state_machine, qtbot):
    """Test speech end transitions from LISTENING to PROCESSING."""
    # Arrange: Move to LISTENING state first
    state_machine.trigger_hotkey()
    qtbot.waitUntil(lambda: state_machine.listening_state.active(), timeout=1000)

    spy = QSignalSpy(state_machine.stateChanged)

    # Act
    audio_data = b'\x00' * 1024  # Dummy audio data
    state_machine.on_speech_ended(audio_data)

    # Wait for transition
    qtbot.waitUntil(lambda: state_machine.processing_state.active(), timeout=1000)

    # Assert
    assert state_machine.processing_state.active()


def test_transcription_complete_transitions_to_injecting(state_machine, qtbot):
    """Test transcription completion transitions PROCESSING to INJECTING."""
    # Arrange: Move to PROCESSING state
    state_machine.trigger_hotkey()
    qtbot.waitUntil(lambda: state_machine.listening_state.active(), timeout=1000)
    state_machine.on_speech_ended(b'\x00' * 1024)
    qtbot.waitUntil(lambda: state_machine.processing_state.active(), timeout=1000)

    # Create mock transcription result
    from src.transcription.whisper_engine import TranscriptionResult
    result = TranscriptionResult(
        text="Test transcription",
        segments=[],
        language="en",
        model_used="base",
        inference_time_ms=500,
        audio_duration_ms=2000,
        real_time_factor=0.25,
        error=None
    )

    # Act
    state_machine.on_transcription_complete(result)

    # Wait for transition
    qtbot.waitUntil(lambda: state_machine.injecting_state.active(), timeout=1000)

    # Assert
    assert state_machine.injecting_state.active()
    assert state_machine.context.transcription_result == result


def test_injection_complete_returns_to_idle(state_machine, qtbot):
    """Test injection completion returns state machine to IDLE."""
    # Arrange: Move through full flow
    state_machine.trigger_hotkey()
    qtbot.waitUntil(lambda: state_machine.listening_state.active(), timeout=1000)

    state_machine.on_speech_ended(b'\x00' * 1024)
    qtbot.waitUntil(lambda: state_machine.processing_state.active(), timeout=1000)

    from src.transcription.whisper_engine import TranscriptionResult
    result = TranscriptionResult(
        text="Test", segments=[], language="en", model_used="base",
        inference_time_ms=500, audio_duration_ms=2000, real_time_factor=0.25
    )
    state_machine.on_transcription_complete(result)
    qtbot.waitUntil(lambda: state_machine.injecting_state.active(), timeout=1000)

    from src.wayland.text_injection import InjectionResult
    injection_result = InjectionResult(
        success=True,
        method_used="clipboard",
        latency_ms=50,
        error=None
    )

    # Act
    state_machine.on_injection_complete(injection_result)

    # Wait for transition back to IDLE
    qtbot.waitUntil(lambda: state_machine.idle_state.active(), timeout=1000)

    # Assert
    assert state_machine.idle_state.active()


def test_error_transitions_to_error_state(state_machine, qtbot):
    """Test error during processing transitions to ERROR state."""
    # Arrange: Move to PROCESSING state
    state_machine.trigger_hotkey()
    qtbot.waitUntil(lambda: state_machine.listening_state.active(), timeout=1000)
    state_machine.on_speech_ended(b'\x00' * 1024)
    qtbot.waitUntil(lambda: state_machine.processing_state.active(), timeout=1000)

    # Create error result
    from src.transcription.whisper_engine import TranscriptionResult
    error_result = TranscriptionResult(
        text="", segments=[], language="", model_used="base",
        inference_time_ms=0, audio_duration_ms=0, real_time_factor=0.0,
        error="CUDA out of memory"
    )

    # Act
    state_machine.on_transcription_complete(error_result)

    # Wait for transition to ERROR
    qtbot.waitUntil(lambda: state_machine.error_state.active(), timeout=1000)

    # Assert
    assert state_machine.error_state.active()
```

---

### Mocking Guidelines

**Mock External Dependencies:**

```python
# Mock sounddevice (audio capture)
@patch('src.audio.capture.sounddevice.InputStream')
def test_with_mocked_audio(mock_stream):
    # Test code here
    pass

# Mock PyTorch Whisper
@patch('src.transcription.whisper_engine.whisper.load_model')
def test_with_mocked_whisper(mock_load_model):
    mock_model = Mock()
    mock_model.transcribe.return_value = {
        "text": "Test transcription",
        "segments": [],
        "language": "en"
    }
    mock_load_model.return_value = mock_model
    # Test code here

# Mock Wayland display
@patch('src.wayland.text_input_protocol.Display')
def test_with_mocked_wayland(mock_display):
    # Test code here
    pass

# Mock D-Bus
@patch('src.utils.notifications.dbus.SessionBus')
def test_with_mocked_dbus(mock_session_bus):
    # Test code here
    pass

# Mock filesystem operations
@patch('builtins.open', new_callable=mock_open, read_data='{"config": "data"}')
def test_with_mocked_file(mock_file):
    # Test code here
    pass
```

**Mock PyQt5 Signals for Testing:**

```python
from PyQt5.QtTest import QSignalSpy

def test_signal_emission(component, qtbot):
    """Test that component emits expected signal."""
    spy = QSignalSpy(component.someSignal)

    # Trigger action
    component.do_something()

    # Wait for signal (optional)
    qtbot.waitUntil(lambda: len(spy) > 0, timeout=1000)

    # Assert signal emitted
    assert len(spy) == 1
    assert spy[0][0] == expected_value  # Check signal arguments
```

---

## Integration Testing

**Scope:** Test component interactions and workflows with real dependencies where feasible.

**Execution:** Manual on developer system with GPU (cannot run in CPU-only CI)

---

### Integration Test Categories

**1. End-to-End Dictation Flow:**

```python
# tests/integration/test_end_to_end.py

import pytest
import numpy as np
from PyQt5.QtWidgets import QApplication

from src.core.main_loop import Application


@pytest.fixture(scope="module")
def app():
    """Create full application instance."""
    import sys
    app = Application(sys.argv)
    yield app
    app.quit()


def test_full_dictation_workflow(app, qtbot):
    """
    Test complete dictation workflow from hotkey to text injection.

    Prerequisites:
    - GPU with CUDA available
    - Microphone connected
    - Wayland session active
    """
    # Arrange
    state_machine = app.state_machine
    history_manager = app.history_manager

    initial_history_count = len(history_manager.sessions)

    # Act: Simulate hotkey press
    app.hotkey_manager.activated.emit()

    # Wait for LISTENING state
    qtbot.waitUntil(
        lambda: state_machine.listening_state.active(),
        timeout=2000
    )

    # Simulate speech (play fixture audio file or use real mic)
    # ... audio capture happens automatically ...

    # Wait for dictation to complete (back to IDLE)
    qtbot.waitUntil(
        lambda: state_machine.idle_state.active(),
        timeout=10000  # Allow up to 10s for full cycle
    )

    # Assert
    assert len(history_manager.sessions) == initial_history_count + 1

    last_session = history_manager.get_recent(1)[0]
    assert last_session.was_successful()
    assert last_session.transcribed_text != ""
    assert last_session.latency_ms < 2000  # Reasonable upper bound
```

**2. Audio Pipeline Integration:**

```python
# tests/integration/test_audio_pipeline.py

import pytest
import numpy as np
from src.audio.capture import AudioCapture
from src.audio.vad import VADProcessor
from src.core.config import ConfigManager


@pytest.fixture
def real_config():
    """Load real configuration."""
    config = ConfigManager()
    config.load()
    return config


@pytest.fixture
def real_vad(real_config):
    """Create real VAD processor (downloads model if needed)."""
    return VADProcessor(real_config)


@pytest.fixture
def real_audio_capture(real_config, real_vad):
    """Create real audio capture."""
    return AudioCapture(real_config, real_vad)


def test_audio_capture_with_real_vad(real_audio_capture, qtbot):
    """
    Test audio capture with real VAD model.

    Prerequisites:
    - Microphone connected
    - silero-vad model downloaded
    """
    # Arrange
    from PyQt5.QtTest import QSignalSpy
    spy = QSignalSpy(real_audio_capture.speechDetected)

    # Act: Start capture
    real_audio_capture.start_capture()

    # Wait for at least one audio level update (proves capture working)
    qtbot.wait(1000)  # Capture for 1 second

    # Stop capture
    real_audio_capture.stop_capture()

    # Assert: Capture was active
    assert real_audio_capture.buffer.duration_ms() > 0

    # Note: speechDetected may or may not emit depending on ambient sound
    # Just verify no crashes occurred
```

**3. Whisper Transcription Integration:**

```python
# tests/integration/test_whisper_transcription.py

import pytest
import numpy as np
from src.transcription.whisper_engine import WhisperEngine
from src.transcription.model_manager import ModelManager
from src.transcription.model_downloader import ModelDownloader
from src.core.config import ConfigManager


@pytest.fixture
def real_whisper_engine(real_config):
    """Create real Whisper engine with GPU."""
    downloader = ModelDownloader(real_config)
    manager = ModelManager(real_config, downloader)
    return WhisperEngine(real_config, manager)


def test_whisper_transcription_with_gpu(real_whisper_engine, qtbot):
    """
    Test Whisper transcription with real CUDA GPU.

    Prerequisites:
    - NVIDIA GPU with CUDA
    - base model downloaded
    - torch with CUDA installed
    """
    # Assert GPU available
    assert real_whisper_engine.is_cuda_available()

    # Arrange: Load fixture audio (5 seconds of speech)
    fixture_audio = np.load("tests/fixtures/audio/test_speech_5s.npy")

    from PyQt5.QtTest import QSignalSpy
    spy = QSignalSpy(real_whisper_engine.transcriptionComplete)

    # Act: Transcribe
    real_whisper_engine.transcribe_async(fixture_audio)

    # Wait for completion (should be <1000ms for base model)
    qtbot.waitUntil(lambda: len(spy) > 0, timeout=3000)

    # Assert
    assert len(spy) == 1
    result = spy[0][0]

    assert result.was_successful()
    assert result.text != ""
    assert result.inference_time_ms < 1000  # MVP target
    assert result.language == "en"
    assert result.model_used == "base"


def test_whisper_transcription_with_cpu_fallback(real_config, qtbot):
    """
    Test Whisper transcription with CPU fallback.

    Can run on CI (no GPU required).
    """
    # Force CPU mode
    real_config.config["advanced"]["enable_cpu_fallback"] = True

    # Mock CUDA as unavailable
    with patch('torch.cuda.is_available', return_value=False):
        downloader = ModelDownloader(real_config)
        manager = ModelManager(real_config, downloader)
        engine = WhisperEngine(real_config, manager)

        # Assert CPU mode active
        assert engine.use_cpu
        assert engine.device == "cpu"

        # Transcribe (will be slower)
        fixture_audio = np.load("tests/fixtures/audio/test_speech_5s.npy")
        result = engine.transcribe_sync(fixture_audio)

        # Assert works (but slower)
        assert result.was_successful()
        assert result.inference_time_ms > 1000  # CPU is slower
```

**4. Wayland Text Injection Integration:**

```python
# tests/integration/test_wayland_injection.py

import pytest
from src.wayland.text_injection import TextInjection
from src.wayland.window_focus import WindowFocus
from src.core.config import ConfigManager


@pytest.fixture
def real_text_injection(real_config):
    """Create real text injection with Wayland."""
    window_focus = WindowFocus()
    return TextInjection(real_config, window_focus)


def test_wayland_protocol_injection(real_text_injection, qtbot):
    """
    Test Wayland text-input-unstable-v3 protocol injection.

    Prerequisites:
    - Wayland session active
    - GNOME or KDE compositor
    - Text editor open and focused

    Manual verification: Check that "Test injection" appears in focused app.
    """
    # Arrange
    from src.wayland.window_focus import WindowInfo
    from datetime import datetime

    target_window = WindowInfo(
        application_name="Test Editor",
        window_title="Untitled - Text Editor",
        app_id="org.gnome.TextEditor",
        pid=12345,
        timestamp=datetime.now()
    )

    from PyQt5.QtTest import QSignalSpy
    spy = QSignalSpy(real_text_injection.injectionComplete)

    # Act
    real_text_injection.inject_async("Test injection via Wayland protocol", target_window)

    # Wait for completion
    qtbot.waitUntil(lambda: len(spy) > 0, timeout=2000)

    # Assert
    assert len(spy) == 1
    result = spy[0][0]

    # May succeed or fail depending on compositor support
    if result.success:
        assert result.method_used == "wayland_protocol"
        assert result.latency_ms < 500
    else:
        # Fallback to clipboard expected
        assert result.method_used == "clipboard"


def test_clipboard_fallback_injection(real_text_injection, qtbot):
    """
    Test clipboard fallback injection.

    Can run on any compositor.
    Manual verification: Check clipboard contains "Test clipboard"
    """
    # Force clipboard mode
    real_text_injection.config.config["text_injection"]["method"] = "clipboard_only"

    from src.wayland.window_focus import WindowInfo
    from datetime import datetime

    target_window = WindowInfo(
        application_name="Test",
        window_title="Test",
        app_id="test",
        pid=1,
        timestamp=datetime.now()
    )

    from PyQt5.QtTest import QSignalSpy
    spy = QSignalSpy(real_text_injection.injectionComplete)

    # Act
    real_text_injection.inject_async("Test clipboard fallback", target_window)

    # Wait for completion
    qtbot.waitUntil(lambda: len(spy) > 0, timeout=1000)

    # Assert
    assert len(spy) == 1
    result = spy[0][0]

    assert result.success
    assert result.method_used == "clipboard"
    assert result.latency_ms < 100  # Clipboard is fast
```

---

## Performance Benchmarking

**Objective:** Measure and track latency at each pipeline stage to ensure <500ms target.

**Framework:** pytest-benchmark + custom latency measurement

---

### Benchmark Suite

```python
# tests/integration/benchmark_latency.py

import pytest
import numpy as np
import time
from src.transcription.whisper_engine import WhisperEngine
from src.audio.vad import VADProcessor


@pytest.fixture
def benchmark_audio_fixtures():
    """Load audio fixtures of varying lengths."""
    return {
        "2s": np.load("tests/fixtures/audio/speech_2s.npy"),
        "5s": np.load("tests/fixtures/audio/speech_5s.npy"),
        "10s": np.load("tests/fixtures/audio/speech_10s.npy"),
    }


def test_benchmark_vad_inference(real_vad, benchmark):
    """Benchmark VAD inference latency."""
    from src.audio.buffer import AudioChunk

    chunk = AudioChunk(
        data=np.random.rand(512).astype(np.float32),  # 32ms at 16kHz
        timestamp=time.time(),
        sample_rate=16000,
        is_speech=False
    )

    # Benchmark
    result = benchmark(real_vad.process_chunk, chunk)

    # Assert: VAD should be <50ms per chunk (GPU) or <100ms (CPU)
    stats = benchmark.stats
    assert stats['mean'] < 0.05  # 50ms


def test_benchmark_whisper_inference_2s_audio(real_whisper_engine, benchmark_audio_fixtures, benchmark):
    """Benchmark Whisper inference on 2s audio."""
    audio = benchmark_audio_fixtures["2s"]

    # Benchmark
    result = benchmark(real_whisper_engine.transcribe_sync, audio)

    # Assert: Should complete in <500ms for 2s audio
    stats = benchmark.stats
    assert stats['mean'] < 0.5  # 500ms
    assert result.was_successful()


def test_benchmark_whisper_inference_5s_audio(real_whisper_engine, benchmark_audio_fixtures, benchmark):
    """Benchmark Whisper inference on 5s audio (typical use case)."""
    audio = benchmark_audio_fixtures["5s"]

    # Benchmark
    result = benchmark(real_whisper_engine.transcribe_sync, audio)

    # Assert: Should complete in <1000ms for 5s audio (MVP target)
    stats = benchmark.stats
    assert stats['mean'] < 1.0  # 1000ms
    print(f"\nWhisper 5s audio latency: {stats['mean']*1000:.0f}ms (target: <1000ms)")


def test_benchmark_whisper_inference_10s_audio(real_whisper_engine, benchmark_audio_fixtures, benchmark):
    """Benchmark Whisper inference on 10s audio (edge case)."""
    audio = benchmark_audio_fixtures["10s"]

    # Benchmark
    result = benchmark(real_whisper_engine.transcribe_sync, audio)

    # Log results (no strict assertion, just tracking)
    stats = benchmark.stats
    print(f"\nWhisper 10s audio latency: {stats['mean']*1000:.0f}ms")


def test_benchmark_end_to_end_latency(app, benchmark_audio_fixtures, qtbot):
    """
    Benchmark full end-to-end latency (hotkey → text injected).

    Prerequisites:
    - Full app initialized with GPU
    - Fixture audio used instead of real mic
    """
    audio_5s = benchmark_audio_fixtures["5s"]

    def run_dictation_cycle():
        """Execute one complete dictation cycle."""
        start_time = time.time()

        # Trigger hotkey
        app.hotkey_manager.activated.emit()

        # Wait for LISTENING
        qtbot.waitUntil(lambda: app.state_machine.listening_state.active(), timeout=1000)

        # Simulate speech end (inject fixture audio directly)
        app.state_machine.on_speech_ended(audio_5s.tobytes())

        # Wait for return to IDLE (full cycle complete)
        qtbot.waitUntil(lambda: app.state_machine.idle_state.active(), timeout=5000)

        end_time = time.time()
        return (end_time - start_time) * 1000  # Convert to ms

    # Run benchmark
    latencies = [run_dictation_cycle() for _ in range(5)]  # 5 samples

    # Calculate statistics
    mean_latency = np.mean(latencies)
    p95_latency = np.percentile(latencies, 95)
    p99_latency = np.percentile(latencies, 99)

    print(f"\n=== End-to-End Latency Benchmark ===")
    print(f"Mean: {mean_latency:.0f}ms")
    print(f"P95:  {p95_latency:.0f}ms")
    print(f"P99:  {p99_latency:.0f}ms")
    print(f"Target: <1000ms (MVP), <500ms (goal)")

    # Assert MVP target
    assert p95_latency < 1000, f"P95 latency {p95_latency:.0f}ms exceeds MVP target 1000ms"
```

**Running Benchmarks:**

```bash
# Run benchmarks with detailed statistics
pytest tests/integration/benchmark_latency.py -v --benchmark-only

# Generate benchmark report
pytest tests/integration/benchmark_latency.py --benchmark-json=benchmark_results.json

# Compare with previous run
pytest-benchmark compare benchmark_results.json
```

---

## Test Fixtures and Data

**Audio Fixtures:**

```
tests/fixtures/audio/
├── speech_2s.npy          # 2-second speech sample (16kHz mono)
├── speech_5s.npy          # 5-second speech sample (typical)
├── speech_10s.npy         # 10-second speech sample (edge case)
├── silence_2s.npy         # 2 seconds of silence (for VAD testing)
├── noise_2s.npy           # 2 seconds of background noise
└── accented_speech_5s.npy # Non-US accent (diversity testing)
```

**Configuration Fixtures:**

```
tests/fixtures/configs/
├── minimal_config.json    # Minimum required config
├── full_config.json       # All options specified
├── invalid_config.json    # For validation testing
└── gpu_disabled.json      # CPU fallback mode
```

**Creating Fixtures:**

```python
# tests/fixtures/create_audio_fixtures.py

import numpy as np
import sounddevice as sd

def record_fixture_audio(duration_seconds: int, output_path: str):
    """Record audio fixture from microphone."""
    print(f"Recording {duration_seconds}s... Speak now!")

    sample_rate = 16000
    audio = sd.rec(
        int(duration_seconds * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()

    np.save(output_path, audio)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    record_fixture_audio(5, "tests/fixtures/audio/speech_5s.npy")
```

---

## CI/CD Pipeline

**GitHub Actions Workflow (`.github/workflows/ci.yaml`):**

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            portaudio19-dev \
            python3-pyqt5 \
            python3-dbus \
            xvfb  # Virtual X server for PyQt5 tests

      - name: Install Python dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt -r requirements-dev.txt

      - name: Run linting (ruff)
        run: ruff check src/ tests/

      - name: Run code formatting check (black)
        run: black --check src/ tests/

      - name: Run type checking (mypy)
        run: mypy src/ --strict

      - name: Run unit tests with coverage
        run: |
          # Run with virtual X display for PyQt5
          xvfb-run pytest tests/unit/ \
            --cov=src \
            --cov-report=term-missing \
            --cov-report=xml \
            --cov-fail-under=60

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  lint-commits:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Check commit messages
        run: |
          # Enforce conventional commits format
          git log --format=%s origin/main..HEAD | \
            grep -E '^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+$' || \
            (echo "Commit messages must follow conventional commits format" && exit 1)
```

**Pre-commit Hook (`.pre-commit-config.yaml`):**

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.285
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--strict]
```

---

## Manual Testing Procedures

**Cross-Desktop Environment Testing:**

| Desktop Environment | Test Location | Tester | Frequency |
|---------------------|---------------|--------|-----------|
| **GNOME 45** | Developer primary system | Developer | Every commit |
| **KDE Plasma 5.27** | VM or secondary system | Developer | Before merge to main |
| **Hyprland 0.30** | Community tester | Community | Before release |
| **Sway 1.8** | Community tester | Community | Before release |

**Manual Test Checklist (Before Release):**

```markdown
# Pre-Release Testing Checklist

## Functional Tests
- [ ] Hotkey activation works
- [ ] System tray icon appears and updates states correctly
- [ ] Settings window opens and saves changes
- [ ] History viewer displays sessions correctly
- [ ] Audio indicator shows levels during capture
- [ ] Model download works (delete model and re-download)
- [ ] CPU fallback mode works (disable CUDA in config)
- [ ] Wayland text injection works (GNOME/KDE)
- [ ] Clipboard fallback works (Hyprland/Sway)

## Performance Tests
- [ ] Latency <1000ms for 5s audio (base model, RTX 4060)
- [ ] UI remains responsive during transcription
- [ ] No memory leaks after 50 dictation cycles
- [ ] Application starts in <5s (with model already downloaded)

## Edge Cases
- [ ] Dictation works with background noise
- [ ] Handles microphone disconnect gracefully
- [ ] Recovers from CUDA out of memory error
- [ ] Handles extremely long dictation (30s+)
- [ ] Works with different audio devices
- [ ] Handles rapid hotkey presses (double-press)

## Cross-DE Tests
- [ ] GNOME: Global hotkey, system tray, text injection
- [ ] KDE: Global hotkey, system tray, text injection
- [ ] Hyprland: Clipboard fallback, tray (if supported)
- [ ] Sway: Clipboard fallback, tray (if supported)

## Compatibility Tests (Target Applications)
- [ ] Claude Code (VS Code variant)
- [ ] GNOME Terminal
- [ ] Firefox
- [ ] Chromium
- [ ] LibreOffice Writer
- [ ] Slack (Electron app)
```

---

## Test Coverage Goals

**Current Coverage (tracked by Codecov):**

| Module | Target Coverage | Critical Paths |
|--------|----------------|----------------|
| `src/audio/` | 70%+ | Audio callback, VAD integration, buffer management |
| `src/transcription/` | 60%+ | Whisper inference, model loading, error handling |
| `src/wayland/` | 60%+ | Text injection strategies, fallback logic |
| `src/ui/` | 50%+ | Signal connections, user interactions (hard to test) |
| `src/core/` | 80%+ | State machine transitions, config validation, history |
| `src/utils/` | 80%+ | Logging, error handling, notifications |
| **Overall** | **60%+** | All critical paths covered |

**Exclusions from Coverage:**

- `src/__main__.py` (entry point, manually tested)
- `if __name__ == "__main__":` blocks
- Qt UI event handlers (require manual testing)
- Platform-specific D-Bus code (mocked in unit tests, manually tested on target DEs)

---

## Testing Anti-Patterns to Avoid

❌ **Don't test implementation details:**
```python
# BAD: Testing internal state
def test_audio_capture_internal_state():
    audio = AudioCapture(config, vad)
    assert audio._internal_buffer is not None  # Fragile

# GOOD: Testing behavior
def test_audio_capture_emits_signal():
    audio = AudioCapture(config, vad)
    spy = QSignalSpy(audio.speechDetected)
    audio.start_capture()
    assert len(spy) > 0  # Tests observable behavior
```

❌ **Don't write flaky tests:**
```python
# BAD: Timing-dependent test
def test_transcription_completes():
    engine.transcribe_async(audio)
    time.sleep(0.5)  # Hope it's done?
    assert result is not None  # Flaky!

# GOOD: Wait for signal
def test_transcription_completes(qtbot):
    spy = QSignalSpy(engine.transcriptionComplete)
    engine.transcribe_async(audio)
    qtbot.waitUntil(lambda: len(spy) > 0, timeout=2000)  # Explicit wait
    assert spy[0][0].was_successful()
```

❌ **Don't skip tests:**
```python
# BAD: Skipping tests that should pass
@pytest.mark.skip(reason="Broken, will fix later")
def test_important_feature():
    ...

# GOOD: Fix or mark as xfail with issue link
@pytest.mark.xfail(reason="Known issue #123, fix in progress")
def test_important_feature():
    ...
```

---
