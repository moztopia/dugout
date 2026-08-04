# Security and networking

## Security model

Tool containers improve dependency isolation, but they are not automatically a
security sandbox. A tool that can write the project can modify source code. A
tool with the Docker socket can usually control the host Docker daemon. A tool
with developer credentials can act as that developer.

The runner must apply least privilege and make privilege expansion visible.

## Default capability set

An ordinary tool invocation should begin from:

```text
--rm
--init
--cap-drop ALL
--security-opt no-new-privileges=true
--user <host-uid>:<host-gid>
--mount project root at /workspace
--tmpfs /tmp
no devices
no Docker socket
no host PID/IPC namespace
no privileged mode
no published ports
no host home mount
minimal environment
declared network policy
```

Some tools will require exceptions. Exceptions belong in reviewed tool policy,
not ad hoc shell snippets hidden in projects.

## Workspace mounts

### Writable workspace

Compilers, formatters, package managers, and generators may require:

```text
type=bind,src=<project-root>,dst=/workspace
```

The runner must:

- resolve an absolute, existing project root;
- reject roots outside the configured project;
- quote paths as a single Docker argument;
- preserve the relative working directory;
- run with the host UID/GID;
- never mount the parent `Code` directory merely for convenience.

### Read-only workspace

Inspection and lint tools should prefer:

```text
type=bind,src=<project-root>,dst=/workspace,readonly
```

Examples:

- ShellCheck;
- Hadolint;
- Actionlint;
- `jq` queries;
- security scans that do not need to update databases in the workspace.

The tool metadata should declare whether write access is required. A caller may
choose a stricter read-only mode, but should not silently broaden a tool's
declared access.

## Root filesystem

Use a read-only root filesystem when the image supports it:

```text
--read-only
--tmpfs /tmp:rw,nosuid,nodev
```

Mount explicit caches separately. If an upstream tool writes to undocumented
system paths, either correct the image or document the exception; do not make
every image writable by default.

## User identity

Without `--user`, containers commonly run as root and create root-owned
workspace files.

The runner supplies:

```text
--user <uid>:<gid>
```

Images must not require a named user. If tools call APIs that need a username
or home directory, the runner supplies a disposable home:

```text
HOME=/tmp/dugout-home
```

Supplementary groups are not forwarded by default. Add them only for a
specific, reviewed resource requirement.

## Network policies

### `none`

Use Docker's disabled-network mode for deterministic, offline tools:

- formatters;
- local linters;
- language runtimes executing local code;
- JSON/YAML processors.

Benefits:

- prevents unexpected downloads;
- reveals undeclared dependencies;
- reduces exfiltration paths;
- improves repeatability.

### `internet`

Use normal Docker egress for:

- Composer installs;
- npm installs;
- registry clients;
- documentation link checks;
- vulnerability database updates.

Internet access does not imply `moznet` access.

### `moznet`

Use only for tools that intentionally talk to local development services:

- MariaDB client;
- Redis CLI;
- HTTP or gRPC diagnostics aimed at project services;
- migrations when they truly execute from a tool container rather than an
  application container.

The runner verifies:

```sh
docker network inspect moznet
```

If unavailable, it fails with instructions to start or repair Dugout. It must
not create the network; Dugout Compose creates it through `make up`.

### Docker API

Docker API access is not an ordinary network mode. Binding
`/var/run/docker.sock` gives the container powerful control over the daemon and
host-mounted data.

Only a dedicated Docker-aware policy can request it. The runner must:

- identify the tool as Docker-aware;
- display or log that expanded capability;
- mount only the socket/API endpoint required;
- avoid also forwarding unrelated credentials;
- never grant it merely because a tool joined `moznet`.

`--privileged` is prohibited for normal tool images.

## Ports

Tool containers never use:

```text
--publish
-p
-P
```

They are command processes, not local services. A tool that starts a listener
needs a separate architectural review and is probably a Dugout service, not a
tool.

