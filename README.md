# Dugout

Current release: **1.1.0 — Double**

Dugout is Moztopia's local development service plane and containerized command
toolbox. It owns the shared local services, the globally named `moznet` Docker
network, and command images for PHP, Composer, Node.js, npm, npx, Dart, and
Flutter.

## Quick start

Follow the [Dugout quick-start guide](QUICK-START.md) to configure the
development environment, start the shared services, and build the command
tools. Installing the command shims for use outside activated VS Code
workspaces—and adding `~/.local/bin` to the workstation `PATH`—is optional.

## Everyday commands

```sh
make services-up       # create moznet if needed and start services
make services-seed     # create missing Nginx Proxy Manager hosts
make services-stop     # stop services but retain moznet and data
make services-restart  # restart the service containers
make services-status   # show container status
make test              # run repository validation
```

Projects join `moznet` as an external network; Dugout alone creates and owns
it. Persistent application state is held in named Docker volumes. Ignored
bind mounts and private backups are organized under [`services/`](services/).

The Flutter image includes the Android command-line SDK needed for package
resolution, analysis, tests, and Android builds, including Flutter's pinned
NDK and CMake. It does not include or require Android Studio, an emulator, USB
access, or device privileges.
`flutter run` is intentionally rejected by the shim; use a host Flutter
installation for interactive emulator or physical-device sessions.

## Documentation

- [Quick-start guide](QUICK-START.md)
- [Documentation index](docs/README.md)
- [New-project integration](docs/10-new-project-quickstart.md)
- [Configuration reference](docs/09-configuration-reference.md)
- [Service and tool architecture](docs/01-platform-architecture.md)
- [Runner and command shims](docs/03-runner-and-command-shims.md)
- [Security and networking](docs/06-security-and-networking.md)
- [Release notes](CHANGELOG.md)

Dugout is development-machine infrastructure. It is not installed or deployed
on application servers.
