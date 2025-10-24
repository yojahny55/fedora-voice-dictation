# Project Brief: Fedora Voice Dictation

---

## Executive Summary

Fedora Voice Dictation is a Wayland-native voice dictation application that enables fast, privacy-focused speech-to-text conversion for power users. Built on OpenAI's Whisper running entirely locally, the app leverages GPU acceleration (optimized for NVIDIA RTX 4060 and modern NVIDIA GPUs) to deliver near-instant transcription while maintaining strong accuracy. The application is particularly well-suited for LLM prompting workflows in Claude Code, terminal command dictation, and code development where rapid input matters.

**Primary Problem:** Developers and power users on Fedora/Wayland systems lack a fast, privacy-respecting voice dictation tool that works seamlessly with modern desktop environments and target applications like Claude Code and terminal emulators. Existing solutions either require cloud connectivity (privacy concerns), don't work well on Wayland (X11 dependencies), or lack the performance needed for professional workflows.

**Target Market:** Individual power users, developers, and terminal-focused professionals running Fedora with modern NVIDIA GPU hardware who value privacy, performance, and local-first computing.

**Key Value Proposition:** 100% offline operation with GPU-accelerated transcription, Wayland-native integration without X11 fallbacks, and a performance-optimized architecture that delivers fast, accurate results for professional workflows—including LLM prompting in Claude Code, terminal commands, and code dictation.

---

## Problem Statement

**Current State & Pain Points:**

Power users and developers on Fedora Linux face a significant productivity barrier: there is no voice dictation solution that works natively on Wayland while respecting privacy and delivering the performance needed for modern workflows. This forces users into uncomfortable compromises:

- **Abandoning voice input entirely**, manually typing long prompts for LLM tools like Claude Code, which slows down ideation and exploration
- **Using cloud-based solutions** that send voice data to third parties, creating privacy concerns and requiring constant internet connectivity
- **Relying on X11 compatibility layers** (XWayland) with legacy dictation tools, which introduces latency, compatibility issues, and defeats the purpose of running a modern Wayland desktop
- **Accepting slow, accuracy-focused tools** that introduce multi-second delays between speaking and seeing results, breaking flow state

**Impact of the Problem:**

The lack of a suitable solution directly impacts productivity and workflow quality:

- **Time loss:** Developers spend unnecessary time typing complex technical prompts, terminal commands, and code snippets that could be dictated in seconds
- **Reduced LLM exploration:** Longer input times discourage experimentation with LLMs, limiting the iterative exploration that makes these tools valuable
- **Privacy compromise:** Users who prioritize voice input must choose between productivity and privacy when using cloud services
- **Desktop environment limitations:** Users can't fully embrace Wayland and must maintain X11 compatibility for basic functionality

**Why Existing Solutions Fall Short:**

Current voice dictation options fail to meet power user needs:

- **Cloud-based services (Google Speech, Azure Speech):** Require internet connectivity, send private data to third parties, introduce network latency, and create vendor lock-in
- **Legacy Linux tools (Simon, Dictator):** Built for X11, don't work properly on Wayland, lack modern GPU acceleration, and have outdated UI paradigms
- **General-purpose dictation apps:** Optimize for accuracy over speed, creating multi-second delays that interrupt natural workflows, especially problematic for rapid LLM prompting

**Urgency & Importance:**

This problem is becoming more critical now:

- **Wayland adoption is accelerating:** Fedora defaults to Wayland, and other distributions are following. X11 workarounds are increasingly unsustainable
- **LLM tools are central to workflows:** Developers increasingly rely on Claude Code, ChatGPT, and similar tools where voice input significantly improves productivity
- **Privacy awareness is growing:** Users are more conscious of data privacy and seek local-first alternatives to cloud services
- **Hardware capabilities enable new solutions:** Modern NVIDIA GPUs make local Whisper transcription fast enough for real-time use, eliminating the technical barriers that previously necessitated cloud solutions

---

## Proposed Solution

**Core Concept & Approach:**

Fedora Voice Dictation solves the voice input problem by combining OpenAI's Whisper speech recognition with GPU acceleration and native Wayland integration. The application runs entirely on the user's local machine, leveraging modern NVIDIA GPU hardware to deliver near-instant transcription without any cloud dependencies.

The solution architecture centers on three core principles:

1. **Local-First Processing:** All audio processing happens on-device using locally-installed Whisper models, ensuring complete privacy and offline capability
2. **GPU-Accelerated Performance:** CUDA optimization for NVIDIA GPUs enables real-time streaming transcription with minimal latency
3. **Wayland-Native Integration:** Direct use of Wayland protocols (text-input-unstable-v3, wlr-layer-shell, XDG Desktop Portal) ensures seamless text injection into target applications without X11 dependencies

**Key Differentiators from Existing Solutions:**

What sets Fedora Voice Dictation apart:

