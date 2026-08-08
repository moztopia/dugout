# Dugout

Containerized development tools. No installers, no version managers, no host pollution.

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/moztopia/dugout/main/.docker/install.sh | sh
```

Requires Docker. That's it.

## Use

```sh
node --version
npm install
npx vite
```

## Switch Node Versions

Set `DUGOUT_NODE_VERSION` in your shell config:

```sh
export DUGOUT_NODE_VERSION=22
```

| Version | Status |
| --- | --- |
| 22 | Supported |
| 24 | **Default** |
| 26 | Supported |

## How It Works

Each command is a shell shim that runs `docker run` with the right image.
No binaries are installed on your machine. The tools live inside containers
pulled from `ghcr.io/moztopia/dugout-node`.

## Repository Structure

```tree
.docker/
  images/node.Dockerfile    Image recipe for Node 22/24/26
  installer.Dockerfile      Installer image
  install.sh                Curl installer
bin/
  node                      Shim
  npm                       Shim
  npx                       Shim
tools/
  barrel/                   Barrel — file scaffolding tool
```

## Uninstall

```sh
rm -rf ~/.local/bin/dugout
```
