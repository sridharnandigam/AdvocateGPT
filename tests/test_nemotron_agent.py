"""Small regression tests for the text-only Nemotron agent MVP."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from nemotron_agent import NemotronAgent


class FakeClient:
    """Minimal client stub that records the last prompt it received."""

    def __init__(self, response: str) -> None:
        self.response = response
        self.last_system_prompt = ""
        self.last_user_message = ""

    def chat(self, system_prompt: str, user_message: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_message = user_message
        return self.response


class FakeManager:
    """Minimal server manager stub for tests."""

    def __init__(self) -> None:
        self.start_calls = 0

    def is_healthy(self) -> bool:
        return True

    def start(self) -> None:
        self.start_calls += 1

    def stop(self) -> None:
        return None


class NemotronAgentTests(unittest.TestCase):
    """Regression tests for prompt assembly and urgent escalation language."""

    def build_agent(self, response: str) -> tuple[NemotronAgent, FakeClient, FakeManager]:
        client = FakeClient(response=response)
        manager = FakeManager()
        agent = NemotronAgent(client=client, server_manager=manager)
        return agent, client, manager

    def test_urgent_patient_response_adds_nurse_escalation(self) -> None:
        agent, _, _ = self.build_agent("I can help summarize this for your care team.")

        response = agent.respond("I have chest pain and trouble breathing.", "patient")

        self.assertIn("Please alert the nurse right away.", response)

    def test_nonurgent_patient_response_is_left_alone(self) -> None:
        agent, _, _ = self.build_agent("I can help summarize that for your nurse.")

        response = agent.respond("My throat feels dry.", "patient")

        self.assertEqual("I can help summarize that for your nurse.", response)

    def test_system_prompt_contains_expected_context_sections(self) -> None:
        agent, client, _ = self.build_agent("Stub response.")

        agent.respond("I feel nauseous.", "nurse")

        for section_name in [
            "AGENT.md",
            "URGENT.md",
            "POSTOP_DETAILS.md",
            "SURGERY_DETAILS.md",
            "MEDICATION_SCHEDULE.md",
        ]:
            self.assertIn(f"## {section_name}", client.last_system_prompt)

    def test_system_prompt_includes_short_response_instruction(self) -> None:
        agent, client, _ = self.build_agent("Stub response.")

        agent.respond("My pain is a little worse.", "patient")

        self.assertIn("Default to 1-3 short sentences", client.last_system_prompt)
        self.assertIn("do not give long lectures", client.last_system_prompt)

    def test_family_prompt_includes_recent_conversations(self) -> None:
        agent, client, _ = self.build_agent("Stub response.")

        with patch.object(
            agent,
            "_load_recent_conversations",
            return_value="### sample.md\n## Assistant\nPatient is stable.",
        ):
            agent.respond("How is she doing?", "family")

        self.assertIn("helping a family member", client.last_system_prompt)
        self.assertIn("## URGENT.md", client.last_system_prompt)
        self.assertIn("## RECENT_CONVERSATIONS", client.last_system_prompt)
        self.assertIn("Patient is stable.", client.last_system_prompt)

    def test_urgent_family_response_adds_nurse_escalation(self) -> None:
        agent, _, _ = self.build_agent("This sounds concerning.")

        response = agent.respond("She has chest pain and trouble breathing.", "family")

        self.assertIn("please alert the nurse right away", response.lower())

    def test_relevant_medquad_examples_are_added_to_prompt(self) -> None:
        agent, client, _ = self.build_agent("Stub response.")
        agent.medquad_examples = [
            {
                "source": "demo-fatigue.xml",
                "focus": "Fatigue after surgery",
                "question": "Why am I so tired after surgery?",
                "answer": "Fatigue can happen after surgery and should be discussed with the care team if it is worsening.",
            },
            {
                "source": "demo-rash.xml",
                "focus": "Rash",
                "question": "Why do I have a rash?",
                "answer": "A rash can have many causes.",
            },
        ]

        agent.respond("I feel very tired and weak after surgery.", "patient")

        self.assertIn("## MEDQUAD_DEMO_SUPPORT", client.last_system_prompt)
        self.assertIn("demo-fatigue.xml", client.last_system_prompt)
        self.assertNotIn("demo-rash.xml", client.last_system_prompt)


if __name__ == "__main__":
    unittest.main()
