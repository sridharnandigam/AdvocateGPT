"""Prompt assembly and response generation for the bedside assistant."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

from config import AUTO_START_MODEL_SERVER, LLAMA_BASE_URL
from llama_client import LlamaChatClient
from server_manager import LlamaServerManager

BASE_DIR = Path(__file__).resolve().parent
CONTEXT_DIR = BASE_DIR / "patient_context"
CONVERSATIONS_DIR = CONTEXT_DIR / "conversations"
MEDQUAD_DEMO_DIR = CONTEXT_DIR / "data" / "medquad" / "demo"

CONTEXT_FILES = {
    "AGENT.md": CONTEXT_DIR / "AGENT.md",
    "URGENT.md": CONTEXT_DIR / "URGENT.md",
    "POSTOP_DETAILS.md": CONTEXT_DIR / "POSTOP_DETAILS.md",
    "SURGERY_DETAILS.md": CONTEXT_DIR / "SURGERY_DETAILS.md",
    "MEDICATION_SCHEDULE.md": CONTEXT_DIR / "MEDICATION_SCHEDULE.md",
}

URGENT_KEYWORDS = {
    "chest pain",
    "trouble breathing",
    "shortness of breath",
    "blue lips",
    "severe pain",
    "worsening pain",
    "heavy bleeding",
    "uncontrolled vomiting",
    "can't stop vomiting",
    "sudden confusion",
    "confused",
    "loss of consciousness",
    "passed out",
    "severe swelling",
    "allergic reaction",
    "wheezing",
    "new weakness",
    "can't move",
    "cannot move",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "did",
    "do",
    "does",
    "for",
    "from",
    "had",
    "has",
    "have",
    "how",
    "i",
    "important",
    "is",
    "it",
    "me",
    "my",
    "now",
    "of",
    "or",
    "say",
    "she",
    "should",
    "that",
    "the",
    "they",
    "to",
    "was",
    "we",
    "were",
    "what",
}


def _read_markdown(path: Path) -> str:
    """Load a markdown file or return a small missing-file marker."""
    if not path.exists():
        return f"# Missing Context\n\nExpected file not found: {path.name}"
    return path.read_text(encoding="utf-8").strip()


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) >= 3 and token not in STOPWORDS
    }


def _tag_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _clip_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars].rstrip()}..."


class NemotronAgent:
    """Context-aware wrapper around the local llama-server chat API."""

    def __init__(
        self,
        client: LlamaChatClient | None = None,
        server_manager: LlamaServerManager | None = None,
    ) -> None:
        self.client = client or LlamaChatClient()
        self.server_manager = server_manager or LlamaServerManager()
        self._startup_error: str | None = None
        self.context = {
            name: _read_markdown(path)
            for name, path in CONTEXT_FILES.items()
        }
        self.medquad_examples = self._load_medquad_examples()

        if AUTO_START_MODEL_SERVER:
            try:
                self.server_manager.start()
            except RuntimeError as exc:
                self._startup_error = str(exc)

    def _extract_qa_pairs_from_xml(self, path: Path) -> list[dict[str, str]]:
        """Parse a MedQuAD-style XML file into question/answer pairs."""
        try:
            root = ET.parse(path).getroot()
        except (ET.ParseError, OSError):
            return []

        pairs: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()

        for node in [root, *root.iter()]:
            question = ""
            answer = ""
            focus = ""

            for child in list(node):
                text = " ".join(part.strip() for part in child.itertext() if part.strip())
                if not text:
                    continue

                tag = _tag_name(child.tag)
                if "question" in tag and not question:
                    question = text
                elif "answer" in tag and not answer:
                    answer = text
                elif "focus" in tag and not focus:
                    focus = text

            if not question or not answer:
                continue

            key = (question, answer)
            if key in seen:
                continue

            seen.add(key)
            pairs.append(
                {
                    "source": path.name,
                    "focus": focus,
                    "question": question,
                    "answer": answer,
                }
            )

        if pairs:
            return pairs

        question = ""
        answer = ""
        focus = ""
        for element in root.iter():
            text = " ".join(part.strip() for part in element.itertext() if part.strip())
            if not text:
                continue

            tag = _tag_name(element.tag)
            if "question" in tag and not question:
                question = text
            elif "answer" in tag and not answer:
                answer = text
            elif "focus" in tag and not focus:
                focus = text

        if question and answer:
            return [
                {
                    "source": path.name,
                    "focus": focus,
                    "question": question,
                    "answer": answer,
                }
            ]

        return []

    def _load_medquad_examples(self) -> list[dict[str, str]]:
        """Load XML demo Q/A data for optional prompt support."""
        if not MEDQUAD_DEMO_DIR.exists():
            return []

        examples: list[dict[str, str]] = []
        for path in sorted(MEDQUAD_DEMO_DIR.rglob("*.xml")):
            examples.extend(self._extract_qa_pairs_from_xml(path))
        return examples

    def _select_medquad_examples(
        self,
        user_message: str,
        max_examples: int = 2,
        max_chars_per_answer: int = 500,
    ) -> str:
        """Return a compact set of relevant MedQuAD demo examples."""
        if not self.medquad_examples:
            return ""

        message_tokens = _tokenize(user_message)
        if not message_tokens:
            return ""

        scored_examples: list[tuple[int, dict[str, str]]] = []
        for example in self.medquad_examples:
            haystack = " ".join(
                [
                    example.get("focus", ""),
                    example.get("question", ""),
                    example.get("answer", ""),
                ]
            )
            example_tokens = _tokenize(haystack)
            overlap = len(message_tokens & example_tokens)
            if overlap <= 0:
                continue
            scored_examples.append((overlap, example))

        if not scored_examples:
            return ""

        scored_examples.sort(
            key=lambda item: (
                -item[0],
                item[1].get("source", ""),
                item[1].get("question", ""),
            )
        )

        lines = [
            (
                "Use these MedQuAD demo examples only as supplemental generic communication context. "
                "Do not treat them as patient-specific facts and do not let them override the local postop records, "
                "recent conversations, or URGENT.md."
            )
        ]

        for _, example in scored_examples[:max_examples]:
            focus = example.get("focus", "").strip()
            lines.append(f"Source: {example['source']}")
            if focus:
                lines.append(f"Focus: {focus}")
            lines.append(f"Q: {_clip_text(example['question'], 220)}")
            lines.append(f"A: {_clip_text(example['answer'], max_chars_per_answer)}")
            lines.append("")

        return "\n".join(lines).strip()

    def _load_recent_conversations(
        self,
        max_files: int = 3,
        max_chars: int = 5000,
    ) -> str:
        """Return a compact slice of recent conversation logs for family updates."""
        if not CONVERSATIONS_DIR.exists():
            return "No prior conversation logs were found."

        files = sorted(
            (
                path
                for path in CONVERSATIONS_DIR.glob("*.md")
                if path.name != "README.md"
            ),
            reverse=True,
        )

        if not files:
            return "No prior conversation logs were found."

        chunks: list[str] = []
        used_chars = 0

        for path in files[:max_files]:
            content = _read_markdown(path)
            remaining = max_chars - used_chars
            if remaining <= 0:
                break

            if len(content) > remaining:
                content = f"{content[:remaining].rstrip()}..."

            chunk = f"### {path.name}\n{content}"
            chunks.append(chunk)
            used_chars += len(chunk)

        return "\n\n".join(chunks)

    def build_system_prompt(self, role: str, user_message: str = "") -> str:
        """Assemble the system prompt from role guidance and markdown context."""
        normalized_role = role.strip().lower()
        if normalized_role not in {"patient", "nurse", "family"}:
            raise ValueError("role must be 'patient', 'nurse', or 'family'")

        if normalized_role == "patient":
            role_prompt = (
                "You are helping a postoperative patient communicate clearly. "
                "Respond with calm, concise language, summarize what matters, "
                "and if symptoms seem urgent explicitly recommend alerting the nurse."
            )
        elif normalized_role == "nurse":
            role_prompt = (
                "You are helping a nurse quickly understand the patient's status. "
                "Be concise and structured, focus on symptom summary, relevant postop "
                "context, medication context, and urgency."
            )
        else:
            role_prompt = (
                "You are helping a family member understand how the patient is doing. "
                "Prioritize recent conversation logs and URGENT.md, summarize the current situation in plain language, "
                "and mention important nurse or doctor updates only if they are explicitly documented. "
                "If the logs do not contain an important update, say that clearly."
            )

        sections = [
            "You are a communication and summarization aide, not an autonomous medical decision-maker.",
            "If symptoms seem urgent or rapidly worsening, explicitly recommend alerting the nurse right away.",
            (
                "Optimize for bedside communication: respond quickly, keep only the most relevant details, "
                "and do not give long lectures or background explanations."
            ),
            (
                "Default to 1-3 short sentences and usually stay under 80 words. "
                "If a list helps, keep it to at most 3 brief items."
            ),
            role_prompt,
        ]

        if normalized_role == "family":
            ordered_names = [
                "URGENT.md",
                "POSTOP_DETAILS.md",
                "SURGERY_DETAILS.md",
                "MEDICATION_SCHEDULE.md",
                "AGENT.md",
            ]
        else:
            ordered_names = list(self.context.keys())

        for name in ordered_names:
            sections.append(f"## {name}\n{self.context[name]}")

        if normalized_role == "family":
            sections.append(
                "## RECENT_CONVERSATIONS\n"
                f"{self._load_recent_conversations()}"
            )

        medquad_support = self._select_medquad_examples(user_message)
        if medquad_support:
            sections.append(f"## MEDQUAD_DEMO_SUPPORT\n{medquad_support}")

        return "\n\n".join(sections)

    def _looks_urgent(self, user_message: str) -> bool:
        lowered = user_message.lower()
        return any(keyword in lowered for keyword in URGENT_KEYWORDS)

    def _finalize_response(self, response: str, user_message: str, role: str) -> str:
        if not self._looks_urgent(user_message):
            return response

        lowered = response.lower()
        if role == "patient" and "nurse" not in lowered:
            return f"{response}\n\nThese symptoms may be urgent. Please alert the nurse right away."
        if role == "nurse" and "prioritize" not in lowered and "urgent" not in lowered:
            return f"{response}\n\nThis may be urgent and should be prioritized for clinical review."
        if role == "family" and "nurse" not in lowered:
            return (
                f"{response}\n\n"
                "If she is having these symptoms now, please alert the nurse right away."
            )
        return response

    def respond(self, user_message: str, role: str) -> str:
        """Generate a response for the given user message and role."""
        message = user_message.strip()
        normalized_role = role.strip().lower()
        if not message:
            return "Please enter a message for the assistant."

        try:
            if AUTO_START_MODEL_SERVER:
                self.server_manager.start()
                self._startup_error = None
            elif not self.server_manager.is_healthy():
                raise RuntimeError(
                    f"Local model server is not reachable at {LLAMA_BASE_URL}."
                )

            response = self.client.chat(
                system_prompt=self.build_system_prompt(normalized_role, message),
                user_message=message,
            )
            return self._finalize_response(
                response=response,
                user_message=message,
                role=normalized_role,
            )
        except (requests.RequestException, RuntimeError, ValueError) as exc:
            details = str(exc)
            if self._startup_error and self._startup_error not in details:
                details = f"{self._startup_error}; {details}"
            return (
                "I couldn't reach the local model right now. "
                "If this feels urgent, please alert the nurse directly.\n\n"
                f"Backend details: {details}"
            )

    def close(self) -> None:
        """Stop the server if this agent started one."""
        self.server_manager.stop()
