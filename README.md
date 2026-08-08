<p align="center">
  <img src="logo.png" alt="Dugout" width="200">
</p>

# Dugout

Containerized development tools. No installers, no version managers, no host
pollution — just Docker.

When you run `npm install`, Dugout spins up a disposable container with the
right Node version, mounts your project, runs the command, and disappears.
Nothing is installed on your machine except a few tiny shell scripts.

---

## Install

```sh
curl -fsSL https://github.com/moztopia/dugout/raw/main/install.sh | sh
```

Make sure `~/.local/bin/dugout` is in your `PATH`. Add this to your shell
config if it isn't already:

```sh
export PATH="$HOME/.local/bin/dugout:$PATH"
```

Then install shims and tools:

```sh
dugout install shims
dugout install tools
```

Verify:

```sh
dugout status
node --version
php --version
```

## Uninstall

```sh
dugout uninstall
```

That's everything. No config files, no daemons, no leftover state.

---

## How It Works

Each command in `~/.local/bin/dugout/` is a ~10 line shell script that calls
`docker run` with the right image and mounts your current directory:

```demo
      you: npm install
     shim: docker run --rm ghcr.io/moztopia/dugout-node:24 npm install
   result: node_modules/ created in your project directory
```

The container runs as your user (same UID/GID), so files it creates are owned
by you. The container is removed immediately after the command finishes.

## Requirements

- Docker
- A POSIX-compliant shell (`sh`, `bash`, `zsh`, etc.)

All shims and the `dugout` CLI are written in POSIX sh — no runtime
dependencies beyond Docker and a shell.

### Platform Support

| Platform | Status |
| --- | --- |
| Linux | ✓ Tested |
| macOS | ✓ Should work (untested) |
| WSL | ⚠ Untested — Windows is evil and nasty |
| Git Bash (Windows) | ⚠ Untested |

---

## Switching Versions

Set an environment variable to change which version runs:

```sh
export DUGOUT_NODE_VERSION=22
export DUGOUT_PHP_VERSION=8.3
export DUGOUT_MARIADB_VERSION=10.11
export DUGOUT_GO_VERSION=1.25
```

Versions can be set globally in your shell config, per-session, or per-command:

```sh
# Global default (add to ~/.bashrc)
export DUGOUT_PYTHON_VERSION=3.14

# One-off command
DUGOUT_PHP_VERSION=8.2 php --version
```

---

## Repository Structure

```tree
install.sh                    Curl bootstrap installer
.docker/
  images/                     Image recipes (Dockerfiles)
bin/                          Shims — one per command (POSIX sh)
tools/
  dugout_core.py              Shared Python library
  dugout/dugout               Dugout CLI (Python, runs in container)
  barrel/barrel               Barrel tool (Python, runs in container)
```

## For Maintainers

Build and push everything:

```sh
./bin/dugout admin shims deploy
```

Or target a specific tool:

```sh
./bin/dugout admin shims build node
./bin/dugout admin shims push redis
./bin/dugout admin shims deploy cdev
```

List all defined images:

```sh
./bin/dugout admin shims images
```

---

## Supported Tools and Versions

### Node.js

| Shim | Image | Env Variable |
| --- | --- | --- |
| `node` | `ghcr.io/moztopia/dugout-node` | `DUGOUT_NODE_VERSION` |
| `npm` | `ghcr.io/moztopia/dugout-node` | `DUGOUT_NODE_VERSION` |
| `npx` | `ghcr.io/moztopia/dugout-node` | `DUGOUT_NODE_VERSION` |

| Version | Status |
| --- | --- |
| 22 | Supported |
| **24** | **Default** |
| 26 | Supported |

---

### PHP

| Shim | Image | Env Variable |
| --- | --- | --- |
| `php` | `ghcr.io/moztopia/dugout-php` | `DUGOUT_PHP_VERSION` |
| `composer` | `ghcr.io/moztopia/dugout-php` | `DUGOUT_PHP_VERSION` |

| Version | Status |
| --- | --- |
| 8.2 | Supported |
| 8.3 | Supported |
| **8.4** | **Default** |
| 8.5 | Supported |

---

### MySQL

| Shim | Image | Env Variable |
| --- | --- | --- |
| `mysql` | `ghcr.io/moztopia/dugout-mysql` | `DUGOUT_MYSQL_VERSION` |

| Version | Status |
| --- | --- |
| **8.4** | **Default** (LTS until 2032) |

---

### MariaDB

| Shim | Image | Env Variable |
| --- | --- | --- |
| `mariadb` | `ghcr.io/moztopia/dugout-mariadb` | `DUGOUT_MARIADB_VERSION` |

| Version | Status |
| --- | --- |
| 10.11 | Supported (LTS until 2028) |
| **11.4** | **Default** (LTS) |

---

### PostgreSQL

| Shim | Image | Env Variable |
| --- | --- | --- |
| `psql` | `ghcr.io/moztopia/dugout-psql` | `DUGOUT_PSQL_VERSION` |

| Version | Status |
| --- | --- |
| 16 | Supported |
| **17** | **Default** |

---

### Redis

| Shim | Image | Env Variable |
| --- | --- | --- |
| `redis-cli` | `ghcr.io/moztopia/dugout-redis` | `DUGOUT_REDIS_VERSION` |

| Version | Status |
| --- | --- |
| 7.2 | Supported (LTS) |
| **7.4** | **Default** |

---

### FFmpeg

| Shim | Image | Env Variable |
| --- | --- | --- |
| `ffmpeg` | `ghcr.io/moztopia/dugout-ffmpeg` | — |
| `ffprobe` | `ghcr.io/moztopia/dugout-ffmpeg` | — |

| Version | Status |
| --- | --- |
| **latest** | **Alpine-packaged** |

---

### SQLite

| Shim | Image | Env Variable |
| --- | --- | --- |
| `sqlite3` | `ghcr.io/moztopia/dugout-sqlite` | — |

| Version | Status |
| --- | --- |
| **latest** | **Alpine-packaged** |

---

### C/C++ / Assembly

| Shim | Image | Env Variable |
| --- | --- | --- |
| `gcc` | `ghcr.io/moztopia/dugout-cdev` | — |
| `g++` | `ghcr.io/moztopia/dugout-cdev` | — |
| `make` | `ghcr.io/moztopia/dugout-cdev` | — |
| `cmake` | `ghcr.io/moztopia/dugout-cdev` | — |
| `nasm` | `ghcr.io/moztopia/dugout-cdev` | — |
| `fasm` | `ghcr.io/moztopia/dugout-cdev` | — |
| `gdb` | `ghcr.io/moztopia/dugout-cdev` | — |

| Version | Status |
| --- | --- |
| **latest** | **Alpine-packaged** (gcc, g++, make, cmake, nasm, gdb, binutils, linux-headers) |

FASM installed from [flatassembler.net](https://flatassembler.net).
All 7 shims share a single image.

---

### Go

| Shim | Image | Env Variable |
| --- | --- | --- |
| `go` | `ghcr.io/moztopia/dugout-go` | `DUGOUT_GO_VERSION` |

| Version | Status |
| --- | --- |
| 1.25 | Supported |
| **1.26** | **Default** |

---

### Rust

| Shim | Image | Env Variable |
| --- | --- | --- |
| `rustc` | `ghcr.io/moztopia/dugout-rust` | — |
| `cargo` | `ghcr.io/moztopia/dugout-rust` | — |

| Version | Status |
| --- | --- |
| **stable** | **Default** (rolling) |
