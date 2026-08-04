# Changelog

## Unreleased

### Added

- per-utility `.env` switches for enabling or disabling Portainer, Adminer,
  Mailpit, and Dozzle;
- configurable loopback-only ports for every web interface and Mailpit SMTP;
- Compose configuration coverage for service switches, loopback bindings, and
  the absence of proxy wiring;
- Markdown linting as part of the canonical `make test` validation.

### Changed

- setup is now `cp .env.example .env` followed by `make up`;
- service lifecycle commands are now `make up`, `down`, `stop`, `restart`, and
  `status`;
- browser utilities now use direct `127.0.0.1` endpoints instead of routed
  hostnames;
- command shims are repository-local and activated only by VS Code workspace
  settings; global runner and shim installation has been removed;
- the root README is now the canonical setup guide and opens as VS
  Code's startup editor when Dugout is opened directly.

### Removed

- the installer, uninstaller, installation state, and their lifecycle tests;
- all Traefik labels, proxy configuration, and the external proxy network;
- obsolete proxy credentials and proxy-related runner configuration.

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
