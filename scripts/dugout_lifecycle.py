#!/usr/bin/env python3
"""Shared helpers for Dugout's repository-local lifecycle commands."""

from __future__ import annotations

import errno
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / ".dugout-install-state.json"
ENV_FILE = ROOT / ".env"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
COMPOSE_PROJECT = "dugout"
NETWORK = "moznet"

CONTAINERS = (
    "do_proxy",
    "do_portainer",
    "do_adminer",
    "do_mailpit",
    "do_dozzle",
)

VOLUMES = (
    "dugout_do_proxy_data",
    "dugout_do_proxy_letsencrypt",
    "dugout_do_portainer_data",
    "dugout_do_adminer_data",
    "dugout_do_mailpit_data",
)

SERVICE_IMAGES = (
    "jc21/nginx-proxy-manager:2.15.1",
    "portainer/portainer-ce:2.39.2",
    "adminer:5.4.2",
    "axllent/mailpit:v1.30.6",
    "amir20/dozzle:v10.6.13",
)

TOOL_IMAGES = (
    "moztopia/dugout-php:8.4",
    "moztopia/dugout-composer:2-php84",
    "moztopia/dugout-node:22",
    "moztopia/dugout-npm:10-node22",
    "moztopia/dugout-npx:10-node22",
)

RUNTIME_PATHS = (
    ROOT / "services/nginx-proxy-manager/config",
    ROOT / "services/nginx-proxy-manager/logs",
    ROOT / "services/portainer/config",
    ROOT / "services/portainer/logs",
    ROOT / "services/adminer/config",
    ROOT / "services/adminer/logs",
)

PROXY_HOSTS = (
    ("proxy.localhost", "do_proxy", 81, False),
    ("portainer.localhost", "do_portainer", 9000, False),
    ("adminer.localhost", "do_adminer", 8080, False),
    ("mailpit.localhost", "do_mailpit", 8025, False),
    ("dozzle.localhost", "do_dozzle", 8080, True),
)


class LifecycleError(RuntimeError):
    """A user-actionable lifecycle failure."""


def run(
    command: list[str],
    *,
    check: bool = True,
    capture: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        env=env,
    )


def docker_object_exists(arguments: list[str]) -> bool:
    result = run(["docker", *arguments], check=False, capture=True)
    return result.returncode == 0


def image_exists(image: str) -> bool:
    return docker_object_exists(["image", "inspect", image])


def existing_installation_resources() -> list[str]:
    found: list[str] = []
    if STATE_FILE.exists():
        found.append(f"installation state: {STATE_FILE}")
    if ENV_FILE.exists():
        found.append(f"local configuration: {ENV_FILE}")
    for container in CONTAINERS:
        if docker_object_exists(["container", "inspect", container]):
            found.append(f"container: {container}")
    for volume in VOLUMES:
        if docker_object_exists(["volume", "inspect", volume]):
            found.append(f"volume: {volume}")
    if docker_object_exists(["network", "inspect", NETWORK]):
        found.append(f"network: {NETWORK}")
    for image in TOOL_IMAGES:
        if image_exists(image):
            found.append(f"tool image: {image}")
    for path_value in cache_paths():
        path = Path(path_value)
        if path.exists() and (not path.is_dir() or any(path.iterdir())):
            found.append(f"tool cache: {path}")
    for path in RUNTIME_PATHS:
        if path.exists() and (not path.is_dir() or any(path.iterdir())):
            found.append(f"runtime data: {path.relative_to(ROOT)}")
    return found


def linux_tcp_port_has_listener(port: int) -> bool | None:
    """Return a port's listener state from procfs, or None if it is unavailable."""
    inspected = False
    expected_port = f"{port:04X}"
    for table in (Path("/proc/net/tcp"), Path("/proc/net/tcp6")):
        try:
            lines = table.read_text(encoding="ascii").splitlines()[1:]
        except FileNotFoundError:
            continue
        except OSError:
            return None
        inspected = True
        for line in lines:
            fields = line.split()
            if len(fields) < 4:
                continue
            local_address = fields[1]
            state = fields[3]
            if (
                local_address.rpartition(":")[2].upper() == expected_port
                and state == "0A"
            ):
                return True
    return False if inspected else None


def port_available(port: int) -> tuple[bool, str]:
    sockets: list[socket.socket] = []
    try:
        for family, address in (
            (socket.AF_INET, ("0.0.0.0", port)),
            (socket.AF_INET6, ("::", port)),
        ):
            try:
                listener = socket.socket(family, socket.SOCK_STREAM)
                listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                if family == socket.AF_INET6:
                    listener.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                listener.bind(address)
                sockets.append(listener)
            except OSError as error:
                listener.close()
                if error.errno == errno.EACCES and sys.platform.startswith("linux"):
                    has_listener = linux_tcp_port_has_listener(port)
                    if has_listener is False:
                        # Docker publishes the port through its daemon, so the
                        # installer's own privileged-port permission is irrelevant.
                        continue
                    if has_listener is True:
                        return False, "a TCP listener is already using it"
                return False, str(error)
    finally:
        for listener in sockets:
            listener.close()
    return True, ""


def validate_answers(email: str, password: str) -> list[str]:
    errors: list[str] = []
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        errors.append("Email must look like a valid email address.")
    if len(password) < 8:
        errors.append("Password must contain at least 8 characters.")
    if not re.fullmatch(r"[A-Za-z0-9._@%+=:,/-]+", password):
        errors.append(
            "Password may use letters, digits, and these symbols: . _ @ % + = : , / -"
        )
    return errors


