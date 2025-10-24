# Tech Stack

The technology stack for Fedora Voice Dictation is carefully selected to achieve **<500ms latency**, **100% offline operation**, and **cross-DE compatibility** while maintaining development velocity and code quality.

**⚠️ CRITICAL DISK SPACE REQUIREMENT: ~6GB+**
- PyTorch + CUDA: ~2GB
- Whisper models: 150MB - 3GB (depending on model size)
- Dependencies: ~1GB
- Application + cache: ~500MB

**Version Pinning Strategy:**
- **Major.minor pinning** for critical dependencies (PyQt5 ~=5.15.0, torch ~=2.0.0) allows patch updates
- **Exact versions** in requirements.txt lock file for reproducible builds
- **Quarterly dependency audits** to update pinned versions and address CVEs
- **CI/CD enforcement** of linting, type checking, formatting (see CI/CD Enforcement below)

---

## Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| **Language** | Python (CPython) | 3.10-3.12 (developed on 3.11) | Application runtime, all application logic | Rapid development, rich ecosystem (PyTorch, PyQt5), official Whisper support. GIL releases during CUDA/audio operations enable parallelism. 3.10+ required for match statements and better type hints. Tested on 3.10, 3.11, 3.12. |
| **UI Framework** | PyQt5 | 5.15.9+ (or system python3-qt5) | GUI toolkit (system tray, settings, dialogs) | Most mature Qt bindings for Python. Proven StatusNotifierItem support across DEs. Better documentation than PyQt6/PySide. Thread-safe signals/slots critical for architecture. **Hybrid install:** System package preferred, pip fallback. |
| **GPU Acceleration** | NVIDIA CUDA Toolkit | 12.1+ (11.8 minimum) | GPU compute for Whisper inference | Required for PyTorch GPU support. 12.x recommended for RTX 4060 Ada Lovelace architecture. See CUDA Compatibility Matrix below. |
| **ML Framework** | PyTorch | 2.0+ with CUDA 12.x | Whisper model execution, tensor operations | Whisper's native framework. Releases GIL during CUDA operations (critical for threading). Extensive CUDA optimization. Version 2.0+ required for better compilation. **Use cu121 wheel for CUDA 12.x** (see installation). |
| **Speech Recognition** | openai-whisper | 20231117 (exact) | Whisper model integration, transcription | Official OpenAI implementation. CUDA-optimized. **NOTE:** Last updated Nov 2023. **Decision gate Week 1-2:** Migrate to whisper.cpp or faster-whisper if latency insufficient or bugs found. |
| **Audio Capture** | sounddevice | 0.4.6+ | Real-time microphone input via PortAudio | Wayland-compatible. Releases GIL during audio callbacks. Simple API. Supports device enumeration. **Requires system portaudio library.** |
| **Audio Backend** | PortAudio | 19.7.1+ (Fedora system package) | Cross-platform audio I/O (sounddevice dependency) | PulseAudio and PipeWire support. Low-latency capture. **System dependency:** `dnf install portaudio-devel` required before pip install sounddevice. |
| **Voice Activity Detection** | silero-vad | 4.0+ | Neural network-based speech detection | More accurate than webrtcvad (95% vs 85%). PyTorch-based (shares CUDA context). Model auto-downloaded (~10MB) to ~/.cache/torch/hub/. |
| **Wayland Protocols** | pywayland | 0.4.14+ | Python bindings for Wayland client protocol | Native text-input-unstable-v3 support. Window focus tracking. No X11 dependencies. **Requires system wayland-devel for compilation.** |
| **Clipboard Access** | pyperclip | 1.8.2+ | Clipboard read/write fallback | Cross-platform clipboard API. Wayland via wl-clipboard. Used when Wayland text injection fails. |
| **D-Bus Integration** | dbus-python | 1.3.2+ (Fedora python3-dbus preferred) | System notifications, system tray, hotkeys | Native D-Bus bindings. **Use system package** to avoid compilation: `dnf install python3-dbus`. |
| **Configuration Storage** | Python stdlib json | Stdlib (3.10+) | JSON config file read/write | No external dependency. Human-readable. Atomic writes via temp+rename. Stored in ~/.config/fedora-voice-dictation/config.json. |
| **History Storage (MVP)** | Python stdlib json | Stdlib (3.10+) | Session history persistence | Simple JSON array in ~/.local/share/fedora-voice-dictation/history.json. **Phase 2:** Migrate to SQLite for queries/analytics. |
| **Logging** | Python stdlib logging | Stdlib (3.10+) | Application logging with rotation | RotatingFileHandler (7-day retention, 10MB max). Configurable log levels. No external dependency. |
| **Whisper Models** | OpenAI Whisper models | base: 150MB, medium: 1.5GB, large: 3GB | Pre-trained speech models | **Downloaded on first run** to ~/.local/share/fedora-voice-dictation/models/ (overrides openai-whisper default ~/.cache/whisper/). Auto-download with progress UI. |
| **VAD Model** | silero-vad model | ~10MB | Pre-trained VAD model | Auto-downloaded to ~/.cache/torch/hub/snakers4_silero-vad/ on first use. |
| **FFmpeg** | ffmpeg (system package) | Latest stable | Audio preprocessing (openai-whisper dependency) | **System dependency:** `dnf install ffmpeg` (from RPM Fusion free). Required for openai-whisper audio decoding. |
| **Testing Framework** | pytest | 7.4+ | Unit and integration testing | Industry standard. pytest-qt plugin for PyQt5 testing. pytest-mock for mocking. Parameterized tests. **CI/CD enforced:** All tests must pass. |
| **Qt Testing** | pytest-qt | 4.2+ | PyQt5 component testing | QTest integration. Signal/slot testing. Event simulation. |
| **Type Checking** | mypy | 1.5+ | Static type analysis | Catches type errors before runtime. **CI/CD enforced:** Strict mode, all type hints required. |
| **Code Formatting** | black | 23.7+ | Automatic code formatting | Opinionated formatter. **CI/CD enforced:** Code must be formatted (check-only in CI, no auto-format). |
| **Linting** | ruff | 0.0.285+ | Fast Python linter (replaces flake8, isort) | 10-100x faster than alternatives. **CI/CD enforced:** All rules must pass. |
| **Build Tool** | pip + setuptools | Latest stable | Python package building | Standard Python packaging. Produces wheel for RPM. pyproject.toml (PEP 517/518). |
| **Package Manager** | pip | Latest stable | Dependency installation | Fedora default. Works with requirements.txt. |
| **Packaging (Fedora)** | rpmbuild + mock | Latest stable | RPM package creation | Fedora-native packaging. Mock provides clean build environment. |
| **CI/CD** | GitHub Actions | N/A (SaaS) | Automated testing, linting, releases | Free for public repos. Ubuntu runners for CI. **No GPU testing** (manual on dev system). |
| **Version Control** | Git | 2.40+ | Source code management | Industry standard. GitHub integration. |
| **Documentation** | Markdown | N/A | All documentation | Simple, readable, GitHub-native. No Sphinx overhead for MVP. |