- **100% Offline Operation:** No cloud connectivity required; all models and processing stay local, ensuring privacy and enabling use anywhere (no internet needed)
- **Performance-Optimized Architecture:** Designed for speed with GPU acceleration, Voice Activity Detection (VAD), and streaming word-by-word output rather than sentence-at-a-time delays
- **Wayland-Native Design:** Built specifically for modern Linux desktops without X11 fallbacks, ensuring compatibility with Fedora's default environment and future-proofing the solution
- **Power User Focus:** Keyboard-first interface, configuration file support, command palette, and terminal/developer workflow optimization
- **Single-User Simplicity:** No multi-user support, no account systems, no synchronization—just a focused tool for individual productivity

**Why This Solution Will Succeed Where Others Haven't:**

Previous voice dictation attempts on Linux failed because they either:
- Required cloud services that violated privacy principles
- Depended on X11, which is being phased out
- Lacked hardware acceleration, making them too slow
- Tried to serve everyone, becoming complex and unfocused

Fedora Voice Dictation succeeds by:
- **Leveraging modern hardware:** GPU capabilities that didn't exist when legacy tools were built now enable fast local processing
- **Embracing constraints:** Single-user, local-only design eliminates complexity without sacrificing utility
- **Targeting a specific audience:** Power users who value speed, privacy, and configurability over hand-holding and universal compatibility
- **Building on proven technology:** Whisper is production-ready, widely-used, and continuously improving

**High-Level Product Vision:**

Users activate voice dictation with a global hotkey, speak naturally, and see their words appear instantly in Claude Code, terminal, or any focused application. The system tray icon provides quick access to settings (model selection, feature toggles) and session history. The app stays running in the background with the model loaded and ready, ensuring zero startup delay when inspiration strikes.

For LLM workflows specifically, the app detects when Claude Code is active and automatically optimizes output by removing filler words and improving prompt structure. For terminal work, users can dictate commands and code snippets using a simple, unified vocabulary. The experience feels fast, private, and seamlessly integrated—like voice input should have worked all along.

---

## Target Users

### Primary User Segment: LLM-First Developers

**Demographic/Firmographic Profile:**
- **Role:** Software developers, DevOps engineers, technical writers, data scientists
- **Experience Level:** Intermediate to advanced technical users comfortable with command-line tools and configuration files
- **Platform:** Fedora Linux (or Fedora-based distributions) running Wayland desktop environment (GNOME, Hyprland)
- **Hardware:** Systems with modern NVIDIA GPU (RTX 3000 series or newer), 16GB+ RAM
- **Work Environment:** Primarily individual contributors working solo or in small teams; remote or hybrid work setups

**Current Behaviors & Workflows:**
- Spend significant time interacting with LLM tools (Claude Code, ChatGPT, GitHub Copilot) for code generation, debugging, documentation, and problem-solving
- Type long, detailed prompts to LLMs multiple times per day (10-50+ prompts daily)
- Work extensively in terminal environments (bash, zsh) executing commands and managing systems
- Use keyboard shortcuts and command-line tools heavily; prefer keyboard navigation over mouse
- Edit configuration files directly rather than using GUI preference panels
- Value efficiency and speed; willing to learn tools that improve productivity
- Run Wayland natively and avoid X11 compatibility modes when possible

**Specific Needs & Pain Points:**
- **Speed bottleneck:** Typing long LLM prompts is time-consuming and interrupts flow state
- **Repetitive typing strain:** Frequent long-form technical input causes physical fatigue
- **Privacy concerns:** Uncomfortable with cloud-based voice services that transmit audio data
- **Wayland compatibility:** Existing voice tools don't work properly on Wayland desktop
- **Context switching:** Slowing down to type breaks concentration during creative/problem-solving work
- **Iteration friction:** LLM workflows require multiple prompt iterations; slow input reduces experimentation

**Goals They're Trying to Achieve:**
- Accelerate LLM prompt creation to enable more rapid iteration and exploration
- Reduce physical strain from extensive typing
- Maintain complete privacy while using voice input (no cloud transmission)
- Stay on Wayland without compromising on tooling or reverting to X11
- Integrate voice dictation seamlessly into existing keyboard-centric workflow
- Minimize setup and configuration time (want it to "just work" after initial setup)

---

### Secondary User Segment: Terminal Power Users

**Demographic/Firmographic Profile:**
- **Role:** System administrators, security researchers, infrastructure engineers, Linux enthusiasts
- **Experience Level:** Advanced Linux users; comfortable compiling software and managing complex systems
- **Platform:** Fedora or Fedora-based distributions with Wayland; may run tiling window managers (Hyprland, Sway)
- **Hardware:** Modern desktop systems with NVIDIA GPU capability
- **Work Environment:** Heavy terminal usage; minimal GUI interaction

