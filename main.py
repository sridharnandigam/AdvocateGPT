"""Terminal entry point for the text-only postoperative assistant MVP."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from nemotron_agent import NemotronAgent

BASE_DIR = Path(__file__).resolve().parent
CONVERSATIONS_DIR = BASE_DIR / "patient_context" / "conversations"


class ConversationLogger:
    """Append a simple markdown transcript for each session."""

    def __init__(self, role: str) -> None:
        CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
        self.started_at = datetime.now()
        self.path = CONVERSATIONS_DIR / f"{self.started_at:%Y-%m-%d_%H-%M-%S}.md"
        self.path.write_text(
            (
                "# Conversation Log\n\n"
                f"- Started: {self.started_at.isoformat(timespec='seconds')}\n"
                f"- Role: {role}\n\n"
            ),
            encoding="utf-8",
        )

    def append(self, speaker: str, message: str) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(f"## {speaker}\n\n{message.strip()}\n\n")


def prompt_for_role() -> str | None:
    """Require /patient, /nurse, or /family before the chat loop begins."""
    print("Welcome to Post-Op Assistant")
    print("Type /patient, /nurse, or /family to begin. Type /quit to exit.")

    while True:
        try:
            command = input("> ").strip()
        except EOFError:
            print()
            return None

        if command == "/quit":
            return None
        if command == "/patient":
            return "patient"
        if command == "/nurse":
            return "nurse"
        if command == "/family":
            return "family"

        print("Please begin with /patient, /nurse, or /family.")


def main() -> None:
    """Run the terminal chat loop."""
    role = prompt_for_role()
    if role is None:
        return

    agent = NemotronAgent()
    logger = ConversationLogger(role)

    logger.append("System", f"Role set to {role}.")
    print(f"Role set to {role}. Type /quit to exit.")

    try:
        while True:
            try:
                user_message = input("> ").strip()
            except EOFError:
                print()
                break

            if not user_message:
                continue
            if user_message == "/quit":
                break

            logger.append("User", user_message)
            response = agent.respond(user_message=user_message, role=role)
            print(f"Assistant: {response}")
            logger.append("Assistant", response)
    finally:
        agent.close()
        print(f"Conversation saved to {logger.path}")


if __name__ == "__main__":
    main()