---

## CUDA + PyTorch Compatibility Matrix

**CRITICAL:** PyTorch CUDA wheel MUST match your installed CUDA version.

| NVIDIA Driver | CUDA Toolkit | PyTorch Wheel | Fedora Version | Status |
|---------------|--------------|---------------|----------------|--------|
| 515+ | 11.8 | `torch==2.0.1+cu118` | Fedora 38 | ✅ Minimum supported |
| 520+ | 12.0 | `torch==2.0.1+cu118` OR `+cu121` | Fedora 39 | ✅ Either wheel works |
| 535+ | 12.1 | `torch==2.0.1+cu121` | Fedora 40 | ✅ **Recommended** |
| 550+ | 12.3 | `torch==2.0.1+cu121` | Fedora 41 | ✅ Use cu121 wheel |

**How to Detect Your CUDA Version:**

```bash
# Check installed CUDA toolkit version
nvcc --version
# Example output: "Cuda compilation tools, release 12.1, V12.1.105"

# Check NVIDIA driver version and supported CUDA
nvidia-smi
# Look for "CUDA Version: 12.1" in top right

# Determine correct PyTorch wheel
python3 -c "import subprocess; v = subprocess.check_output(['nvcc', '--version']).decode(); print('Use: torch+cu121' if '12.' in v else 'Use: torch+cu118')"
```

