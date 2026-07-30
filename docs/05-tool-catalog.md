# Initial tool catalog

## Selection principles

Add a tool image when it provides at least one of:

- meaningful version isolation between projects;
- removal of a heavy or awkward host dependency;
- consistent behavior between developer machines and CI;
- useful security isolation;
- a reusable command across multiple repositories.

Do not add an image merely because a binary exists. Each image creates ongoing
work: upstream monitoring, rebuilds, scanning, multi-architecture publication,
documentation, and compatibility tests.

## Priority 0: prove the system

Before building every language runtime, prove the runner with small tools:

| Tool | Why first | Default network | Writable workspace |
| --- | --- | ---: | ---: |
| `jq` | Tiny, stable argument and pipe tests | `none` | No |
| `shellcheck` | Repository value and machine-readable exits | `none` | No |
| `shfmt` | Exercises read/write and check-only modes | `none` | Optional |

These validate standard input, output, exit codes, read-only operation, UID/GID,
and project-relative paths without runtime-family complexity.

## Priority 1: requested language tools

| Tool | Public command | Default network | Cache | Important compatibility |
| --- | --- | ---: | --- | --- |
| PHP | `php` | `none` | Optional | Version, extensions, libc |
| Composer | `composer` | `internet` | Required | PHP version and extensions |
| Node.js | `node` | `none` | Optional | Version, architecture, libc |
| npm | `npm` | `internet` | Required | Must match Node runtime family |
| npx | `npx` | `internet` | Required | Must match Node/npm family |
| Dart | `dart` | `internet` | Required | Project SDK constraint |
| Flutter | `flutter` | `internet` | Required | Pinned Android toolchain |

### PHP variants

A useful PHP catalog may require variants:

```text
dugout-php:<version>-cli
dugout-php:<version>-project
```

Prefer a small number of documented variants over a combinatorial tag matrix.
For project dependency work, matching the application's actual extension set
is more important than making the generic PHP image a few megabytes smaller.

### Composer

Composer is not truly independent from PHP. The initial Composer image should
declare exactly which PHP runtime and extensions it contains.

Before a project adopts it for `composer update`, compare:

```sh
composer check-platform-reqs
php --version
php -m
```

between the tool image and application runtime.

### Node/npm/npx

Build the three public images from a shared versioned base. This avoids
duplicated maintenance while retaining one obvious command per image.

Do not use an Alpine npm image to populate `node_modules` for a Debian runtime
without tests proving native-module compatibility.

### Dart and Flutter

Dart 3.12.2 and Flutter 3.44.2 are implemented as separate public tools.
Flutter includes the command-line Android SDK for dependency resolution,
analysis, tests, and builds. Android Studio, emulators, USB devices, and
privileged container access are not part of the image. `flutter run` is
rejected with a clear message; interactive device work stays on the host.

## Priority 2: universal development utilities

| Tool | Purpose | Default network |
| --- | --- | ---: |
| `yq` | YAML queries and transformations | `none` |
| `curl` | HTTP diagnostics and smoke tests | `explicit` |
| `openssl` | Keys, certificates, hashes, and diagnostics | `none` |
| `make` | Consistent Make implementation | `none` |
| `git` | Versioned Git behavior when truly needed | `internet` |
| `gh` | GitHub workflows | `internet` |
| `rsync` | File synchronization | `none` |
| `zip` | Archive creation | `none` |
| `unzip` | Archive extraction | `none` |

Some of these are commonly available on the host. Their value depends on
whether projects need version control or CI parity. Avoid turning simple host
bootstrap into hundreds of container images without a concrete benefit.

`gh` requires explicit authentication forwarding. It must never receive the
entire host home directory.

## Priority 3: source and workflow validation

| Tool | Purpose | Default network |
| --- | --- | ---: |
| `hadolint` | Dockerfile linting | `none` |
| `actionlint` | GitHub Actions linting | `none` |
| `markdownlint` | Markdown style checking | `none` |
| `markdown-link-check` | Documentation link validation | `internet` |
| `vale` | Prose linting | `none` |
| `prettier` | Generic formatting | `none` |

Project plugins and configurations remain in the project. A global Prettier or
Markdown lint image must not override a repository's pinned package without an
explicit policy.