**Current Behaviors & Workflows:**
- Spend majority of work time in terminal emulators
- Execute complex command sequences and scripts frequently
- Manage multiple systems via SSH
- Prefer keyboard-only workflows; rarely use mouse
- Configure systems via dotfiles and version-controlled configurations
- Value automation and scripting

**Specific Needs & Pain Points:**
- **Complex command entry:** Long command lines with multiple arguments are tedious to type
- **Repetitive commands:** Frequently execute similar commands with slight variations
- **Documentation needs:** Need to document commands and procedures, which requires switching between terminal and text editor
- **Speed requirements:** Want to execute commands as quickly as thinking them
- **No GUI preference:** Existing voice tools are too GUI-focused

**Goals They're Trying to Achieve:**
- Speed up command entry for complex or repetitive terminal operations
- Reduce context switching between thinking and typing
- Document work processes more efficiently
- Maintain fully keyboard-centric workflow with voice as complementary input
- Avoid mouse interaction entirely

---

## Goals & Success Metrics

### Business Objectives

- **Launch a functional MVP within 3 months** that demonstrates core voice dictation capability on Wayland with GPU acceleration, enabling early user feedback and iteration
- **Achieve 100% offline operation** with no cloud dependencies, establishing privacy and independence as foundational product attributes
- **Deliver transcription latency under 500ms** (from speech end to text appearance) to prove the speed-first architecture works for professional workflows
- **Successfully integrate with 3 target applications** (Claude Code, terminal, and one additional text application) to validate Wayland protocol implementation
- **Build an active early adopter community** of 25-50 users within 6 months to provide feedback, identify issues, and validate product-market fit
- **Establish open-source presence** through GitHub repository with clear documentation, enabling community contributions and transparency

### User Success Metrics

- **Daily usage rate:** Users activate voice dictation at least 10 times per day, indicating it's integrated into their workflow
- **Session completion rate:** 90%+ of dictation sessions result in successful text insertion (not aborted due to errors or frustration)
- **Speed improvement:** Users report dictation is faster than typing for prompts/commands longer than 20 words
- **Adoption retention:** 70%+ of users who try the app continue using it after 2 weeks (indicating it provides real value)
- **Privacy satisfaction:** 100% of users confirm they're comfortable with the local-only processing model
- **Zero X11 dependency:** Users successfully run the app on pure Wayland without any X11 compatibility layers

### Key Performance Indicators (KPIs)

- **Transcription Latency:** Average time from end-of-speech to text insertion < 500ms (target: 300ms)
- **Transcription Accuracy:** Word Error Rate (WER) < 10% for technical content (code, commands, LLM prompts)
- **GPU Utilization:** Efficient use of GPU resources, keeping VRAM usage under 4GB for base model
- **Application Compatibility:** Successful text insertion in 95% of tested Wayland applications
- **Startup Time:** App launches and loads model in < 5 seconds on target hardware (RTX 4060, 32GB RAM)
- **Crash-Free Sessions:** 99%+ of dictation sessions complete without application crashes or freezes
- **User Satisfaction Score:** Net Promoter Score (NPS) > 40 among early adopters (indicating strong recommendation likelihood)
- **Community Engagement:** 20+ GitHub stars within first 3 months, 5+ community contributions (issues, PRs, documentation)

---

## MVP Scope

### Core Features (Must Have)

- **Audio Capture & Processing:** Real-time audio capture from microphone using sounddevice library with Wayland compatibility. Implement Voice Activity Detection (VAD) to automatically detect speech start/end, eliminating manual stop button requirement.
  - *Rationale:* Foundation of the entire system. Without reliable audio capture and VAD, user experience degrades to manual stop/start which breaks flow.

- **Whisper Integration with GPU Acceleration:** Local Whisper installation (via pip) with CUDA support for NVIDIA GPU acceleration. Default to base model for optimal speed/accuracy balance. Enable streaming word-by-word transcription output.
  - *Rationale:* GPU acceleration is THE differentiator enabling real-time performance. Base model provides fastest reliable transcription. Streaming output gives immediate feedback.

- **Wayland Text Injection:** Implement text insertion using text-input-unstable-v3 Wayland protocol with clipboard fallback mechanism. Test and verify on GNOME, Hyprland, Sway, and KDE Plasma desktop environments.
  - *Rationale:* Makes dictation actually useful. Wayland protocol is the proper method; clipboard is pragmatic fallback ensuring functionality while protocol implementation matures. Broad DE coverage ensures compatibility across major Wayland implementations.

- **System Tray Integration:** Persistent system tray icon showing status (listening/idle/processing). System tray menu with Start/Stop controls, settings access, and quit option. Toast notifications for state changes.
  - *Rationale:* Provides always-available access without window clutter. Tray icon communicates status at a glance. Matches power user expectations for background services.

- **Global Hotkey Activation:** Configure and trigger voice dictation via global keyboard shortcut. Hotkey activates listening mode; VAD auto-stops when speech ends.
  - *Rationale:* Keyboard-centric workflow essential for target users. Hotkey removes need to hunt for app window or click buttons. Combined with VAD, enables hands-on-keyboard operation.

