# Data Directory

This directory stores supporting reference material used by the assistant.

## Subdirectories

- `medication_details/`
  - markdown files describing specific medications, common uses, and side effects
- `medquad/demo/`
  - optional XML demo question/answer data used as supplemental generic context
- `operation_details/`
  - markdown files describing specific operations and common recovery expectations

## Data Principles

- keep files short and readable
- prefer patient-friendly language
- avoid dumping huge documents into a single file
- use filenames that are easy to retrieve
- treat MedQuAD demo data as generic support material, not patient-specific facts

## Example File Names

Medication details:
- `acetaminophen.md`
- `ondansetron.md`
- `oxycodone.md`

Operation details:
- `laparoscopic_cholecystectomy.md`
- `knee_replacement.md`
- `appendectomy.md`