## Priority 4: API tools

| Tool | Purpose | Default network | Weight |
| --- | --- | ---: | --- |
| `spectral` | OpenAPI linting | `none` | Medium |
| `openapi-generator` | Client/server generation | `none` | Heavy |
| `swagger-cli` | OpenAPI validation and bundling | `none` | Medium |
| `grpcurl` | gRPC requests and reflection | `explicit` | Small |
| `httpie` | Human-friendly HTTP client | `explicit` | Medium |

OpenAPI Generator carries a Java runtime and is a good example of why
single-purpose matters more than absolute image size: the weight is isolated
to the command that needs it.

Generated files must use the host UID/GID and deterministic generator versions.

## Priority 5: database and service clients

| Tool | Purpose | Default network | Server included |
| --- | --- | ---: | ---: |
| `mariadb` | MariaDB/MySQL client | `moznet` | No |
| `psql` | PostgreSQL client | `moznet` | No |
| `redis-cli` | Redis diagnostics | `moznet` | No |
| `sqlite3` | Local SQLite inspection | `none` | No |

These images contain clients only. Dugout and project Compose own servers.

Examples:

```sh
mariadb --host hearts_database --user hearts --password
redis-cli -h hearts_cache ping
```

No client publishes a port. Network access is outbound from the ephemeral tool
container to services already reachable on `moznet`.

## Priority 6: container supply-chain tools

| Tool | Purpose | Default access |
| --- | --- | --- |
| `trivy` | Image/filesystem vulnerability scanning | Internet or Docker API |
| `syft` | SBOM generation | Filesystem or Docker API |
| `grype` | Vulnerability matching | Internet |
| `cosign` | Signing and verification | Internet plus explicit credentials |
| `dive` | Image layer inspection | Docker API or saved image |
| `docker` | Docker CLI | Docker API |

Docker API access is equivalent to powerful host control. Keep this class
separate from ordinary tools and require an explicit capability.

Prefer scanning an exported artifact or registry reference when it avoids
mounting the host Docker socket.

## Heavy language tools

| Tool | Notes |
| --- | --- |
| Dart | Implemented pinned SDK image with a persistent pub cache |
| Flutter | Implemented heavyweight SDK image with pub and Gradle caches |
| Python | Small runtime possible, but native wheels affect base selection |
| `uv` | Useful fast Python environment/package tool |
| Java | Runtime family and JDK distribution must be explicit |
| Gradle | Coupled to Java and project wrapper conventions |

Gradle projects should generally prefer the committed Gradle Wrapper inside a
matching Java image rather than a globally selected Gradle image.

## Tools that normally stay project-local

These are usually dependencies rather than global Dugout images:

- PHPUnit;
- Laravel Pint;
- PHPStan or Psalm;
- ESLint;
- TypeScript;
- Vitest or Jest;
- Vite;
- React tooling;
- project-specific code generators.

The language/package-manager image executes the version selected by the
repository:

```sh
composer exec phpunit
npx eslint .
npm test
```

Creating global images for these tools can bypass lock files and produce
different behavior from CI.

## Suggested first release

### Foundation release

- `jq`
- `shellcheck`
- `shfmt`
- the `dug` runner;
- shared Dugout command shims;
- contract-test fixture.

### Language release

- `php`;
- `composer`;
- shared Node base;
- `node`;
- `npm`;
- `npx`.
- `dart`;
- `flutter`.

### Platform-aware release

- `mariadb`;
- `redis-cli`;
- `curl`;
- `gh`;
- `hadolint`;
- `actionlint`.

This sequence proves the mechanics before introducing dependency-resolution
and runtime-compatibility risks.

## Tool proposal checklist

Before accepting a new tool:

- [ ] At least two concrete consumers or one compelling heavy-dependency use
- [ ] Named maintainer
- [ ] Upstream release source identified
- [ ] License reviewed
- [ ] Public command and entrypoint defined
- [ ] Network policy selected
- [ ] Cache policy selected
- [ ] Credential requirements documented
- [ ] Runtime compatibility documented
- [ ] Supported architectures selected
- [ ] Contract tests written
- [ ] Update process defined
- [ ] Removal/deprecation path considered