**Installation Based on CUDA Version:**

```bash
# For CUDA 12.x (Fedora 40+):
pip install torch==2.0.1+cu121 -f https://download.pytorch.org/whl/torch_stable.html

# For CUDA 11.8 (Fedora 38-39):
pip install torch==2.0.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html
```

**⚠️ WARNING:** Using wrong wheel causes runtime error:
```
RuntimeError: CUDA mismatch: PyTorch compiled with CUDA 11.8 but system has CUDA 12.1
```

---

## Critical Dependencies Detail

**1. PyQt5 vs PyQt6 vs PySide6 - Decision: PyQt5 5.15.x**

| Consideration | PyQt5 (Chosen) | PyQt6 | PySide6 |
|---------------|----------------|-------|---------|
| **StatusNotifierItem Support** | Excellent | Limited | Limited |
| **Cross-DE Compatibility** | Proven (GNOME, KDE, Hyprland, Sway) | Untested on tiling WMs | Untested on tiling WMs |
| **Documentation** | Extensive | Moderate | Moderate |
| **License** | GPL or Commercial | GPL or Commercial | LGPL (more permissive) |
| **Fedora System Package** | ✅ python3-qt5 available | ❌ Not in repos | ❌ Not in repos |
| **Signal/Slot Performance** | Mature | Slightly improved | Similar to PyQt6 |

**Rationale:** PyQt5 is battle-tested for system tray across all target DEs. PyQt6/PySide6 improvements don't justify migration risk for MVP. **Recommended:** Use Fedora system package when possible.

---

**2. openai-whisper vs whisper.cpp vs faster-whisper**

**Decision: openai-whisper for MVP, with STRONG fallback plan**

| Consideration | openai-whisper (MVP) | whisper.cpp (Fallback) | faster-whisper (Alternative) |
|---------------|----------------------|------------------------|------------------------------|
| **Language** | Pure Python | C++ with Python bindings | Python (ctranslate2 backend) |
| **Latency (base model, RTX 4060)** | 500-800ms (estimated) | 300-500ms (benchmarked) | 400-600ms (benchmarked) |
| **Development Speed** | Fast (pip install) | Slower (build dependencies) | Fast (pip install) |
| **CUDA Support** | Via PyTorch | Via cuBLAS, cuDNN | Via ctranslate2 (CUDA) |
| **Maintenance Status** | ⚠️ **Last update Nov 2023** | ✅ **Active (weekly updates)** | ✅ **Active (monthly updates)** |
| **Model Compatibility** | Official models | Same models | Same models |

**⚠️ CRITICAL CONCERN:** openai-whisper hasn't been updated in 2 years (as of Oct 2025). Project may be abandoned.

**Decision Gate (Week 1-2):**
- ✅ **openai-whisper GO:** If p95 latency <1000ms AND no critical bugs → Proceed
- ⚠️ **faster-whisper PIVOT:** If openai-whisper has bugs but latency OK → Use faster-whisper (drop-in replacement, 2x faster)
- ❌ **whisper.cpp PIVOT:** If p95 latency >1500ms → Migrate to whisper.cpp

**Migration Path (faster-whisper):** Easiest, replace `import whisper` with `from faster_whisper import WhisperModel`, minimal code changes.

**Migration Path (whisper.cpp):** Replace `src/transcription/whisper_engine.py`, use `pywhispercpp` bindings, ~1 week integration.