- **Basic Settings UI:** Settings window for Whisper model selection (tiny/base/small/medium/large via radio buttons), hotkey configuration, and audio input device selection. Settings persistence via JSON configuration file.
  - *Rationale:* Users need control over model choice (speed vs accuracy trade-off) and hotkey preference. JSON file enables manual editing for power users.

- **Session History:** Track and store recent dictation sessions (timestamp, transcribed text, duration). Accessible via system tray menu.
  - *Rationale:* Enables recovery of lost text, provides confidence in system reliability, and creates foundation for future snippet suggestions.

- **Visual Feedback:** Waveform display or level indicator showing audio input and listening/processing state. Ensures user knows system is active.
  - *Rationale:* Audio-only tools lack feedback. Visual indicator prevents "is it working?" uncertainty and confirms microphone is picking up voice.

### Out of Scope for MVP

- Advanced Wayland protocols (wlr-layer-shell, XDG Desktop Portal integration beyond basic text injection)
- Personal dictionary and custom vocabulary learning
- Snippet library and auto-suggestion from history
- Command dictation and voice editing commands ("scratch that", "delete line")
- Code snippet dictation with syntax awareness
- Voice macros and script triggering
- Claude Code context detection and LLM prompt optimization
- Multi-desktop environment optimization beyond GNOME/Hyprland/Sway/KDE
- Personal model training and fine-tuning
- Command palette interface
- Real-time text preview window (optional toggle)
- Learning tool/pronunciation practice mode

### MVP Success Criteria

The MVP is considered successful and ready for early adopter release when:

1. **Core functionality works reliably:** Users can activate dictation via hotkey, speak naturally, and see text appear in target applications with 90%+ success rate
2. **Performance meets speed requirements:** Average transcription latency < 1 second from speech end to text appearance (acceptable starting point, will optimize toward 500ms target post-MVP)
3. **Wayland compatibility proven:** Successfully inserts text in Claude Code, at least 2 terminal emulators (GNOME Terminal, Konsole), and 1 text editor on GNOME, Hyprland, Sway, and KDE Plasma
4. **GPU acceleration functional:** Demonstrates measurable performance improvement with CUDA vs CPU-only processing (at least 3x faster)
5. **Stable enough for daily use:** Runs for full workday without crashes or memory leaks; handles 50+ dictation sessions consecutively
6. **User can get started quickly:** Complete setup (installation, configuration, first dictation) achievable in under 30 minutes with documentation
7. **Feedback collection ready:** Instrumentation in place to gather latency metrics, error rates, and usage patterns for iteration

---

## Post-MVP Vision

### Phase 2 Features

**Intelligent Features & Learning (4-6 weeks post-MVP)**
- **Personal Dictionary:** Custom vocabulary learning system that adapts to user's technical terms, jargon, project names, and frequently-used phrases. User can manually add entries or system learns from corrections.
- **Snippet Library:** Save and reuse frequently-dictated phrases with quick keyword triggers. System auto-suggests converting repeated dictations (detected via history analysis) into reusable snippets.
- **History-Based Intelligence:** Analyze session history to identify patterns and make proactive suggestions (e.g., "You've dictated this 5 times—create a snippet?").

**Voice Commands & Editing (6-8 weeks post-MVP)**
- **Voice Editing Commands:** Implement natural language editing: "scratch that" (undo last phrase), "delete line", "new paragraph", "cap that" (capitalize previous word).
- **Command Dictation:** Recognize terminal command patterns and format appropriately (spacing, no autocorrect on command names/flags).
- **Code Snippet Dictation:** Basic syntax awareness for common programming languages (Python, JavaScript, Bash) to handle indentation and formatting.

**Claude Code Integration (3-4 weeks post-MVP)**
- **Application Context Detection:** Detect when Claude Code is the active window via Wayland protocols.
- **LLM Prompt Optimization:** Automatically remove filler words ("um", "uh", "like", "you know") and improve prompt structure when dictating to Claude Code.
- **Mode Indicator:** Visual feedback showing "LLM Mode" when optimization is active.

### Long-term Vision (6-12 months)

**Advanced Performance & Hardware Support:**
- Explore whisper.cpp integration for even lower latency (target: sub-200ms)
- Investigate AMD GPU support (ROCm) to broaden hardware compatibility
- Optimize for lower-end hardware (8GB VRAM, older GPUs) through model quantization

**Power User Enhancements:**
- **Command Palette:** Keyboard-accessible interface for all app functions, snippet management, and settings
- **Voice Macros:** Record voice commands that trigger scripts, shell commands, or complex text insertion sequences
- **Configuration Profiles:** Switch between different settings profiles for different contexts (coding, documentation, terminal work)
- **Vim-style Keyboard Navigation:** Navigate settings and history with hjkl keys

