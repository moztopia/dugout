# Dugout

Dugout provides optional local web utilities and repository-local container
wrappers for PHP, Composer, Node.js, npm, and npx. There is no installer and no
reverse proxy.

## Requirements

You need:

- Docker Engine or Docker Desktop, with the Docker Compose plugin;
- GNU Make;
- Git and VS Code only if you want the repository-local command wrappers.

Start Docker, then prepare the configuration:

```sh
git clone https://github.com/mozrin/dugout.git
cd dugout
cp .env.example .env
```

Review `.env` before starting. The required decisions are:

- set each `DUGOUT_<SERVICE>_ENABLED` value to `1` or `0`;
- change any `DUGOUT_<SERVICE>_PORT` that conflicts with another local service;
- change tool image versions only when you intentionally want different tool
  images.

Start the enabled utilities:

```sh
make up
```

Compose creates the shared `moznet` Docker network automatically. It also
pulls the utility images when they are not already present.

## Utilities

All browser and SMTP ports bind only to `127.0.0.1`; Dugout has no proxy,
public routes, TLS configuration, or external proxy network.

| Utility | Default local endpoint | Enable setting |
| --- | --- | --- |
| Portainer | `http://localhost:9000` | `DUGOUT_PORTAINER_ENABLED` |
| Adminer | `http://localhost:8080` | `DUGOUT_ADMINER_ENABLED` |
| Mailpit UI | `http://localhost:8025` | `DUGOUT_MAILPIT_ENABLED` |
| Mailpit SMTP | `localhost:1025` | `DUGOUT_MAILPIT_ENABLED` |
| Dozzle | `http://localhost:9999` | `DUGOUT_DOZZLE_ENABLED` |

Set an enable value to `0` and run `make up` again. Compose removes that
service's container while preserving its named volume. Set it back to `1` and
run `make up` to restore it.

Services on `moznet` remain reachable to application containers by Compose
service name, such as `mailpit:1025`.

## Commands

```sh
make up       # apply .env and start enabled utilities
make status   # show utility status
make stop     # stop utilities without removing containers
make restart  # restart existing utility containers
make down     # remove containers and network, preserving named volumes
```

To delete persistent utility data as well, explicitly run
`docker compose down --volumes`.

## Command wrappers

Open Dugout in VS Code and create a new integrated terminal to use its local
`php`, `composer`, `node`, `npm`, and `npx` wrappers. They read tool versions
and network policies from `.env`; they do not install host commands or modify
your shell profile.

Verify them with:

```sh
dug doctor
php --version
composer --version
node --version
npm --version
npx --version
```

For maintainer and architecture details, see the
[documentation index](docs/README.md).