---

**3. silero-vad vs webrtcvad - Decision: silero-vad 4.0+**

| Consideration | silero-vad (Chosen) | webrtcvad |
|---------------|---------------------|-----------|
| **Accuracy** | ~95% (neural network) | ~85% (heuristic) |
| **False Positive Rate** | 5% | 15% |
| **Latency** | ~50ms (PyTorch inference) | ~10ms (C code) |
| **CUDA Sharing** | ✅ Yes (PyTorch model, shares context) | ❌ No (CPU only) |
| **Sample Rate** | 8kHz, 16kHz | 8kHz, 16kHz, 32kHz, 48kHz |
| **Model Size** | ~10MB (auto-download) | None (algorithm-based) |

**Rationale:** 10% accuracy improvement worth 40ms latency increase. False transcriptions waste GPU cycles (more costly than VAD latency). Shares CUDA context with Whisper (no context switch overhead).

---

**4. System Packages vs pip (Hybrid Approach) - RECOMMENDED**

**Best Practice:** Use Fedora system packages where available, pip for the rest.

| Package | System Package | pip Install | Recommendation |
|---------|----------------|-------------|----------------|
| **PyQt5** | `python3-qt5` | `pip install PyQt5` | ✅ **Use system package** (no compilation, version-tested) |
| **dbus-python** | `python3-dbus` | `pip install dbus-python` | ✅ **Use system package** (avoids dbus-devel compilation) |
| **pytest** | `python3-pytest` | `pip install pytest` | ⚠️ **Either** (system version may lag) |
| **PyTorch** | ❌ Not available with CUDA | `pip install torch+cu121` | ❌ **Must use pip** (CUDA wheels not in Fedora repos) |
| **openai-whisper** | ❌ Not packaged | `pip install openai-whisper` | ❌ **Must use pip** |
| **sounddevice** | ❌ Not packaged | `pip install sounddevice` | ❌ **Must use pip** |
| **pywayland** | `python3-pywayland` | `pip install pywayland` | ✅ **Use system package** (avoids wayland-devel compilation) |

**Hybrid Installation (Recommended for Development):**

```bash
# 1. Install system packages first
sudo dnf install python3-qt5 python3-dbus python3-pywayland

# 2. Create venv with system site-packages access
python3 -m venv --system-site-packages venv
source venv/bin/activate

# 3. Install pip-only dependencies
pip install torch==2.0.1+cu121 openai-whisper==20231117 sounddevice
```

---

## Dependency Installation (Correct Order)

**⚠️ CRITICAL: Install system dependencies BEFORE Python packages to avoid compilation errors.**

**Step 1: System Dependencies (Fedora)**

```bash
# NVIDIA driver + CUDA toolkit (RPM Fusion)
sudo dnf install nvidia-driver cuda-toolkit

# Audio system (usually pre-installed on Fedora)
sudo dnf install pipewire pipewire-pulseaudio  # Or pulseaudio

# Compilation dependencies for pip packages
sudo dnf install portaudio-devel  # For sounddevice
sudo dnf install wayland-devel wayland-protocols-devel  # For pywayland
sudo dnf install python3-devel  # Python headers

# FFmpeg (openai-whisper dependency, from RPM Fusion Free)
sudo dnf install ffmpeg

# Python system packages (optional but recommended)
sudo dnf install python3-qt5 python3-dbus python3-pywayland python3-pytest
```

**Step 2: Python Virtual Environment**

```bash
# Create venv with system site-packages (accesses system PyQt5, dbus-python)
python3 -m venv --system-site-packages venv
source venv/bin/activate

# Verify Python version
python --version  # Should be 3.10+
```

**Step 3: Detect CUDA Version and Install PyTorch**

```bash
# Detect CUDA version
nvcc --version | grep release

# For CUDA 12.x (Fedora 40+):
pip install torch==2.0.1+cu121 -f https://download.pytorch.org/whl/torch_stable.html

# For CUDA 11.8 (Fedora 38-39):
pip install torch==2.0.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html

# Verify PyTorch GPU support
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
# Should print: CUDA available: True
```