**Extended Platform Support:**
- Package as Flatpak for broader distribution
- Test and optimize for additional Wayland compositors (wlroots-based, others)
- Explore compatibility with non-Fedora distributions (Arch, Ubuntu with Wayland)

**Community & Ecosystem:**
- Plugin system for community-contributed features
- API for integration with other tools (text editors, IDEs, terminal emulators)
- Crowdsourced technical vocabulary database (opt-in, privacy-preserving)

### Expansion Opportunities

**Learning & Accessibility:**
- **Pronunciation Practice Mode:** Display real-time transcription for language learning and pronunciation improvement
- **Accessibility Features:** Adapt for users with disabilities who rely on voice input as primary interaction method
- **Multi-language Support:** Expand beyond English to support other languages via Whisper's multilingual models

**Enterprise & Team Features:**
- **Shared Snippet Libraries:** Team-wide snippet sharing (requires rethinking single-user architecture)
- **Usage Analytics Dashboard:** Insights into dictation patterns, time saved, most-used features
- **Integration with Development Tools:** Direct integration with VS Code, JetBrains IDEs, tmux

**Personal AI Training:**
- **On-Device Model Fine-tuning:** Train personalized Whisper model on user's voice and vocabulary (moonshot from brainstorming)
- **Continuous Learning:** System improves automatically from corrections and usage patterns
- **Privacy-Preserving Training:** All training happens locally, no data leaves machine

---

## Technical Considerations

### Platform Requirements

- **Target Platforms:** Fedora Linux 38+ (primary), compatible with Fedora-based distributions (Nobara, Ultramarine)
- **Desktop Environment:** Wayland compositors only - GNOME 43+, KDE Plasma 5.27+, Hyprland 0.30+, Sway 1.8+
- **No X11 Support:** Deliberately excludes XWayland compatibility to maintain architecture purity and simplicity
- **Browser/OS Support:** N/A (native Linux application, not web-based)
- **Performance Requirements:**
  - NVIDIA GPU with CUDA support (RTX 3000 series or newer recommended, GTX 1660+ minimum)
  - 16GB+ system RAM (32GB recommended for large models)
  - 4GB+ available VRAM for base model, 6GB+ for medium/large models
  - Modern CPU (4+ cores) for audio processing pipeline
  - Microphone with reasonable quality (USB or built-in)

### Technology Preferences

**Frontend:**
- **UI Toolkit:** PyQt5 for settings window, system tray, and visual feedback
  - *Rationale:* More complete widget set, better documentation, and proven system tray support across desktop environments
  - *Note:* Will validate performance with early prototypes to ensure latency targets are achievable

**Backend:**
- **Language:** Python 3.10+ (leveraging asyncio for concurrent audio/transcription processing)
  - *Performance validation:* Early prototypes will benchmark latency to confirm Python meets < 1 second transcription target
- **Speech Recognition:** OpenAI Whisper (via openai-whisper pip package) with CUDA acceleration
- **Alternative consideration:** whisper.cpp with Python bindings for potentially better performance (evaluate if Python benchmarks fall short)
- **Audio Capture:** sounddevice library (PortAudio wrapper) with Wayland compatibility
- **VAD Library:** silero-vad (neural network-based) for better accuracy

**Database:**
- **Settings Storage:** JSON configuration file (~/.config/fedora-voice-dictation/config.json)
- **Session History:** JSON file for MVP (~/.local/share/fedora-voice-dictation/history.json)
  - *Future consideration:* Migrate to SQLite post-MVP if advanced querying/analytics become needed

**Hosting/Infrastructure:**
- **Distribution:** RPM package (.rpm) distributed via GitHub repository
- **Repository:** Public GitHub repository for source code, issue tracking, and community contributions
- **Future consideration:** Flatpak package for broader distribution beyond Fedora ecosystem

### Architecture Considerations

**Repository Structure:**
- **Monorepo:** Single repository containing application code, packaging specs, documentation
- **Structure:**
  ```
  fedora-voice-dictation/
  ├── src/                    # Application source code
  │   ├── audio/              # Audio capture, VAD
  │   ├── transcription/      # Whisper integration
  │   ├── wayland/            # Wayland protocol integration
  │   ├── ui/                 # System tray, settings, feedback UI
  │   └── core/               # Configuration, history, main loop
  ├── packaging/              # RPM spec files, build scripts
  ├── docs/                   # User documentation, API docs
  ├── tests/                  # Unit and integration tests
  └── examples/               # Example configurations
  ```

**Service Architecture:**
- **Single-process application** with threaded/async architecture (no microservices)
- **Main event loop:** Qt event loop managing UI and system tray
- **Audio thread:** Continuous audio capture and VAD processing
- **Transcription worker:** Queue-based Whisper processing (async to avoid blocking)
- **IPC:** D-Bus for system tray notifications and desktop integration
- *Rationale:* Single-process simplicity aligns with single-user, local-only design; no network complexity

