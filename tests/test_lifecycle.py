#!/usr/bin/env python3
"""Fast tests for lifecycle data and safety rules."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import dugout_lifecycle as lifecycle  # noqa: E402


class LifecycleTests(unittest.TestCase):
    def test_valid_answers(self) -> None:
        self.assertEqual(
            lifecycle.validate_answers(
                "developer",
                "developer@example.com",
                "long-password",
            ),
            [],
        )

    def test_invalid_answers_are_explained(self) -> None:
        errors = lifecycle.validate_answers("x", "invalid", "short")
        self.assertEqual(len(errors), 3)

    def test_compose_unsafe_password_is_rejected(self) -> None:
        errors = lifecycle.validate_answers(
            "developer",
            "developer@example.com",
            "unsafe$password",
        )
        self.assertTrue(any("symbols" in error for error in errors))

    def test_generated_environment_contains_answers(self) -> None:
        contents = lifecycle.env_contents(
            "developer",
            "developer@example.com",
            "long-password",
        )
        self.assertIn("DUGOUT_MINIO_ROOT_USER=developer\n", contents)
        self.assertIn("DUGOUT_NPM_EMAIL=developer@example.com\n", contents)
        self.assertEqual(contents.count("long-password"), 2)

    def test_installation_state_contains_no_credentials(self) -> None:
        state = lifecycle.initial_state(["example/image:1"])
        serialized = json.dumps(state)
        self.assertNotIn("password", serialized.lower())
        self.assertNotIn("email", serialized.lower())
        self.assertEqual(state["status"], "installing")
        self.assertEqual(state["schema"], 1)

    def test_unsafe_state_is_rejected(self) -> None:
        state = lifecycle.initial_state(["example/image:1"])
        state["images"] = ["unrelated/private-image:latest"]
        with tempfile.TemporaryDirectory() as directory:
            state_file = Path(directory) / "state.json"
            state_file.write_text(json.dumps(state), encoding="utf-8")
            with patch.object(lifecycle, "STATE_FILE", state_file):
                with self.assertRaises(lifecycle.LifecycleError):
                    lifecycle.load_state()

    def test_foreign_network_containers_are_detected(self) -> None:
        network_data = {
            "known": {"Name": "do_proxy"},
            "foreign": {"Name": "application_api"},
        }
        completed = type(
            "Completed",
            (),
            {"returncode": 0, "stdout": json.dumps(network_data)},
        )()
        with patch.object(lifecycle, "run", return_value=completed):
            self.assertEqual(
                lifecycle.foreign_network_containers(),
                ["application_api"],
            )

    def test_compose_has_fixed_project_and_automatic_admin(self) -> None:
        compose = (ROOT / "docker-compose.yaml").read_text(encoding="utf-8")
        self.assertTrue(compose.startswith("name: dugout\n"))
        self.assertIn("INITIAL_ADMIN_EMAIL: ${DUGOUT_NPM_EMAIL}", compose)
        self.assertIn("INITIAL_ADMIN_PASSWORD: ${DUGOUT_NPM_PASSWORD}", compose)

    def test_vscode_activation_is_repository_local(self) -> None:
        settings = json.loads(
            (ROOT / ".vscode/settings.json").read_text(encoding="utf-8")
        )
        self.assertEqual(settings["workbench.startupEditor"], "readme")
        self.assertEqual(
            settings["terminal.integrated.env.linux"]["PATH"],
            "${workspaceFolder}/bin:${env:PATH}",
        )


if __name__ == "__main__":
    unittest.main()
