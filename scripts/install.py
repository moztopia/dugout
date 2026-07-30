#!/usr/bin/env python3
"""Install Dugout's services and local tool images."""

from __future__ import annotations

import getpass
import shutil
import sys

from dugout_lifecycle import (
    ENV_FILE,
    SERVICE_IMAGES,
    STATE_FILE,
    TOOL_IMAGES,
    VERSION,
    LifecycleError,
    env_contents,
    existing_installation_resources,
    fail,
    image_exists,
    initial_state,
    port_available,
    run,
    seed_proxy_hosts,
    validate_answers,
    wait_for_proxy_token,
    write_private_file,
    write_state,
)


def require_interactive() -> None:
    if not sys.stdin.isatty():
        fail("make install must run in an interactive terminal.")


def preflight() -> list[str]:
    print("Preflight checks")
    print("  Dugout will stop before changing anything when a requirement fails.")

    missing = [
        command
        for command in ("docker", "git", "make", "python3")
        if shutil.which(command) is None
    ]
    if missing:
        fail("Missing required commands: " + ", ".join(missing))
    if sys.version_info < (3, 9):
        fail("Python 3.9 or newer is required.")

    compose = run(["docker", "compose", "version"], check=False, capture=True)
    if compose.returncode != 0:
        fail("Docker Compose plugin is unavailable. Install it and rerun make install.")
    daemon = run(["docker", "info"], check=False, capture=True)
    if daemon.returncode != 0:
        fail("The Docker daemon is unavailable. Start Docker and rerun make install.")

    free_bytes = shutil.disk_usage(ENV_FILE.parent).free
    required_bytes = 12 * 1024 * 1024 * 1024
    if free_bytes < required_bytes:
        fail(
            "Dugout requires at least 12 GiB of free disk space for its tool "
            f"and service images; only {free_bytes / 1024**3:.1f} GiB is available."
        )

    existing = existing_installation_resources()
    if existing:
        formatted = "\n".join(f"  - {resource}" for resource in existing)
        fail(
            "Dugout is already installed or partially installed:\n"
            f"{formatted}\n"
            "Run make uninstall to remove it, or resolve the listed resources "
            "before trying again."
        )

    for port in (80, 81):
        available, reason = port_available(port)
        if not available:
            fail(
                f"TCP port {port} is unavailable ({reason}). Stop the process "
                "using it and rerun make install."
            )

    images_to_remove = [
        image
        for image in (*SERVICE_IMAGES, *TOOL_IMAGES)
        if not image_exists(image)
    ]
    print(
        "  Docker, Compose, required commands, disk space, ports 80/81, "
        "and resource names are clear."
    )
    return images_to_remove


def ask_questions() -> tuple[str, str, str]:
    print("\nInstallation questions")
    print(
        "\nUsername\n"
        "  Used as the administrator name for Dugout's local MinIO object store."
    )
    username = input("  Username: ").strip()

    print(
        "\nEmail\n"
        "  Used to create the Nginx Proxy Manager administrator account."
    )
    email = input("  Email: ").strip()

    print(
        "\nPassword\n"
        "  Shared by the local MinIO and Nginx Proxy Manager administrator "
        "accounts. It is stored only in Dugout's ignored .env file."
    )
    password = getpass.getpass("  Password: ")
    confirmation = getpass.getpass("  Confirm password: ")
    if password != confirmation:
        fail("The passwords did not match. Nothing was installed.")

    errors = validate_answers(username, email, password)
    if errors:
        fail("\n".join(errors) + "\nNothing was installed.")
    return username, email, password


def confirm(username: str, email: str) -> None:
    print(
        "\nInstallation summary\n"
        f"  Dugout version:       {VERSION}\n"
        f"  MinIO administrator:  {username}\n"
        f"  Proxy administrator:  {email}\n"
        "  Published ports:      80 and 81\n"
        "  Docker network:       moznet\n"
        "  Tool images:          PHP, Composer, Node, npm, npx, Dart, Flutter\n"
        "  Services:             Proxy, Portainer, Adminer, Mailpit, Dozzle, MinIO\n"
        "\nNo commands or shims will be installed globally."
    )
    answer = input("\nInstall Dugout now? [y/N] ").strip().lower()
    if answer not in {"y", "yes"}:
        print("Installation cancelled. Nothing was changed.")
        raise SystemExit(0)


def verify_services() -> None:
    expected = {"proxy", "portainer", "adminer", "mailpit", "dozzle", "minio"}
    result = run(
        [
            "docker",
            "compose",
            "ps",
            "--services",
            "--filter",
            "status=running",
        ],
        capture=True,
    )
    running = set(result.stdout.splitlines())
    missing = sorted(expected - running)
    if missing:
        raise LifecycleError(
            "These services are not running: " + ", ".join(missing)
        )


def install() -> None:
    require_interactive()
    images_to_remove = preflight()
    username, email, password = ask_questions()
    confirm(username, email)

    state = initial_state(images_to_remove)
    write_state(state)
    try:
        print("\nWriting private local configuration...")
        write_private_file(ENV_FILE, env_contents(username, email, password))

        print("\nBuilding Dugout tool images. Flutter can take several minutes...")
        run(["make", "build-tools"])

        print("\nStarting Dugout services...")
        run(["docker", "compose", "up", "--detach"])

        print("\nWaiting for Nginx Proxy Manager and authenticating...")
        token = wait_for_proxy_token("http://localhost:81", email, password)

        print("\nCreating standard proxy hosts...")
        seed_proxy_hosts("http://localhost:81", token)

        print("\nVerifying the installation...")
        verify_services()
        run(["docker", "compose", "ps"])
        run(["make", "test"])
        run(["./bin/dug", "doctor"])

        state["status"] = "installed"
        write_state(state)
    except Exception as error:
        fail(
            f"Installation did not complete: {error}\n"
            f"Partial installation state is recorded in {STATE_FILE}. "
            "Run make uninstall before retrying."
        )

    print(
        "\nDugout installation complete.\n"
        "Open this repository in VS Code. New integrated terminals use the "
        "repository-local Dugout shims; terminals elsewhere are unchanged."
    )


if __name__ == "__main__":
    try:
        install()
    except KeyboardInterrupt:
        print("\nInstallation cancelled.", file=sys.stderr)
        raise SystemExit(130)
