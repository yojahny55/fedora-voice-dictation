# Next Steps

## UX Expert Prompt

**Context:** The Product Requirements Document for Fedora Voice Dictation is complete and validated. We need detailed UX/UI design to guide Epic 2 (Desktop Integration) and Epic 3 (Configuration & Model Management) implementation.

**Your Task:**

Using the PRD (docs/prd.md) and Project Brief (docs/brief.md) as input, create a comprehensive UX design document that includes:

1. **Detailed User Flows:** First-run setup wizard, hotkey-activated dictation, settings configuration, history viewer, error recovery workflows
2. **UI Specifications:** Settings window wireframes, model management dialog, history viewer, diagnostic tools, system tray menu, audio level indicator
3. **Interaction Design:** Keyboard navigation patterns, state transitions and visual feedback, notification design, audio feedback timing
4. **Accessibility Specifications:** Keyboard navigation requirements, screen reader labels, focus indicator styling, high contrast considerations
5. **Desktop Environment Adaptations:** GNOME-specific considerations, KDE theming, Hyprland/Sway minimal DE adaptations

**Key Constraints from PRD:**
- Target users: Power users, developers, terminal-focused professionals
- Design philosophy: "Invisible until needed" - minimal UI, keyboard-first
- Accessibility: MVP scope is keyboard navigation + basic screen reader, full WCAG AA in Phase 2
- System tray is primary interface
- Non-modal windows preferred

**Deliverables:**
- UX Design Document (docs/ux-design.md) with wireframes and interaction specifications
- Recommendations for UX validation testing during Epic 2-3 development

---

## Architect Prompt

**Context:** The Product Requirements Document for Fedora Voice Dictation is complete and validated. The PRD defines a Wayland-native voice dictation application using Python, PyQt5, Whisper (GPU-accelerated), and local-only processing.

**Your Task:**

Using the PRD (docs/prd.md), Project Brief (docs/brief.md), and the comprehensive requirements, create a detailed Software Architecture Document that provides implementation guidance for all 4 epics (40 stories).

**Critical Architecture Decisions Required:**

1. **Performance Validation (Week 1-2 Prototype):**
   - Validate Python async/threaded architecture can achieve <1 second latency (MVP) and <500ms goal
   - Benchmark Whisper base model on RTX 4060 with CUDA
   - Test sounddevice audio capture on Wayland
   - **Go/No-Go:** If latency >1.5 seconds, recommend whisper.cpp alternative

2. **Wayland Integration Strategy (Week 2-3 Spike):**
   - Design text-input-unstable-v3 protocol implementation approach
   - Test protocol across GNOME, KDE, Hyprland, Sway
   - Design clipboard fallback mechanism and orchestration logic
   - Specify hotkey registration methods per compositor
   - Test PyQt5 StatusNotifierItem system tray across all 4 DEs

3. **Detailed Component Architecture:**
   - Audio Pipeline (threading, buffering, VAD integration)
   - Transcription Engine (model loading, CUDA context, CPU fallback)
   - Wayland Integration (window focus, text injection orchestration)
   - State Machine (states, transitions, timeouts, thread-safety)
   - UI Components (Qt event loop, system tray, non-modal windows, settings persistence)
   - Configuration & History (JSON schema, atomic writes, validation, pruning)

4. **Data Flow & Threading:** Sequence diagrams, thread communication, latency budget breakdown, error propagation

5. **Technology Stack Specifics:** Python 3.10+ features, PyQt5 components, CUDA/PyTorch integration, Wayland library choices

6. **Testing Strategy:** Unit testing approach, integration testing, performance testing methodology

**Key Technical Constraints from PRD:**
- Python 3.10+, PyQt5, openai-whisper, sounddevice, silero-vad
- NVIDIA CUDA 11.8+ (AMD deferred to Phase 2)
- Wayland-only (no X11 dependencies)
- Single-process architecture
- Monorepo structure
- Target latency: <1000ms MVP, <500ms goal
- Target platforms: Fedora 38+, GNOME/KDE/Hyprland/Sway

**Deliverables:**
1. **Software Architecture Document** (docs/architecture.md) with: Component diagrams, threading model, technology stack specifications, data models, error handling patterns, performance optimization strategies
2. **Week 1-2 Prototype Results:** Performance benchmark report, Wayland integration spike findings, Go/No-Go recommendation
3. **Epic 1 Implementation Guide:** Detailed module specifications for Stories 1.1-1.10, code structure, logging patterns, testing approach

**Timeline:** Architecture document complete before Epic 1 development begins (Week 3-4). Early prototypes (Week 1-2) inform architecture decisions and validate feasibility.

---

**End of PRD**