An image's `EXPOSE` metadata does not itself publish a port, but initial Dugout
tool images should omit it to keep intent unambiguous.

## Credentials and secrets

### Default

Forward no credentials.

### Explicit environment

Allowlist individual names per tool or project:

```text
COMPOSER_AUTH
NPM_TOKEN
GH_TOKEN
```

Avoid command-line secret values when they would appear in process listings or
shell history.

### Files

Mount the narrowest possible credential file read-only:

```text
source=<specific-file>,target=<tool-specific-path>,readonly
```

Never mount all of:

```text
$HOME
~/.ssh
~/.config
```

merely because one tool needs one file.

### SSH agent

If a package manager requires private Git dependencies, forwarding an SSH
agent is preferable to mounting private keys, but still grants the container
the ability to request signatures. It must be a named, explicit capability.

### Registry credentials

Image pulls are performed by the host Docker client/daemon. The tool container
does not need access to the host's Docker configuration merely to run a pulled
image.

## Caches and trust

Caches are writable, persistent inputs. A compromised tool invocation can
poison data consumed later.

Mitigations:

- scope caches by tool and incompatible runtime family;
- never execute a cache as shell code in the runner;
- prefer package-manager integrity verification;
- provide simple cache deletion;
- do not share credential files through cache volumes;
- treat cache invalidation as normal, not exceptional;
- use read-only mounts when a command only consumes cached data.

## Supply-chain controls

Published images should:

- pin base images by digest in source;
- verify downloaded artifact checksums or signatures;
- record upstream source URLs;
- generate an SBOM;
- receive vulnerability scanning;
- publish immutable digests;
- optionally sign releases;
- rebuild when base-image security updates require it;
- avoid curl-pipe-shell installation unless the upstream method is verified
  and isolated in a build stage.

Projects should lock images by digest once the locking workflow exists.

## Repository trust

Adding Dugout's shared `bin` directory to the front of `PATH` gives
Dugout-owned executables priority over host tools. This is powerful by design.

Controls:

- shared shims contain only the minimal delegation contract;
- shim changes receive review in the Dugout repository;
- projects do not supply executable shims;
- VS Code Workspace Trust remains enabled;
- the runner never executes the manifest as shell;
- the lock file is parsed as data;
- unknown manifest fields fail closed.

## Logging and privacy

Debug output may include:

- host project paths;
- image references;
- environment variable names;
- command arguments;
- container IDs.

It must not include secret values. A `--debug` mode should redact values for
known credential variables and avoid dumping the complete host environment.

Normal output should remain the tool's output so scripts and pipes work.
Runner diagnostics belong on standard error.

## Threat-oriented checklist

### A malicious project checkout

Risk:
: A manifest tricks a developer into selecting an unexpected image.

Controls:
: Workspace Trust, shared audited shims, data-only manifests, and clear image
  resolution through `dug which`.

### A compromised tool image

Risk:
: Reads credentials, rewrites source, or contacts external systems.

Controls:
: Minimal mounts, environment allowlists, disabled network where possible,
  digest locks, scanning, non-root execution, no Docker socket.

### A poisoned cache

Risk:
: Malicious cached content affects later invocations.

Controls:
: Scoped caches, integrity checks, easy eviction, no shared executable runner
  code in caches.

### Docker socket exposure

Risk:
: Effective host-level Docker control.

Controls:
: Separate explicit policy, dedicated images, no default socket mount, visible
  diagnostics.

### Incorrect `moznet`

Risk:
: A tool silently creates or joins an unintended network.

Controls:
: Dugout owns lifecycle; runner only inspects and joins the exact named
  network; absence is fatal.

## Source references

- [Docker container run options](https://docs.docker.com/reference/cli/docker/container/run/)
- [Docker container runtime user and workdir](https://docs.docker.com/engine/containers/run/)
- [Docker Compose external networks](https://docs.docker.com/reference/compose-file/networks/#external)
