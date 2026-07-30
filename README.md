# Dugout

Dugout is MozTopia's local development service plane and containerized command
toolbox. It owns shared local services and the external `moznet` Docker
network, plus small one-command images for PHP, Composer, Node.js, npm, and
npx.

The command shims live in [`bin/`](bin). Put that directory first in a
development terminal's `PATH` and ordinary commands run in ephemeral
containers:

```sh
export PATH="/path/to/dugout/bin:$PATH"
php --version
composer install
npm test
```

Copy [`.env.example`](.env.example) to `.env` to configure image versions,
networks, and other machine defaults. `.env` is local and ignored by Git.

```sh
cp .env.example .env
make build-tools
./bin/dug doctor
```

Start with the [documentation index](docs/README.md), especially:

- [new-project quick start](docs/10-new-project-quickstart.md);
- [configuration reference](docs/09-configuration-reference.md);
- [runner and shim behavior](docs/03-runner-and-command-shims.md);
- [workspace integration](docs/04-project-and-workspace-integration.md);
- [production boundary](docs/01-platform-architecture.md#deployment-boundary).

Dugout is development-machine infrastructure. It is not installed or deployed
on application servers.
