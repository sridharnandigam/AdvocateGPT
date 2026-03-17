# MVP TODO

## Must Have

- [ ] create runnable `main.py`
- [ ] create `NemotronAgent` in `nemotron_agent.py`
- [ ] load context markdown from `patient_context/`
- [ ] implement role selection: `/patient`, `/nurse`
- [ ] generate response from local model backend
- [ ] save logs to `patient_context/conversations/`
- [ ] handle missing model/backend errors gracefully

## Should Have

- [ ] concise assistant persona
- [ ] urgent symptom escalation behavior
- [ ] nurse-oriented summarization mode
- [ ] simple config for model name/path/backend
- [ ] unit-testable context loader helpers

## Nice to Have

- [ ] `video.py` placeholder API
- [ ] `vlm.py` placeholder API
- [ ] `hand_detection.py` placeholder API
- [ ] mock gesture input for demo
- [ ] command like `/summary` for nurse handoff

## Demo Script

- [ ] start program
- [ ] initialize with `/patient`
- [ ] enter concern like pain/nausea
- [ ] receive context-aware response
- [ ] trigger urgent escalation example
- [ ] show generated conversation log