def env_contents(email: str, password: str) -> str:
    return f"""# Generated by make install. This file contains local credentials.
DUGOUT_IMAGE_PREFIX=moztopia/dugout

DUGOUT_PHP_VERSION=8.4
DUGOUT_COMPOSER_VERSION=2
DUGOUT_NODE_VERSION=22
DUGOUT_NPM_VERSION=10

DUGOUT_PHP_NETWORK=moznet
DUGOUT_COMPOSER_NETWORK=bridge
DUGOUT_NODE_NETWORK=none
DUGOUT_NPM_NETWORK=bridge
DUGOUT_NPX_NETWORK=bridge

DUGOUT_NPM_API_URL=http://localhost:81
DUGOUT_NPM_EMAIL={email}
DUGOUT_NPM_PASSWORD={password}
"""


def write_private_file(path: Path, contents: str) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(contents)


def cache_paths() -> list[str]:
    cache_root = Path(
        os.environ.get(
            "XDG_CACHE_HOME",
            str(Path.home() / ".cache"),
        )
    ) / "dugout"
    return [
        str(cache_root / "composer-2-php84"),
        str(cache_root / "npm-10-node22"),
    ]


def initial_state(images_to_remove: list[str]) -> dict[str, Any]:
    return {
        "schema": 1,
        "status": "installing",
        "dugout_version": VERSION,
        "compose_project": COMPOSE_PROJECT,
        "network": NETWORK,
        "containers": list(CONTAINERS),
        "volumes": list(VOLUMES),
        "images": images_to_remove,
        "cache_paths": cache_paths(),
        "runtime_paths": [str(path) for path in RUNTIME_PATHS],
        "configuration": str(ENV_FILE),
    }


def write_state(state: dict[str, Any]) -> None:
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(state, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.chmod(0o600)
    temporary.replace(STATE_FILE)


def load_state() -> dict[str, Any]:
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LifecycleError(f"Cannot read installation state: {error}") from error
    if state.get("schema") != 1:
        raise LifecycleError("The installation state uses an unsupported schema.")
    allowed = {
        "containers": set(CONTAINERS),
        "volumes": set(VOLUMES),
        "images": set((*SERVICE_IMAGES, *TOOL_IMAGES)),
        "runtime_paths": {str(path) for path in RUNTIME_PATHS},
    }
    for key, permitted in allowed.items():
        values = state.get(key)
        if not isinstance(values, list) or not set(values).issubset(permitted):
            raise LifecycleError(
                f"The installation state contains unsafe {key} values."
            )
    if state.get("network") != NETWORK:
        raise LifecycleError("The installation state contains an unsafe network.")
    if state.get("configuration") != str(ENV_FILE):
        raise LifecycleError(
            "The installation state contains an unsafe configuration path."
        )
    return state


def api_request(
    base_url: str,
    method: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
    timeout: float = 10,
) -> Any:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
    return json.loads(body) if body else None


def wait_for_proxy_token(base_url: str, email: str, password: str) -> str:
    deadline = time.monotonic() + 180
    last_error = "service did not respond"
    while time.monotonic() < deadline:
        try:
            response = api_request(
                base_url,
                "POST",
                "/api/tokens",
                payload={"identity": email, "secret": password},
            )
            token = response.get("token") if isinstance(response, dict) else None
            if token:
                return str(token)
            last_error = "authentication response did not contain a token"
        except (OSError, urllib.error.HTTPError, json.JSONDecodeError) as error:
            last_error = str(error)
        time.sleep(2)
    raise LifecycleError(
        "Nginx Proxy Manager did not become ready within 180 seconds: "
        f"{last_error}"
    )


def seed_proxy_hosts(base_url: str, token: str) -> None:
    current = api_request(base_url, "GET", "/api/nginx/proxy-hosts", token=token)
    if not isinstance(current, list):
        raise LifecycleError(
            "Nginx Proxy Manager returned an unexpected proxy-host response."
        )
    existing_domains = {
        domain
        for host in current
        for domain in host.get("domain_names", [])
    }
    for domain, forward_host, forward_port, websocket in PROXY_HOSTS:
        if domain in existing_domains:
            print(f"  Exists:  {domain}")
            continue
        api_request(
            base_url,
            "POST",
            "/api/nginx/proxy-hosts",
            token=token,
            payload={
                "domain_names": [domain],
                "forward_scheme": "http",
                "forward_host": forward_host,
                "forward_port": forward_port,
                "certificate_id": 0,
                "ssl_forced": False,
                "hsts_enabled": False,
                "hsts_subdomains": False,
                "http2_support": False,
                "block_exploits": True,
                "caching_enabled": False,
                "allow_websocket_upgrade": websocket,
                "access_list_id": 0,
                "advanced_config": "",
                "enabled": True,
                "meta": {},
                "locations": [],
            },
        )
        print(f"  Created: {domain} -> {forward_host}:{forward_port}")


def foreign_network_containers() -> list[str]:
    result = run(
        ["docker", "network", "inspect", NETWORK, "--format", "{{json .Containers}}"],
        check=False,
        capture=True,
    )
    if result.returncode != 0:
        return []
    try:
        attached = json.loads(result.stdout.strip() or "{}")
    except json.JSONDecodeError as error:
        raise LifecycleError(
            f"Cannot inspect containers attached to {NETWORK}."
        ) from error
    known = set(CONTAINERS)
    return sorted(
        details.get("Name", identifier)
        for identifier, details in attached.items()
        if details.get("Name", identifier) not in known
    )


def remove_path(path: Path) -> None:
    resolved_root = ROOT.resolve()
    resolved = path.resolve()
    if resolved_root not in resolved.parents:
        raise LifecycleError(f"Refusing to remove path outside Dugout: {resolved}")
    if resolved.is_dir():
        shutil.rmtree(resolved)
    elif resolved.exists():
        resolved.unlink()


def fail(message: str) -> None:
    print(f"\nError: {message}", file=sys.stderr)
    raise SystemExit(1)
