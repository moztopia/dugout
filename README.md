# Dugout

Current release: **1.1.0 — Double**

Dugout is Moztopia's local development service plane and containerized command
toolbox. It owns the shared local services, the globally named `moznet` Docker
network, and command images for PHP, Composer, Node.js, npm, npx, Dart, and
Flutter.

## Quick start

### Prerequisites

- Docker Engine with the Compose plugin;
- Git;
- a POSIX shell (`sh`);
- `make`.

### 1. Configure Dugout

```sh
git clone https://github.com/mozrin/dugout.git
cd dugout
cp .env.example .env
```

Open `.env` and replace the default MinIO credentials:

```dotenv
DUGOUT_MINIO_ROOT_USER=your-local-admin
DUGOUT_MINIO_ROOT_PASSWORD=your-long-local-password
```

The local `.env` is ignored by Git.

### 2. Start the shared services

```sh
make services-up
```

This creates the shared `moznet` network automatically and starts:

- Nginx Proxy Manager;
- Portainer;
- Adminer;
- Mailpit;
- Dozzle;
- MinIO.

Only host ports `80` and `81` are published. Open Nginx Proxy Manager at
[http://localhost:81](http://localhost:81), then route local HTTP hostnames to
the internal services:

| Local hostname | Forward host | Forward port |
| --- | --- | ---: |
| `proxy.localhost` | `do_proxy` | 81 |
| `portainer.localhost` | `do_portainer` | 9000 |
| `adminer.localhost` | `do_adminer` | 8080 |
| `mailpit.localhost` | `do_mailpit` | 8025 |
| `dozzle.localhost` | `do_dozzle` | 8080 |
| `minio.localhost` | `do_minio` | 9001 |
| `s3.localhost` | `do_minio` | 9000 |

Use HTTP, leave SSL disabled, and enable WebSocket support for Dozzle and
MinIO. Application containers on `moznet` can use `mailpit:1025` for SMTP and
`http://minio:9000` for S3-compatible storage.

### 3. Build and install the command tools

```sh
make build-tools
make install
export PATH="$HOME/.local/bin:$PATH"
```

Persist the `PATH` line in your shell profile if desired. Verify the complete
installation:

```sh
dug version
dug doctor
php --version
composer --version
node --version
npm --version
dart --version
flutter --version
```

Expected release output:

```text
dug 1.1.0 (Double)
```

## Everyday commands

```sh
make services-up       # create moznet if needed and start services
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

- [Documentation index](docs/README.md)
- [New-project integration](docs/10-new-project-quickstart.md)
- [Configuration reference](docs/09-configuration-reference.md)
- [Service and tool architecture](docs/01-platform-architecture.md)
- [Runner and command shims](docs/03-runner-and-command-shims.md)
- [Security and networking](docs/06-security-and-networking.md)
- [Release notes](CHANGELOG.md)

Dugout is development-machine infrastructure. It is not installed or deployed
on application servers.
