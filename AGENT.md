
---

## `AGENT.md` (root)

```md
# Repository Agent Instructions

This file is for Codex or any code-generation assistant working on the repository.

## Project Mission

Build a local-first postoperative bedside assistant MVP with:
- a terminal text UI
- a local LLM backend
- markdown-based patient context
- safe summarization and escalation behavior
- stubs for future vision and gesture input

## Build Priorities

### Highest priority
1. `main.py` should run
2. user can choose `/patient` or `/nurse`
3. agent can load context markdown files
4. agent can generate a response using a local model wrapper
5. conversation logs are saved

### Medium priority
1. clean file/module structure
2. configurable context loading
3. clean prompts and response formatting
4. graceful error handling when model backend is unavailable

### Lowest priority
1. actual video support
2. actual VLM support
3. actual MediaPipe support
4. speech

## Architectural Constraints

- Prefer plain Python.
- Avoid LangChain for the MVP.
- Do not build a distributed system.
- Only the LLM may be treated like a model service.
- `vlm.py` and `hand_detection.py` should expose simple function/class interfaces but may initially return mock data.
- Keep implementation understandable and hackathon-friendly.

## Expected Python Files

### `main.py`
Responsibilities:
- terminal UI
- role initialization via user input (`/patient` or `/nurse`)
- message loop
- response printing
- conversation logging

### `nemotron_agent.py`
Responsibilities:
- load markdown context
- assemble system prompt
- call local LLM backend
- optionally expose simple tool hooks
- return assistant response text

### `video.py`
Responsibilities:
- future camera capture
- may initially contain placeholder classes/functions only

### `vlm.py`
Responsibilities:
- future screenshot/image reasoning
- initially define a stable interface only

### `hand_detection.py`
Responsibilities:
- future MediaPipe integration
- initially define a stable interface only

## Coding Style

- Python 3.10+
- readable and minimal
- docstrings for public functions/classes
- small functions
- avoid deep abstractions
- make reasonable defaults
- use simple config constants if needed

## Safety Rules

The assistant must not:
- claim to diagnose
- recommend medication changes as authoritative medical advice
- override clinician judgment

The assistant should:
- summarize context
- encourage escalation when symptoms are urgent
- state limitations clearly when needed

## Suggested Interfaces

### `nemotron_agent.py`
Potential objects/functions:
- `class NemotronAgent`
- `load_context()`
- `build_system_prompt(role: str) -> str`
- `respond(user_message: str, role: str) -> str`

### `vlm.py`
Potential objects/functions:
- `class VLMClient`
- `analyze_image(image_path: str, prompt: str) -> str`

### `hand_detection.py`
Potential objects/functions:
- `class HandSignalDetector`
- `detect_pain_score(frame) -> int | None`
- `detect_yes_no(frame) -> str | None`

## Acceptance Criteria for MVP

The MVP is successful when:
1. `python main.py`, or ideally, a built launches successfully
2. role can be set with `/patient` or `/nurse`
3. typed patient concerns receive a contextual response
4. context files influence the answer
5. chat is logged to a timestamped markdown file
6. code contains clear extension points for vision and gesture support

## Do Not Do Yet

- no database
- no auth system
- no web app
- no Kubernetes
- no microservices
- no complex orchestration
- no advanced agent frameworks