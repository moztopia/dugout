# Dugout documentation

Dugout is the local development platform shared by MozTopia projects. It has
two complementary responsibilities:

1. provide long-lived local infrastructure such as DNS, reverse proxying,
   administration, and the shared `moznet` Docker network;
2. provide small, single-purpose tool images that projects can invoke as if
   the tools were installed locally.

The tool-container design is documented here before it is implemented. Any
path, command, image name, configuration file, or behavior described as
**proposed** is a contract for the implementation—not a claim that it already
exists.

## Design goals

- Typing `php`, `composer`, `node`, `npm`, or `npx` in a project terminal
  invokes the project-selected Dugout image instead of a host installation.
- Every tool image has one public purpose and one predictable entrypoint.
- Projects pin their own tool versions.
- The same commands work in VS Code, ordinary terminals, scripts, Make
  targets, and CI.
- Files created by tools belong to the host user.
- Commands preserve the caller's project-relative working directory.
- Tool containers are ephemeral and publish no ports.
- Access to `moznet`, credentials, host caches, devices, and the Docker socket
  is explicit rather than automatic.
- Project behavior does not depend on a devcontainer.
- A devcontainer may consume the same commands as an optional editor
  environment, but it does not become a second toolchain.

## Documents

| Document | Purpose |
| --- | --- |
| [Platform architecture](01-platform-architecture.md) | Dugout's service plane, tool plane, ownership boundaries, and execution flow |
| [Tool image contract](02-tool-image-contract.md) | Requirements every single-purpose image must satisfy |
| [Runner and command shims](03-runner-and-command-shims.md) | How a typed command becomes an ephemeral container invocation |
| [Project and workspace integration](04-project-and-workspace-integration.md) | Project files, VS Code settings, `direnv`, tasks, and editor limitations |
| [Initial tool catalog](05-tool-catalog.md) | Recommended tools, policies, priorities, and runtime compatibility concerns |
| [Security and networking](06-security-and-networking.md) | Least privilege, `moznet`, secrets, mounts, caches, and Docker access |
| [Build, test, and publish](07-build-test-and-publish.md) | Repository layout, image versioning, CI, contract tests, and releases |
| [Rollout and operations](08-rollout-and-operations.md) | Phased delivery, project adoption, upgrades, troubleshooting, and rollback |

## Vocabulary

**Dugout service**
: A long-running local infrastructure container managed by Dugout Compose,
  such as the proxy, Portainer, Adminer, or Pi-hole.

**Tool image**
: An immutable image whose public interface is one command, such as `php`,
  `composer`, or `shellcheck`.

**Tool container**
: A short-lived container created from a tool image for one invocation. It is
  removed when the command exits.

**Runner**
: The small host-side program that turns a tool name and arguments into a safe,
  consistent `docker run` invocation.

**Shim**
: A project-local executable named after a tool. It delegates to the runner so
  normal shell command lookup selects the containerized tool.

**Tool manifest**
: A committed project file that selects tool versions and runtime policies.

**Tool lock**
: An optional committed file that resolves human-friendly image tags to
  immutable image digests.

## Non-goals

The tool plane is not intended to:

- replace project application containers;
- run package managers as permanent services;
- expose development ports;
- automatically join every tool to `moznet`;
- silently mount the Docker socket;
- mount the user's entire home directory;
- hide incompatible language runtimes;
- make every possible tool image tiny at the cost of correctness;
- require VS Code or any particular editor.

## Decision summary

The proposed direction is:

- Dugout owns local infrastructure and the `moznet` lifecycle.
- Project Compose overrides consume `moznet` as an external network.
- Tool images are independently versioned and independently runnable.
- A shared `dug` runner owns container mechanics.
- Projects commit small shims and version selections.
- Workspace settings only prepend the project's shim directory to `PATH`.
- Pure tools run without `moznet`; service-aware tools join it only when
  requested or allowed by policy.
- Images never publish ports.
- Image size matters, but runtime compatibility and predictable behavior matter
  more than winning an artificial size contest.
