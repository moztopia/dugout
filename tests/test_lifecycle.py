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
import uninstall as uninstall_command  # noqa: E402


class LifecycleTests(unittest.TestCase):
    def test_uninstall_removes_an_owned_image_that_exists(self) -> None:
        completed = type("Completed", (), {"returncode": 0})()
        plan = {
            "containers": [],
            "volumes": [],
            "network": lifecycle.NETWORK,
            "images": [lifecycle.TOOL_IMAGES[0]],
            "cache_paths": [],
            "runtime_paths": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.object(uninstall_command, "require_interactive"),
                patch.object(uninstall_command, "removal_plan", return_value=plan),
                patch.object(uninstall_command, "foreign_network_containers", return_value=[]),
                patch.object(uninstall_command, "confirm"),
                patch.object(uninstall_command, "image_exists", return_value=True),
                patch.object(uninstall_command, "existing_installation_resources", return_value=[]),
                patch.object(uninstall_command, "ENV_FILE", root / ".env"),
                patch.object(uninstall_command, "STATE_FILE", root / "state.json"),
                patch.object(uninstall_command, "run", return_value=completed) as run,
            ):
                uninstall_command.uninstall()

        run.assert_any_call(
            ["docker", "image", "rm", lifecycle.TOOL_IMAGES[0]],
            check=False,
        )

    def test_generated_environment_has_no_proxy_credentials(self) -> None:
        contents = lifecycle.env_contents()
        self.assertNotIn("DUGOUT_NPM_API_URL", contents)
        self.assertNotIn("DUGOUT_NPM_EMAIL", contents)
        self.assertNotIn("DUGOUT_NPM_PASSWORD", contents)
        self.assertIn("DUGOUT_IMAGE_PREFIX=moztopia/dugout\n", contents)
        self.assertIn("TRAEFIK_NETWORK_NAME=web-proxy\n", contents)

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

    def test_legacy_proxy_state_is_accepted_for_uninstall(self) -> None:
        state = lifecycle.initial_state([])
        state["volumes"] = list(lifecycle.LEGACY_PROXY_VOLUMES)
        state["images"] = list(lifecycle.LEGACY_PROXY_IMAGES)
        state["runtime_paths"] = [
            str(path) for path in lifecycle.LEGACY_PROXY_RUNTIME_PATHS
        ]
        with tempfile.TemporaryDirectory() as directory:
            state_file = Path(directory) / "state.json"
            state_file.write_text(json.dumps(state), encoding="utf-8")
            with patch.object(lifecycle, "STATE_FILE", state_file):
                self.assertEqual(lifecycle.load_state()["images"], state["images"])

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

    def test_compose_uses_standalone_traefik_network_and_routes(self) -> None:
        compose = (ROOT / "docker-compose.yaml").read_text(encoding="utf-8")
        self.assertTrue(compose.startswith("name: dugout\n"))
        self.assertNotIn("image: traefik:", compose)
        self.assertNotIn("container_name: do_proxy", compose)
        self.assertIn("traefik.docker.network=${TRAEFIK_NETWORK_NAME:-web-proxy}", compose)
        self.assertIn("name: ${TRAEFIK_NETWORK_NAME:-web-proxy}", compose)
        for hostname in (
            "portainer.localhost.moztopia.com",
            "adminer.localhost.moztopia.com",
            "mailpit.localhost.moztopia.com",
            "dozzle.localhost.moztopia.com",
        ):
            self.assertIn(f"Host(`{hostname}`)", compose)

    def test_vscode_activation_is_repository_local(self) -> None:
        settings = json.loads(
            (ROOT / ".vscode/settings.json").read_text(encoding="utf-8")
        )
        self.assertEqual(settings["workbench.startupEditor"], "readme")
        self.assertEqual(
            settings["terminal.integrated.env.linux"]["PATH"],
            "${workspaceFolder}/bin:${env:PATH}",
        )
        self.assertTrue((ROOT / "bin/barrel").is_file())
        self.assertTrue((ROOT / "tools/barrel/barrel").is_file())


if __name__ == "__main__":
    unittest.main()