**Integration Requirements:**
- **Wayland Protocols:**
  - text-input-unstable-v3 for text injection (primary method)
  - wlr-layer-shell (future: for overlay UI)
  - XDG Desktop Portal (future: for enhanced permissions/compatibility)
- **D-Bus Services:**
  - org.freedesktop.Notifications for toast notifications
  - System tray via StatusNotifierItem protocol
- **Clipboard Integration:** python-xlib or pyclip as fallback text injection method
- **Hotkey Registration:** python-xlib global hotkey or compositor-specific methods

**Security/Compliance:**
- **Privacy-First Design:** No telemetry, no analytics, no network calls (except initial model download)
- **Data Storage:** All data stays local; no cloud sync or backup
- **Permissions:** Requires microphone access (system prompt on first use), keyboard hotkey registration
- **Model Security:** Verify Whisper model checksums on download to prevent tampering
- **Configuration Security:** Warn if config file has overly permissive permissions

---

## Constraints & Assumptions

### Constraints

**Budget:**
- **Development Cost:** Solo developer project (no paid development team)
- **Infrastructure Cost:** Zero hosting costs (no servers, no cloud services)
- **Distribution Cost:** Free via GitHub and RPM; no paid app store fees
- **Third-party Services:** None (100% open-source dependencies)
- *Constraint impact:* Development speed limited by single developer bandwidth; prioritization critical

**Timeline:**
- **MVP Target:** 3 months from project start to first usable release
- **Development Pace:** Part-time development (evenings/weekends assumed)
- **Iteration Cycles:** 2-week sprints aligned with brainstorming priority list
- *Constraint impact:* Must ruthlessly scope MVP to achievable features; defer nice-to-haves

**Resources:**
- **Developer Expertise:** Strong Python skills, moderate Wayland/Linux knowledge, learning Whisper integration
- **Hardware Access:** Personal RTX 4060 + 32GB RAM system for development and testing
- **Testing Environment:** Limited to developer's desktop environments (GNOME, Hyprland); community needed for broader testing
- **Documentation Time:** Must balance coding with writing user/developer documentation
- *Constraint impact:* Some learning curve on Wayland protocols; may need community help for multi-DE testing

**Technical:**
- **Wayland Protocols:** text-input-unstable-v3 availability varies by compositor; may need fallback strategies
- **GPU Dependency:** NVIDIA-only support initially; AMD users excluded until ROCm support added
- **Python Performance:** Interpreted language may limit absolute performance ceiling; mitigated by GPU doing heavy lifting
- **Desktop Environment Support:** System tray implementation varies across GNOME/KDE/Hyprland/Sway; requires per-DE testing
- **Whisper Model Size:** Model download size (base: ~150MB, medium: ~1.5GB, large: ~3GB) requires user bandwidth and storage
- *Constraint impact:* Some users may be unable to run app due to hardware/software incompatibility

### Key Assumptions

**User Assumptions:**
- Users are comfortable with command-line installation and configuration (at least initially)
- Users have modern NVIDIA GPU hardware or are willing to acquire it
- Users are running Fedora or willing to adapt RPM installation to their distribution
- Users have already migrated to Wayland (not still on X11 by choice)
- Users understand voice dictation workflow and have reasonable expectations for accuracy
- Users can tolerate 1-second latency for MVP and understand it will improve

**Technical Assumptions:**
- Python async/threading is sufficient for target latency (< 1 second MVP, < 500ms future)
- Whisper base model provides acceptable accuracy for technical content (code, commands, prompts)
- GPU acceleration provides 3x+ speedup over CPU-only processing
- Wayland text-input-unstable-v3 protocol works reliably in target desktop environments
- PyQt5 system tray integration works consistently across GNOME/KDE/Hyprland/Sway
- sounddevice library captures audio reliably on Wayland without X11 dependencies
- VAD (silero-vad) accurately detects speech boundaries with < 200ms lag

**Market Assumptions:**
- Sufficient demand exists among Fedora power users for local voice dictation
- Early adopter community (25-50 users) is achievable through GitHub/Reddit/forums
- Users value privacy/local-processing enough to accept hardware requirements
- LLM usage (Claude Code, ChatGPT) is widespread enough to justify optimization focus
- Community will contribute bug reports, testing, and eventually code/documentation

**Project Assumptions:**
- MVP can be built in 3 months with part-time development effort
- Open-source model will attract contributors once MVP demonstrates viability
- RPM distribution is sufficient for initial user base (no urgent need for Flatpak)
- GitHub Issues provides adequate project management and user support
- Documentation can be written incrementally alongside feature development

---

## Risks & Open Questions

### Key Risks

