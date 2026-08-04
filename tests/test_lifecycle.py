#!/usr/bin/env python3
"""Fast tests for lifecycle data and safety rules."""

from __future__ import annotations

import errno
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
    def test_free_privileged_port_is_available_to_docker(self) -> None:
        listener = unittest.mock.MagicMock()
        listener.bind.side_effect = PermissionError(
            errno.EACCES,
            "Permission denied",
        )
        with (
            patch.object(lifecycle.socket, "socket", return_value=listener),
            patch.object(lifecycle.sys, "platform", "linux"),
            patch.object(
                lifecycle,
                "linux_tcp_port_has_listener",
                return_value=False,
            ),
        ):
            self.assertEqual(lifecycle.port_available(80), (True, ""))
        self.assertEqual(listener.close.call_count, 2)

    def test_occupied_privileged_port_is_unavailable(self) -> None:
        listener = unittest.mock.MagicMock()
        listener.bind.side_effect = PermissionError(
            errno.EACCES,
            "Permission denied",
        )
        with (
            patch.object(lifecycle.socket, "socket", return_value=listener),
            patch.object(lifecycle.sys, "platform", "linux"),
            patch.object(
                lifecycle,
                "linux_tcp_port_has_listener",
                return_value=True,
            ),
        ):
            available, reason = lifecycle.port_available(80)
        self.assertFalse(available)
        self.assertIn("already using", reason)

    def test_valid_answers(self) -> None:
        self.assertEqual(
            lifecycle.validate_answers(
                "developer@example.com",
                "long-password",
            ),
            [],
        )

    def test_invalid_answers_are_explained(self) -> None:
        errors = lifecycle.validate_answers("invalid", "short")
        self.assertEqual(len(errors), 2)

    def test_compose_unsafe_password_is_rejected(self) -> None:
        errors = lifecycle.validate_answers(
            "developer@example.com",
            "unsafe$password",
        )
        self.assertTrue(any("symbols" in error for error in errors))

    def test_generated_environment_contains_answers(self) -> None:
        contents = lifecycle.env_contents(
            "developer@example.com",
            "long-password",
        )
        self.assertIn("DUGOUT_NPM_EMAIL=developer@example.com\n", contents)
        self.assertEqual(contents.count("long-password"), 1)

    def test_installation_state_contains_no_credentials(self) -> None:
        state = lifecycle.initial_state(["example/image:1"])
        serialized = json.dumps(state)
        self.assertNotIn("password", serialized.lower())
        self.assertNotIn("email", serialized.lower())
        self.assertEqual(state["status"], "installing")
        self.assertEqual(state["schema"], 1)

    def test_reusable_tool_artifacts_are_not_an_existing_installation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache = root / "npm-10-node22"
            cache.mkdir()
            (cache / "cached-package").write_text("data", encoding="utf-8")
            with (
                patch.object(lifecycle, "STATE_FILE", root / "state.json"),
                patch.object(lifecycle, "ENV_FILE", root / ".env"),
                patch.object(lifecycle, "CONTAINERS", ()),
                patch.object(lifecycle, "VOLUMES", ()),
                patch.object(lifecycle, "TOOL_IMAGES", ("dugout/tool:1",)),
                patch.object(lifecycle, "RUNTIME_PATHS", ()),
                patch.object(lifecycle, "cache_paths", return_value=[str(cache)]),
                patch.object(lifecycle, "docker_object_exists", return_value=False),
            ):
                self.assertEqual(lifecycle.existing_installation_resources(), [])

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
