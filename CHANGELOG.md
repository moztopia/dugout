# Changelog

All notable changes to Dugout will be documented in this file.

---

## [0.10.0] — 2026-08-08

### Services

- **Persistent dev services behind Traefik.** `dugout install services` sets up a Traefik reverse proxy and optional dev services — Portainer, Dozzle, Adminer, Mailpit — all accessed via `{service}.{domain}` with no exposed ports.
- **Interactive install.** Each service is prompted y/n. Use `--all-services` to skip prompts.
- **Automatic TLS.** Self-signed cert generated in `~/.dugout/certs/`. Drop in mkcert certs for browser-trusted HTTPS.
- **Config persistence.** Network name, port, and domain pattern saved to `~/.dugout/config`.
- **Service definitions in YAML.** Adding a new service is just editing `docker/services/services.yaml`.

### Repository Structure

- **Renamed `.docker/` → `docker/`** — no more hidden directories.
- **Reorganized into clear categories:**
  - `docker/shims/` — Dockerfiles for shim images
  - `docker/services/` — service definitions
  - `docker/tools/` — tools container
  - `docker/installer/` — installer image
- **`install.sh` moved to repo root.**

### Tools Container

- Added `openssl` to `dugout-tools` image for cert generation.
- `docker/` directory now copied into the container so services.yaml is available at runtime.
- Added `~/.dugout/` host mount for config and cert persistence.

---

## [0.9.0] — Skywalker — 2026-08-08

### Architecture

- **Tools run in containers.** The `dugout` CLI and all tools (barrel, etc.) run inside a `dugout-tools` Docker image (Alpine + Python3). Users never install or manage Python — it's invisible infrastructure.
- **Shims are POSIX sh.** Every command (`node`, `php`, `gcc`, etc.) is a ~10 line shell script that calls `docker run`. Zero host dependencies beyond Docker and a POSIX shell.
- **Single bootstrap.** One `curl | sh` installs the `dugout` CLI. Everything else flows through `dugout install`.

### Commands

- `dugout install [shims|tools] [name]` — download and install from GitHub
- `dugout uninstall [shims|tools] [name]` — remove shims, tools, or everything
- `dugout status` — show Docker status, PATH check, installed shims and tools
- `dugout admin shims build [tool]` — build Docker images
- `dugout admin shims push [tool]` — push to GHCR
- `dugout admin shims deploy [tool]` — build + push
- `dugout admin shims images` — list all defined images
- `dugout help` / `-h` / `--help` — works at any level

### Supported Shims

- **Node.js** — `node`, `npm`, `npx` (22, 24, 26)
- **PHP** — `php`, `composer` (8.2, 8.3, 8.4, 8.5)
- **MySQL** — `mysql` (8.4)
- **MariaDB** — `mariadb` (10.11, 11.4)
- **PostgreSQL** — `psql` (16, 17)
- **Redis** — `redis-cli` (7.2, 7.4)
- **FFmpeg** — `ffmpeg`, `ffprobe`
- **SQLite** — `sqlite3`
- **C/C++/Assembly** — `gcc`, `g++`, `make`, `cmake`, `nasm`, `fasm`, `gdb`
- **Go** — `go` (1.25, 1.26)
- **Rust** — `rustc`, `cargo` (stable)

### Tools

- **dugout** — CLI for managing shims, tools, and images
- **barrel** — generates barrel/index files from `barrel.yaml` configs

### Platform Support

- ✓ Linux (tested)
- ✓ macOS (should work)
- ⚠ WSL (untested)
- ⚠ Git Bash / Windows (untested)
