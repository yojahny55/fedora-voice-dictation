# Goals and Background Context

## Goals

- Launch a functional MVP within 3 months that demonstrates core voice dictation capability on Wayland with GPU acceleration
- Achieve 100% offline operation with no cloud dependencies, establishing privacy and independence as foundational attributes
- Deliver transcription latency under 500ms (from speech end to text appearance) for professional workflows
- Successfully integrate with 3 target applications (Claude Code, terminal, and one additional text application) to validate Wayland protocol implementation
- Build an active early adopter community of 25-50 users within 6 months for feedback and validation
- Establish open-source presence through GitHub with clear documentation enabling community contributions

## Background Context

Developers and power users on Fedora Linux running Wayland face a critical productivity barrier: there is no voice dictation solution that works natively on Wayland while respecting privacy and delivering the performance needed for modern workflows. Existing solutions either require cloud connectivity (creating privacy concerns), rely on X11 compatibility layers (introducing latency and defeating the purpose of Wayland), or lack the speed necessary for professional use cases like LLM prompting in Claude Code and terminal command dictation.

Fedora Voice Dictation solves this problem by combining OpenAI's Whisper speech recognition with GPU acceleration (optimized for NVIDIA RTX GPUs) and native Wayland integration. Running entirely on the user's local machine, the application delivers near-instant transcription without any cloud dependencies, enabling fast, privacy-focused speech-to-text conversion for power users who value performance, privacy, and local-first computing.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-21 | v1.0 | Initial PRD creation from Project Brief | John (PM) |

---
