#!/usr/bin/env python3
"""dugout_core — shared functions for all dugout tools."""

import os
import sys
import subprocess

PREFIX = "ghcr.io/moztopia/dugout"
REPO = "https://github.com/moztopia/dugout/raw/main"
INSTALL_DIR = os.environ.get("DUGOUT_HOSTBIN", os.path.expanduser("~/.local/bin/dugout"))
DUGOUT_HOME = os.environ.get("DUGOUT_HOME", os.path.expanduser("~/.dugout"))
CONFIG_FILE = os.path.join(DUGOUT_HOME, "config")


def msg(text):
    print(f"  {text}")


def success(text):
    print(f"  ✓ {text}")


def fail(text):
    print(f"  ✗ {text}")


def header(text):
    print(f"\n  {text}\n")


def done():
    print("\n  Done.\n")


def confirm(prompt="Continue?"):
    try:
        response = input(f"  {prompt} [y/N] ").strip().lower()
    except EOFError:
        response = ""
    if response not in ("y", "yes"):
        print("  Aborted.\n")
        sys.exit(0)


def prompt_yn(question, default=True):
    """Ask a yes/no question. Returns True/False."""
    hint = "Y/n" if default else "y/N"
    try:
        response = input(f"  {question} [{hint}] ").strip().lower()
    except EOFError:
        response = ""
    if not response:
        return default
    return response in ("y", "yes")


def prompt(question, default=""):
    try:
        hint = f" [{default}]" if default else ""
        answer = input(f"  {question}{hint}: ").strip()
    except EOFError:
        answer = ""
    return answer or default


def require_maintainer():
    print("\n  Maintainer operation — requires the dugout repo and ghcr.io write access.")
    confirm("Continue?")


def download_to(dest, url):
    subprocess.run(["curl", "-fsSL", url, "-o", dest], check=True)
    os.chmod(dest, 0o755)


def install_from_repo(src_path, dest_name=None):
    if dest_name is None:
        dest_name = os.path.basename(src_path)
    os.makedirs(INSTALL_DIR, exist_ok=True)
    download_to(os.path.join(INSTALL_DIR, dest_name), f"{REPO}/{src_path}")
    success(dest_name)


def check_help(args):
    return any(a in ("help", "-h", "--help") for a in args)


def run(cmd, **kwargs):
    """Run a shell command, passing through stdout/stderr."""
    return subprocess.run(cmd, **kwargs)


def run_quiet(cmd):
    """Run a command and return (returncode, stdout)."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip()


# ── Config ───────────────────────────────────────────────────

def load_config():
    """Load config from ~/.dugout/config as key=value pairs."""
    config = {}
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    config[key.strip()] = value.strip()
    return config


def save_config(config):
    """Save config to ~/.dugout/config."""
    os.makedirs(DUGOUT_HOME, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        f.write("# Dugout configuration\n")
        for key, value in sorted(config.items()):
            f.write(f"{key}={value}\n")
