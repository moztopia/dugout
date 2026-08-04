# Install Dugout

Dugout is a standalone local development environment. It installs a complete
service plane and builds isolated command-tool containers for PHP, Composer,
Node.js, npm, and npx.

**Dugout must be installed before it can be used.**

The installation lives in this Git checkout. Dugout never installs commands
globally, never changes a shell profile, and never adds anything to
`~/.local/bin`. Its command shims are active only in new VS Code integrated
terminals opened for this repository.

## Requirements

Installation currently supports Linux and macOS development hosts with:

- Docker Engine or Docker Desktop;
- the Docker Compose plugin;
- Git;
- GNU Make;
- Python 3.9 or newer;
- VS Code for the repository-scoped command environment;
- a running standalone Traefik proxy and its shared external Docker network;
- enough disk space for the service and tool images.

Start Docker before installing. Dugout checks every requirement and stops
without making changes when it finds a conflict.

## Install

Clone and open Dugout:

```sh
git clone https://github.com/mozrin/dugout.git
cd dugout
code .
```

Run the complete installer from a terminal in the checkout:

```sh
make install
```

Start standalone Traefik before installing Dugout. Both repositories default
to `web-proxy`. To use another external network, set the same value for both
stacks and install with `TRAEFIK_NETWORK_NAME=<name> make install`.

The installer explains and checks its work before changing the machine. It:

1. verifies Docker, Compose, required host commands, the shared proxy network,
   and Dugout's reserved Docker resource names;
2. stops if Dugout is already or partially installed;
3. shows the complete proposed installation and asks for confirmation;
4. writes local tool configuration to the ignored `.env` file;
5. builds all five command-tool images;
6. creates `moznet` and starts all four development services;
7. exposes browser routes to the standalone proxy through Compose labels;
8. runs the full validation suite and records the resources owned by the
    installation.

## After installation

Reopen this repository in VS Code and create a new integrated terminal.
Existing terminals cannot receive an updated workspace environment.

Verify the installation:

```sh
dug version
dug doctor
php --version
composer --version
node --version
npm --version
npx --version
```

These names resolve to `dugout/bin` only inside this VS Code workspace.
Terminals elsewhere continue to use their normal host `PATH`.

The installed browser endpoints are:

| Address | Service |
| --- | --- |
| `https://portainer.localhost.moztopia.com` | Portainer |
| `https://adminer.localhost.moztopia.com` | Adminer |
| `https://mailpit.localhost.moztopia.com` | Mailpit |
| `https://dozzle.localhost.moztopia.com` | Dozzle |

## Already installed

`make install` deliberately refuses to modify an existing or partial
installation. It checks its private state file together with the actual
containers, volumes, runtime files, configuration, and `moznet` network.
Reusable tool images and package-manager caches do not block installation, so
a fresh checkout recovers cleanly after `docker compose down -v` and removal
of the previous checkout.

If installation previously stopped partway through, remove the recorded
partial installation before trying again:

```sh
make uninstall
make install
```

## Uninstall

Uninstalling Dugout permanently deletes everything created by the installer:

- service containers and tool images;
- Portainer and Adminer state;
- Mailpit messages;
- Docker volumes and the `moznet` network;
- tool caches;
- local configuration and credentials;
- installation state.

The Git checkout and committed source files remain.

Run:

```sh
make uninstall
```

The uninstaller displays the complete data-loss warning and requires the exact
confirmation phrase `DELETE DUGOUT`.

It refuses to proceed when any non-Dugout container is attached to `moznet`.
Disconnect those containers first, then rerun the command. This prevents
Dugout from removing a network that an active development stack still uses.

## Troubleshooting installation

The installer does not automatically resolve host conflicts.

If a requirement, container name, volume, image, or network is
unavailable, it reports the exact conflict and stops. Resolve the issue, then
rerun:

```sh
make install
```

For architecture and operational details after installation, see the
[documentation index](docs/README.md).
