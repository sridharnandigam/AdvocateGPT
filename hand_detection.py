"""Placeholder hand signal interface for future non-verbal input."""

from __future__ import annotations


class HandSignalDetector:
    """Stub detector for future MediaPipe-based gesture support."""

    def detect_pain_score(self, frame) -> int | None:
        return None

    def detect_yes_no(self, frame) -> str | None:
        return None
