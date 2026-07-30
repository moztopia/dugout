# Changelog

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
- a documented `services/` layout for runtime files and private backups.

### Changed

- Dugout Compose now creates and owns the globally named `moznet` network;
- application projects continue consuming `moznet` as an external network;
- service-specific bind mounts now live under `services/<service>/`;
- default service images are pinned to the versions validated for this
  release instead of moving `latest` tags;
- installing the runner copies the active local configuration on first
  install;
- the root README now provides an end-to-end fresh-machine quick start.

### Security

- only Nginx Proxy Manager ports 80 and 81 are published to the host;
- service UIs and application endpoints remain internal to `moznet`;
- MinIO development credentials are configurable through the ignored `.env`;
- service runtime data, logs, and backups remain excluded from Git.
