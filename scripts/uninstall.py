#!/usr/bin/env python3
"""Completely remove a Dugout installation."""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

from dugout_lifecycle import (
    CONTAINERS,
    ENV_FILE,
    NETWORK,
    RUNTIME_PATHS,
    SERVICE_IMAGES,
    STATE_FILE,
    TOOL_IMAGES,
    VOLUMES,
    LifecycleError,
    cache_paths,
    existing_installation_resources,
    fail,
    foreign_network_containers,
    image_exists,
    load_state,
    remove_path,
    run,
)


def require_interactive() -> None:
    if not sys.stdin.isatty():
        fail("make uninstall must run in an interactive terminal.")


def removal_plan() -> dict[str, object]:
    if STATE_FILE.exists():
        return load_state()
    existing = existing_installation_resources()
    if not existing:
        fail("Dugout is not installed.")
    print(
        "No installation state file was found. A legacy or partial Dugout "
        "installation was detected and will be handled using the known "
        "repository resource names."
    )
    return {
        "schema": 1,
        "status": "legacy",
        "network": NETWORK,
        "containers": list(CONTAINERS),
        "volumes": list(VOLUMES),
        "images": list((*SERVICE_IMAGES, *TOOL_IMAGES)),
        "cache_paths": cache_paths(),
        "runtime_paths": [str(path) for path in RUNTIME_PATHS],
        "configuration": str(ENV_FILE),
    }


def confirm() -> None:
    print(
        "\nDANGER: COMPLETE DUGOUT REMOVAL\n"
        "\nThis permanently deletes:\n"
        "  - every Dugout container and locally owned image;\n"
        "  - all Nginx Proxy Manager hosts, certificates, and configuration;\n"
        "  - all Portainer and Adminer state;\n"
        "  - all captured Mailpit messages;\n"
        "  - Dugout tool caches and local credentials;\n"
        "  - Dugout's moznet network.\n"
        "\nThis data cannot be recovered unless you made a separate backup."
    )
    answer = input('\nType "DELETE DUGOUT" to continue: ')
    if answer != "DELETE DUGOUT":
        print("Uninstall cancelled. Nothing was removed.")
        raise SystemExit(0)


def uninstall() -> None:
    require_interactive()
    plan = removal_plan()

    daemon = run(["docker", "info"], check=False, capture=True)
    if daemon.returncode != 0:
        fail("The Docker daemon is unavailable. Start Docker and rerun make uninstall.")

    foreign = foreign_network_containers()
    if foreign:
        fail(
            "Cannot uninstall while non-Dugout containers are attached to "
            f"{NETWORK}:\n" + "\n".join(f"  - {name}" for name in foreign)
        )

    confirm()

    print("\nStopping and removing Dugout services, volumes, and network...")
    down = run(
        ["docker", "compose", "down", "--volumes", "--remove-orphans"],
        check=False,
    )
    if down.returncode != 0:
        fail("Docker Compose could not remove the Dugout service plane.")

    for container in plan.get("containers", []):
        run(["docker", "container", "rm", "--force", str(container)], check=False)
    for volume in plan.get("volumes", []):
        run(["docker", "volume", "rm", str(volume)], check=False)
    run(["docker", "network", "rm", str(plan.get("network", NETWORK))], check=False)

    print("\nRemoving images created by this installation...")
    for image in plan.get("images", []):
        image_name = str(image)
        if not image_exists(image_name):
            continue
        result = run(["docker", "image", "rm", image_name], check=False)
        if result.returncode != 0:
            fail(
                f"Could not remove image {image_name}. It may be used by another "
                "container; resolve that conflict and rerun make uninstall."
            )

    print("\nRemoving Dugout caches, runtime files, credentials, and state...")
    for path_value in plan.get("cache_paths", []):
        path = Path(str(path_value)).expanduser().resolve()
        cache_parent = (Path.home() / ".cache" / "dugout").resolve()
        configured_parent = Path(
            os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
        ).resolve() / "dugout"
        if cache_parent not in path.parents and configured_parent not in path.parents:
            fail(f"Refusing to remove unexpected cache path: {path}")
        if path.is_dir():
            shutil.rmtree(path)

    for path_value in plan.get("runtime_paths", []):
        remove_path(Path(str(path_value)))
    ENV_FILE.unlink(missing_ok=True)
    STATE_FILE.unlink(missing_ok=True)

    remaining = existing_installation_resources()
    if remaining:
        fail(
            "Uninstall is incomplete. Resolve these remaining resources and rerun:\n"
            + "\n".join(f"  - {resource}" for resource in remaining)
        )

    print(
        "\nDugout was completely uninstalled.\n"
        "The Git checkout and its committed source files were preserved."
    )


if __name__ == "__main__":
    try:
        uninstall()
    except (LifecycleError, json.JSONDecodeError) as error:
        fail(str(error))
    except KeyboardInterrupt:
        print("\nUninstall cancelled.", file=sys.stderr)
        raise SystemExit(130)