- **Wayland Protocol Compatibility:** text-input-unstable-v3 implementation varies across compositors; may not work reliably in all target desktop environments (GNOME/KDE/Hyprland/Sway).
  - *Impact:* High - Core functionality broken if text injection fails. Clipboard fallback mitigates but degrades user experience.
  - *Mitigation:* Early testing across all target DEs; implement robust clipboard fallback; engage with compositor developers if protocol issues discovered.

- **Performance Targets Unachievable:** Python architecture may not achieve < 1 second latency, especially with VAD + Whisper + text injection pipeline.
  - *Impact:* High - Slow performance defeats core value proposition (speed over cloud solutions). User adoption fails if too slow.
  - *Mitigation:* Early performance prototypes to validate architecture; fallback to whisper.cpp if Python too slow; optimize audio buffer sizes and threading.

- **GPU Acceleration Setup Friction:** Users may struggle with CUDA toolkit installation, driver configuration, or model compatibility.
  - *Impact:* Medium - Reduces addressable user base; increases support burden; may prevent adoption despite interest.
  - *Mitigation:* Comprehensive installation documentation; automated setup scripts where possible; provide CPU fallback (slower but functional).

- **Limited User Base:** Fedora + Wayland + NVIDIA GPU + power user comfort level significantly constrains potential users.
  - *Impact:* Medium - Small community limits feedback, testing coverage, and contributor pool. May not reach 25-50 early adopter target.
  - *Mitigation:* Engage Fedora community proactively (Reddit, forums, mailing lists); plan AMD GPU support early; consider Flatpak for broader distribution.

- **VAD Accuracy Problems:** Voice Activity Detection may fail to reliably detect speech boundaries, causing truncated transcriptions or false triggers.
  - *Impact:* Medium - Degrades user experience; forces manual stop button usage (defeats automation benefit). Erodes trust in system.
  - *Mitigation:* Test multiple VAD libraries (silero-vad, webrtcvad); allow user to configure VAD sensitivity; provide manual stop option as backup.

- **Technical Vocabulary Accuracy:** Whisper may struggle with technical terms, code identifiers, command names, and project-specific jargon.
  - *Impact:* Medium - Frustration from constant corrections; may make tool unusable for technical content. Users abandon for typing.
  - *Mitigation:* Plan personal dictionary for Phase 2; document base model limitations; suggest medium/large models for better accuracy.

- **Solo Developer Sustainability:** Single developer may burn out, lose interest, or lack time to maintain project long-term.
  - *Impact:* High - Project stagnates or dies; users lose critical tool; reputation damage for developer.
  - *Mitigation:* Set realistic scope and pace; engage community early for contributions; document architecture for future maintainers; build modular codebase.

- **Competing Solutions Emerge:** Other developers or companies may release similar Wayland voice dictation tools, especially if demand validates.
  - *Impact:* Low-Medium - Could reduce user base or make project redundant. However, open-source nature and specific focus may differentiate.
  - *Mitigation:* Move fast on MVP; build community early; differentiate on privacy/performance; embrace competition as market validation.

### Open Questions

- **Text Injection Method:** Which works most reliably across desktop environments - text-input-unstable-v3, virtual keyboard, or clipboard? Need empirical testing to determine best primary method and fallback strategy.

- **VAD Library Selection:** silero-vad (more accurate, neural network) vs. webrtcvad (faster, simpler) vs. others? What's the actual latency and accuracy trade-off in practice with our audio pipeline?

- **Hotkey Registration:** What's the most reliable cross-compositor method for global hotkeys on Wayland? compositor-specific vs. XDG protocol vs. python-xlib?

- **Model Selection Guidance:** How to help users choose between tiny/base/small/medium/large models? What's the actual speed/accuracy trade-off on our target hardware (RTX 4060)?

- **Snippet Suggestions Trigger:** Should snippet suggestions be proactive (popup) or passive (available in menu)? When triggered, how intrusive should they be?

- **Command Ambiguity Handling:** Voice commands like "delete line" - which line? Previous line, current line, next line? Need clear rules or context detection.

- **Personal Dictionary Training Mode:** Should there be explicit "training mode" where users dictate technical terms, or automatic learning from corrections? What's the UX?

- **Distribution Strategy:** GitHub releases sufficient, or should we pursue COPR repository immediately? What about Flathub for Flatpak distribution?

- **Telemetry Ethics:** Even for improvement, is any usage data collection acceptable given privacy-first positioning? If yes, what minimal metrics with explicit opt-in?

- **Claude Code Detection Mechanism:** How to reliably detect active application on Wayland? Window title, process name, or other compositor APIs? Does it work on all target DEs?

- **Error Recovery UX:** When transcription fails or text injection doesn't work, what should happen? Silent failure, notification, automatic retry, user prompt?

### Areas Needing Further Research

- **Wayland Protocol Implementation:** Deep dive into text-input-unstable-v3 implementation across GNOME, KDE, Hyprland, Sway. Understand limitations and quirks. Identify best practices and fallback strategies.