**Step 4: Install Application Dependencies**

```bash
# Install from requirements.txt (excludes torch, installed above)
pip install -r requirements.txt

# Or install individually:
pip install openai-whisper==20231117
pip install sounddevice==0.4.6
pip install silero-vad==4.0.1
pip install pyperclip==1.8.2
# (Skip PyQt5, dbus-python, pywayland if using system packages)
```

**Step 5: Verify Installation**

```bash
# Check all critical imports
python3 << 'EOF'
import torch
print(f"PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}")

import whisper
print(f"Whisper: {whisper.__version__}")

import sounddevice as sd
print(f"Sounddevice: {sd.__version__}, Devices: {len(sd.query_devices())}")

from PyQt5.QtWidgets import QApplication
print("PyQt5: OK")

import dbus
print("D-Bus: OK")

print("\n✅ All dependencies installed successfully!")
EOF
```

---

## Runtime Dependencies (requirements.txt)

```txt
# Core Application - UI & Event Loop
PyQt5==5.15.9  # Omit if using system python3-qt5
PyQt5-sip==12.12.2  # Required by PyQt5

# Audio Processing
sounddevice==0.4.6
numpy==1.24.3  # sounddevice + audio preprocessing dependency

# Speech Recognition & ML
# NOTE: torch installed separately (see installation instructions above)
# torch==2.0.1+cu121  # CUDA 12.x - installed via separate command
# torch==2.0.1+cu118  # CUDA 11.8 - alternative
openai-whisper==20231117  # Exact version (date-based)
tiktoken==0.5.1  # openai-whisper dependency (Rust compilation)
numba==0.58.0  # openai-whisper dependency (LLVM, large package)

# Voice Activity Detection
silero-vad==4.0.1

# Wayland Integration
pywayland==0.4.14  # Omit if using system python3-pywayland
pyperclip==1.8.2  # Clipboard fallback

# D-Bus Integration
dbus-python==1.3.2  # Omit if using system python3-dbus

# No dependencies for: json, logging (stdlib)
```

---

## Development Dependencies (requirements-dev.txt)

```txt
# Testing
pytest==7.4.2
pytest-qt==4.2.0  # PyQt5 testing
pytest-mock==3.11.1  # Mocking
pytest-cov==4.1.0  # Coverage reporting

# Type Checking & Linting
mypy==1.5.1  # Static type checking (strict mode in CI/CD)
ruff==0.0.285  # Fast linter (replaces flake8, isort)

# Code Formatting
black==23.7.0  # Automatic formatting (enforced in CI/CD)

# Development Tools
ipython==8.14.0  # Interactive debugging
```

---

## CI/CD Enforcement

**GitHub Actions Pipeline (`.github/workflows/ci.yaml`):**

| Tool | Enforcement | Failure = Block Merge | Configuration |
|------|-------------|----------------------|---------------|
| **pytest** | ✅ All tests must pass | ✅ Yes | 60%+ code coverage required |
| **mypy** | ✅ Strict type checking | ✅ Yes | `--strict` mode, all files |
| **ruff** | ✅ All linting rules | ✅ Yes | Default rules + import sorting |
| **black** | ✅ Code formatting check | ✅ Yes | `--check` (no auto-format in CI) |

**Local Development Workflow:**

```bash
# Before committing:
black .                          # Auto-format code
ruff check --fix .               # Auto-fix linting issues
mypy src/                        # Type check
pytest tests/ --cov=src --cov-report=term-missing  # Run tests with coverage

# Or use pre-commit hook (optional):
pip install pre-commit
pre-commit install
# Runs black, ruff, mypy on git commit
```

---

## Technology Alternatives Considered

