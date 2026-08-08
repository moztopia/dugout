#!/usr/bin/env python3
"""dugout_core — shared functions for all dugout tools."""

import os
import sys
import subprocess

PREFIX = "ghcr.io/moztopia/dugout"
REPO = "https://github.com/moztopia/dugout/raw/main"
INSTALL_DIR = os.environ.get("DUGOUT_HOSTBIN", os.path.expanduser("~/.local/bin/dugout"))


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
