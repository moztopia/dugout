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
curl -fsSL https://raw.githubusercontent.com/moztopia/dugout/main/.docker/install.sh | sh
```

Make sure `~/.local/bin/dugout` is in your `PATH`. Add this to your shell
config if it isn't already:

```sh
export PATH="$HOME/.local/bin/dugout:$PATH"
```

Open a new terminal and verify:

```sh
node --version
npm --version
php --version
composer --version
```

## Uninstall

Remove the shims:

```sh
rm -rf ~/.local/bin/dugout
```

Optionally remove the cached Docker images:

```sh
docker rmi ghcr.io/moztopia/dugout-node:22 ghcr.io/moztopia/dugout-node:24 ghcr.io/moztopia/dugout-node:26
docker rmi ghcr.io/moztopia/dugout-php:8.2 ghcr.io/moztopia/dugout-php:8.3 ghcr.io/moztopia/dugout-php:8.4 ghcr.io/moztopia/dugout-php:8.5
```

That's everything. No config files, no daemons, no leftover state.

---

## Supported Tools

| Tool | Command | Image |
| --- | --- | --- |
| Node.js | `node` | `ghcr.io/moztopia/dugout-node` |
| npm | `npm` | `ghcr.io/moztopia/dugout-node` |
| npx | `npx` | `ghcr.io/moztopia/dugout-node` |
| PHP | `php` | `ghcr.io/moztopia/dugout-php` |
| Composer | `composer` | `ghcr.io/moztopia/dugout-php` |

Node, npm, and npx share one image. PHP and Composer share another.

## Switching Versions

Set an environment variable to change which version runs:

```sh
export DUGOUT_NODE_VERSION=22
export DUGOUT_PHP_VERSION=8.3
```

### Node

| Version | Status |
| --- | --- |
| 22 | Supported |
| **24** | **Default** |
| 26 | Supported |

### PHP

| Version | Status |
| --- | --- |
| 8.2 | Supported |
| 8.3 | Supported |
| **8.4** | **Default** |
| 8.5 | Supported |

The version can be set globally in your shell config, per-session, or
per-command:

```sh
# Global default (add to ~/.bashrc or ~/.bash_pathing)
export DUGOUT_NODE_VERSION=26
export DUGOUT_PHP_VERSION=8.5

# One-off command
DUGOUT_PHP_VERSION=8.2 php --version
```

---

## How It Works

Each command in `~/.local/bin/dugout/` is a ~10 line shell script that calls
`docker run` with the right image and mounts your current directory:

```
you type: npm install
     shim: docker run --rm ghcr.io/moztopia/dugout-node:24 npm install
   result: node_modules/ created in your project directory
```

The container runs as your user (same UID/GID), so files it creates are owned
by you. The container is removed immediately after the command finishes.

## Requirements

- Docker

---

## Repository Structure

```
.docker/
  images/node.Dockerfile    Image recipe for Node 22/24/26
  images/php.Dockerfile     Image recipe for PHP 8.2/8.3/8.4/8.5
  installer.Dockerfile      Installer image
  install.sh                Curl installer
bin/
  node                      Shim — runs node in a container
  npm                       Shim — runs npm in a container
  npx                       Shim — runs npx in a container
  php                       Shim — runs php in a container
  composer                  Shim — runs composer in a container
tools/
  barrel/                   Barrel — file scaffolding tool
```

## For Maintainers

Build images:

```sh
# Node
for v in 22 24 26; do
  docker build --build-arg NODE_VERSION=$v -f .docker/images/node.Dockerfile -t ghcr.io/moztopia/dugout-node:$v .
done

# PHP
for v in 8.2 8.3 8.4 8.5; do
  docker build --build-arg PHP_VERSION=$v -f .docker/images/php.Dockerfile -t ghcr.io/moztopia/dugout-php:$v .
done
```

Push to GHCR:

```sh
echo $GH_DUGOUT_WRITE_PACKAGES | docker login ghcr.io -u moztopia --password-stdin
for v in 22 24 26; do docker push ghcr.io/moztopia/dugout-node:$v; done
for v in 8.2 8.3 8.4 8.5; do docker push ghcr.io/moztopia/dugout-php:$v; done
```
