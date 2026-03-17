# Post-Op Assistant MVP

A local-first postoperative patient assistant for hackathon demo use.

This MVP is designed for a **very short build window** and prioritizes:
- local inference
- simple terminal/text UI
- clear patient/nurse workflows
- context-aware summaries
- future support for vision and non-verbal input

## MVP Goal

Build a working demo where:
1. The program starts in a simple Python terminal UI.
2. The user initializes as either `/patient` or `/nurse`.
3. The patient types concerns or requests.
4. A local LLM reads from structured context in `patient_context/`.
5. The LLM responds as a bedside assistant:
   - acknowledges the concern
   - summarizes relevant postop context
   - references medication and surgery details when applicable
   - escalates urgent concerns
6. The conversation is logged to `patient_context/conversations/`.

## Non-Goals for MVP

These are intentionally deferred unless the text MVP is already working:
- real-time video streaming
- fully autonomous tool use
- speech input/output
- strong permission enforcement on files
- production security
- real medical advice, diagnosis, or medication changes

## Core Design

### Model plan
Primary model:
- Nemotron 30B **or**
- NVIDIA Nemotron Nano 12B v2 VL FP8 if it is much easier/faster to run locally

For the MVP, treat the model as a **text assistant first**.

Planned later:
- Qwen VL for screenshot/image reasoning
- MediaPipe for non-verbal yes/no and finger pain score
- optional speech stack

## Safety Boundaries

This assistant is a **communication, summarization, and context-retrieval tool**.

It must:
- help patients express needs
- summarize relevant recovery context
- surface urgent red flags
- help nurses quickly understand the situation

It must not:
- independently diagnose
- prescribe or change medications
- replace a doctor or nurse
- present itself as a definitive medical authority

When uncertain or when red flags are present, it should explicitly recommend escalation to the nurse or doctor.

## Directory Overview

### Root files
- `main.py`
  - terminal UI entry point
  - user role selection
  - event loop
- `nemotron_agent.py`
  - agent initialization
  - prompt assembly
  - context loading
  - response generation
  - optional simple tool dispatch
- `video.py`
  - future video capture module
- `vlm.py`
  - future Qwen VL integration
- `hand_detection.py`
  - future MediaPipe integration for hand gestures

### Context directory
- `patient_context/AGENT.md`
  - runtime instructions loaded into the model
- `patient_context/URGENT.md`
  - urgent red flags and escalation behavior
- `patient_context/DOCTOR.md`
  - doctor-facing notes
- `patient_context/POSTOP_DETAILS.md`
  - patient’s current post-op status
- `patient_context/SURGERY_DETAILS.md`
  - surgery details and restrictions
- `patient_context/MEDICATION_SCHEDULE.md`
  - scheduled meds and simple notes
- `patient_context/conversations/`
  - saved chat logs
- `patient_context/data/`
  - reference material for medication and operation details

## Recommended Build Order

### Phase 1: text MVP
1. Implement `main.py`
2. Implement `nemotron_agent.py`
3. Load markdown context files
4. Generate responses from local model
5. Log conversation transcripts

### Phase 2: vision skeleton
1. Create stub interfaces in `video.py`
2. Create stub interfaces in `vlm.py`
3. Create stub interfaces in `hand_detection.py`

### Phase 3: non-verbal input
1. MediaPipe finger counting
2. thumbs up/down yes-no input
3. feed extracted signals into the agent as structured observations

## Expected CLI Flow

Example:

```text
$ python main.py

Welcome to Post-Op Assistant
Type /patient or /nurse to begin.

> /patient
Role set to patient.

> My pain is getting worse and I feel nauseous.
Assistant: ...