| Technology | Alternative | Why Rejected |
|------------|-------------|--------------|
| **PyQt5** | Tkinter | No system tray support on Wayland, looks outdated, limited theming |
| **PyQt5** | GTK3 via PyGObject | GNOME-specific, poor KDE integration, weaker signal/slot equivalents |
| **Python** | Rust | Steep learning curve, longer dev time, Whisper integration harder, no GPU performance benefit (both use CUDA) |
| **Python** | C++ | No official Whisper bindings, complex build, slower iteration. Consider for Phase 2 if performance insufficient. |
| **openai-whisper** | Vosk | Lower accuracy (~20% WER vs 10%), no GPU acceleration, smaller models |
| **openai-whisper** | Coqui STT | Discontinued project (2023), no active maintenance |
| **sounddevice** | PyAudio | Unmaintained since 2017, poor Wayland support, lacks device hotplug detection |
| **JSON config** | TOML | Requires external library (tomli for Python <3.11), JSON stdlib sufficient, atomicity easier with JSON |
| **JSON history (MVP)** | SQLite from start | Over-engineering for MVP append-only log. SQLite in Phase 2 when queries needed. |
| **pytest** | unittest (stdlib) | Less readable, more verbose, weaker parametrization. pytest is industry standard. |
| **Fedora** | Ubuntu 22.04 LTS | Slower Wayland adoption, X11 default on some configs. Deferred to Phase 2 (PPA distribution). |
| **NVIDIA CUDA** | AMD ROCm | Higher integration complexity, less mature PyTorch support. Deferred to Phase 2. |

---

## Dependency Update Strategy

**Quarterly Dependency Review (Every 3 months):**

1. **Security Audit:**
   ```bash
   pip install pip-audit
   pip-audit  # Check for CVEs in dependencies
   ```

2. **Check for Updates:**
   ```bash
   pip list --outdated  # Show available updates
   ```

3. **Update and Test:**
   ```bash
   # Update specific package
   pip install --upgrade openai-whisper

   # Run full test suite
   pytest tests/

   # Benchmark performance (ensure no regressions)
   pytest tests/integration/benchmark_latency.py

   # Update requirements.txt
   pip freeze > requirements.txt
   ```

4. **Review Changelogs:**
   - PyQt5: Check for Qt upstream changes
   - PyTorch: Check CUDA compatibility matrix
   - openai-whisper: Check if project resumed development (currently stale)

**Dependabot Configuration (`.github/dependabot.yml`):**

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "monthly"
    open-pull-requests-limit: 5
    reviewers:
      - "project-maintainer"
```

---

## RPM Packaging Dependencies

**RPM Spec File (`packaging/fedora/fedora-voice-dictation.spec`):**

```spec
# Runtime requirements (system packages)
Requires: python3 >= 3.10
Requires: python3-qt5
Requires: python3-dbus
Requires: python3-pywayland
Requires: portaudio
Requires: pipewire-pulseaudio
Requires: ffmpeg

# NVIDIA dependencies (recommended, not required - CPU fallback exists)
Recommends: nvidia-driver >= 535
Recommends: cuda-toolkit >= 12.0

# Build requirements
BuildRequires: python3-devel
BuildRequires: python3-setuptools
BuildRequires: python3-wheel

# Python dependencies bundled in RPM site-packages
# (PyTorch, openai-whisper, sounddevice, etc. installed via pip during build)
```

**Note:** RPM bundles all pip dependencies in `/usr/lib/python3.11/site-packages/`. No venv used in system-wide RPM installation.

---

## Future: Flatpak Distribution (Phase 2)

**Benefits:**
- Broader distribution (works on any Linux distro, not just Fedora)
- Bundled CUDA runtime (no system NVIDIA driver dependency confusion)
- Sandboxed environment (security)
- Automatic updates via Flathub

**Challenges:**
- GPU passthrough requires special permissions
- Larger download size (~2GB with all dependencies)
- Flatpak portal integration for Wayland text injection

**Target Timeline:** Post-MVP, after Fedora RPM validation complete.

---