- **Whisper Performance Benchmarking:** Systematic testing of Whisper models (tiny through large) on RTX 4060 with CUDA. Measure latency, accuracy, VRAM usage, CPU utilization. Compare openai-whisper vs. whisper.cpp.

- **VAD Library Comparison:** Hands-on testing of silero-vad, webrtcvad, and alternatives. Measure latency, accuracy (false positives/negatives), CPU overhead. Test with various microphone qualities and noise levels.

- **Audio Pipeline Optimization:** Research optimal buffer sizes, sample rates, and threading models for minimal latency while maintaining quality. Understand sounddevice library limitations on Wayland.

- **PyQt5 System Tray Portability:** Verify StatusNotifierItem support across all target DEs. Test waveform display performance. Identify any DE-specific quirks or workarounds needed.

- **LLM Prompt Optimization Rules:** Research what filler words to remove, what formatting improves LLM results. Study Claude Code, ChatGPT prompt best practices. Define transformation rules.

- **RPM Packaging Best Practices:** Learn Fedora packaging guidelines, spec file creation, dependency management. Understand how to handle Python packages and CUDA dependencies in RPM.

- **Community Building Strategies:** Research successful open-source project launches. Identify Fedora community forums, subreddits, mailing lists. Plan announcement and feedback collection strategies.

---

## Next Steps

### Immediate Actions

1. **Set up development environment and GitHub repository**
   - Create GitHub repository: `fedora-voice-dictation`
   - Initialize repository structure (src/, docs/, packaging/, tests/, examples/)
   - Set up Python virtual environment with initial dependencies
   - Configure Git workflows and contribution guidelines
   - Create README.md with project overview and setup instructions

2. **Conduct technical validation prototypes (Week 1-2)**
   - **Performance Prototype:** Basic Python script testing Whisper + CUDA latency
     - Measure end-to-end transcription time with base model
     - Validate < 1 second target is achievable
     - Document hardware performance benchmarks
   - **Audio Capture Test:** Verify sounddevice works on Wayland
   - **VAD Comparison:** Quick test of silero-vad vs. webrtcvad accuracy/latency
   - **Decision Point:** Proceed with Python or pivot to whisper.cpp based on results

3. **Implement Core Dictation Engine (Priority #1 from brainstorming) (Week 3-6)**
   - Audio capture pipeline using sounddevice
   - VAD integration (silero-vad based on testing)
   - Whisper integration with CUDA acceleration
   - Streaming word-by-word transcription output
   - Basic error handling and logging
   - Console output for testing (before GUI)

4. **Implement Wayland Text Integration (Priority #2 from brainstorming) (Week 7-10)**
   - Research and implement text-input-unstable-v3 protocol
   - Develop clipboard fallback mechanism
   - Test on GNOME and Hyprland environments
   - Verify text insertion in Claude Code, terminal emulators, text editors
   - Document compatibility findings and workarounds

5. **Build Minimal UI (Week 11-12)**
   - PyQt5 system tray icon with status indication
   - System tray menu (start/stop, settings, quit)
   - Global hotkey registration and handling
   - Basic settings window (model selection, hotkey config, audio device)
   - Toast notifications for state changes
   - Simple waveform or level indicator for visual feedback

6. **Create MVP Packaging and Documentation (Week 13-14)**
   - Write user documentation (installation, configuration, usage)
   - Create RPM spec file and build scripts
   - Test RPM installation on clean Fedora system
   - Write developer documentation (architecture, contributing guide)
   - Prepare GitHub release with installation instructions

7. **Early User Testing and Iteration (Week 15-18)**
   - Release MVP to personal use and 5-10 trusted early testers
   - Collect feedback on performance, reliability, usability
   - Fix critical bugs and usability issues
   - Iterate based on real-world usage patterns
   - Document common issues and FAQs

8. **Public MVP Release (Week 19-20)**
   - Finalize documentation and README
   - Create GitHub release with binaries and source
   - Announce on Fedora subreddit, forums, mailing lists
   - Set up GitHub Issues for bug reports and feature requests
   - Monitor feedback and respond to early adopter questions

### PM Handoff

This Project Brief provides the full context for **Fedora Voice Dictation**. When transitioning to PRD development, please:

- Start in **PRD Generation Mode** to create detailed product requirements
- Review this brief thoroughly, noting the prioritized MVP scope and out-of-scope features
- Work with the user section-by-section following the PRD template
- Ask for clarification on any ambiguities or open questions documented here
- Suggest improvements based on industry best practices for voice dictation and developer tools
- Ensure the PRD reflects the technical decisions made in this brief (Python, PyQt5, Wayland-native, NVIDIA GPU, RPM distribution)
- Maintain focus on the primary user segment (LLM-First Developers) and their workflows
- Keep the 3-month MVP timeline constraint in mind when scoping features

The brainstorming results in `docs/brainstorming-session-results.md` provide additional context on ideation, priorities, and technical considerations.

---

