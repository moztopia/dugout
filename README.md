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
- free TCP ports `80` and `81`;
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

The installer explains and checks its work before changing the machine. It:

1. verifies Docker, Compose, required host commands, ports `80` and `81`, and
   Dugout's reserved Docker resource names;
2. stops if Dugout is already or partially installed;
3. asks for an email address and hidden password;
4. shows the complete proposed installation and asks for confirmation;
5. writes local credentials to the ignored `.env` file;
6. builds all seven command-tool images;
7. creates `moznet` and starts all five development services;
8. creates the Nginx Proxy Manager administrator automatically;
9. creates the standard local proxy hosts;
10. runs the full validation suite and records the resources owned by the
    installation.

The email address and password configure the Nginx Proxy Manager administrator
and are stored only in the ignored `.env` file.

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
| `http://proxy.localhost` | Nginx Proxy Manager |
| `http://portainer.localhost` | Portainer |
| `http://adminer.localhost` | Adminer |
| `http://mailpit.localhost` | Mailpit |
| `http://dozzle.localhost` | Dozzle |

## Already installed

`make install` deliberately refuses to modify an existing or partial
installation. It checks its private state file together with the actual
containers, volumes, images, runtime files, configuration, and `moznet`
network.

If installation previously stopped partway through, remove the recorded
partial installation before trying again:

```sh
make uninstall
make install
```

## Uninstall

Uninstalling Dugout permanently deletes everything created by the installer:

- service containers and tool images;
- Nginx Proxy Manager hosts, certificates, and configuration;
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

If a requirement, port, container name, volume, image, or network is
unavailable, it reports the exact conflict and stops. Resolve the issue, then
rerun:

```sh
make install
```

For architecture and operational details after installation, see the
[documentation index](docs/README.md).
