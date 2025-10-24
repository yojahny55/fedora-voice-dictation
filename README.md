# Fedora Voice Dictation

**Offline, low-latency voice-to-text dictation for Fedora Linux with Wayland support**

## Overview

Fedora Voice Dictation is a native Linux application that enables fast, accurate voice-to-text transcription directly into any application. Built specifically for Fedora Linux with first-class Wayland support, it runs 100% offline using OpenAI's Whisper speech recognition model with GPU acceleration.

**Key Features:**
- **100% Offline:** All processing happens locally - no internet required after initial setup
- **Low Latency:** Target <500ms transcription time with GPU acceleration
- **Wayland Native:** First-class support for GNOME, KDE Plasma, and tiling window managers
- **GPU Accelerated:** NVIDIA CUDA support for fast inference (CPU fallback available)
- **System Tray Integration:** Unobtrusive background operation with quick access controls
- **Privacy Focused:** Your voice data never leaves your machine

## System Requirements

- **Operating System:** Fedora 40+ (or compatible Linux with Wayland)
- **Python:** 3.10 or higher (developed on Python 3.11)
- **GPU (Recommended):** NVIDIA GPU with CUDA 12.x support
  - Minimum: GTX 1060 or equivalent (6GB VRAM)
  - Recommended: RTX 4060 or newer for best performance
- **CPU Fallback:** Intel Core i5-8th gen or AMD Ryzen 5 2600 (slower, 2-5s latency)
- **RAM:** 8GB minimum, 16GB recommended
- **Disk Space:** ~6GB for dependencies and models

## Installation

### Step 1: Install System Dependencies

```bash
# NVIDIA driver + CUDA toolkit (from RPM Fusion)
sudo dnf install nvidia-driver cuda-toolkit

# Audio system (usually pre-installed on Fedora)
sudo dnf install pipewire pipewire-pulseaudio

# Development dependencies for Python packages
sudo dnf install portaudio-devel wayland-devel wayland-protocols-devel python3-devel

# FFmpeg (required by Whisper, from RPM Fusion Free)
sudo dnf install ffmpeg

# Python system packages (optional but recommended)
sudo dnf install python3-qt5 python3-dbus python3-pywayland python3-pytest
```

### Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/fedora-voice-dictation.git
cd fedora-voice-dictation
```

### Step 3: Create Virtual Environment

Create a virtual environment with access to system packages (PyQt5, dbus):

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

### Step 4: Install PyTorch with CUDA

Detect your CUDA version and install the matching PyTorch wheel:

```bash
# Check CUDA version
nvcc --version | grep release

# For CUDA 12.x (Fedora 40+):
pip install torch==2.0.1+cu121 -f https://download.pytorch.org/whl/torch_stable.html

# For CUDA 11.8 (Fedora 38-39):
pip install torch==2.0.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html

# Verify CUDA is available:
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Step 5: Install Python Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### Step 6: Install in Development Mode

```bash
pip install -e .
```

### Step 7: Verify Installation

```bash
python -m src --version
```

## Development Setup

### Running Tests

```bash
# Run all unit tests
pytest tests/unit/

# Run tests with coverage
pytest tests/unit/ --cov=src --cov-report=term-missing

# Run tests with PyQt5 (requires xvfb on headless systems)
xvfb-run pytest tests/unit/
```

### Code Quality Checks

```bash
# Auto-format code
black src/ tests/

# Lint code
ruff check src/ tests/ --fix

# Type checking
mypy src/ --strict
```

### Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

This will automatically run black, ruff, and mypy on git commit.

## Usage

*Coming soon - application is under active development*

## Project Status

**Current Phase:** MVP Development (Story 1.1 - Project Setup)

See [docs/stories/](docs/stories/) for current development status and upcoming features.

## Architecture

This project follows a modular architecture with clear separation of concerns:

- `src/audio/` - Audio capture and Voice Activity Detection
- `src/transcription/` - Whisper model integration and inference
- `src/wayland/` - Wayland protocol integration for text injection
- `src/ui/` - PyQt5 GUI components (system tray, settings)
- `src/core/` - State machine, configuration, and history management
- `src/utils/` - Logging, error handling, and utilities

See [docs/architecture/](docs/architecture/) for detailed architecture documentation.

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `pytest tests/`
2. Code is formatted: `black .`
3. Linting passes: `ruff check .`
4. Type checking passes: `mypy src/`
5. Test coverage ≥60%

## License

*License to be determined - see LICENSE file*

## Acknowledgments

- **OpenAI Whisper** - Speech recognition model
- **silero-vad** - Voice Activity Detection
- **PyQt5** - GUI framework
- **PyTorch** - Machine learning framework
