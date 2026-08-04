# Changelog

## Unreleased

### Added

- configurable attachment to the standalone Traefik external network for all
  browser-facing services;
- Markdown linting as part of the canonical `make test` validation.

### Changed

- reverse-proxy ownership has moved to the standalone Traefik stack; Dugout's
  browser services now join its configurable external network and declare
  their routes with Docker Compose labels;
- `make install` now performs the complete interactive Dugout installation,
  including preflight checks, private configuration, all tool builds, service
  startup, validation, and ownership-state recording;
- `make uninstall` now reverses the complete installation after an explicit
  data-loss confirmation and refuses to remove `moznet` while another
  container is attached;
- command shims are repository-local and activated only by VS Code workspace
  settings; global runner and shim installation has been removed;
- the root README is now the canonical installation guide and opens as VS
  Code's startup editor when Dugout is opened directly.

### Removed

- the embedded reverse proxy, automatic certificate/DNS management, and host
  port ownership from the Dugout lifecycle;
- obsolete proxy-port availability checks from installation and lifecycle
  tests.

## 1.1.0 — Double (2026-07-30)

Double strengthens both halves of Dugout: the long-running service plane and
the short-lived command-tool plane.

### Added

- Mailpit for captured development email;
- Dozzle for live container logs;
- MinIO for local S3-compatible object storage;
- `make services-up`, `services-stop`, `services-restart`, and
  `services-status` lifecycle commands;
- `dug version`, reporting `dug 1.1.0 (Double)`;
- pinned Dart 3.12.2 and Flutter 3.44.2 command images and shims;
- command-line Android SDK support for Flutter analysis, tests, and builds,
  without Android Studio or device privileges;
- a documented `services/` layout for runtime files and private backups.

### Changed

- Dugout Compose now creates and owns the globally named `moznet` network;
- application projects continue consuming `moznet` as an external network;
- service-specific bind mounts now live under `services/<service>/`;
- default service images are pinned to the versions validated for this
  release instead of moving `latest` tags;
- installing the runner copies the active local configuration on first
  install;
- the root README now provides an end-to-end fresh-machine installation guide.

### Security

- only Nginx Proxy Manager ports 80 and 81 are published to the host;
- service UIs and application endpoints remain internal to `moznet`;
- MinIO development credentials are configurable through the ignored `.env`;
- service runtime data, logs, and backups remain excluded from Git.
