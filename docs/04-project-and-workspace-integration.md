# Project and workspace integration

## Objective

When a developer opens a configured project and creates a terminal, normal
command lookup should find the project's Dugout shims before host binaries.

This must be an ordinary `PATH` mechanism—not a collection of aliases.

Why shims instead of aliases:

- aliases usually exist only in interactive shells;
- Make and child processes do not reliably inherit aliases;
- scripts using `#!/usr/bin/env php` need a real executable in `PATH`;
- VS Code tasks may use non-interactive shells;
- `command -v` and `type` can inspect real shims;
- shims forward exit codes predictably.

## Proposed project files

```text
.dugout/
├── bin/
│   ├── composer
│   ├── node
│   ├── npm
│   ├── npx
│   └── php
├── tool-lock.json
└── tool-versions
```

All three are committed:

- `bin/` defines which ordinary command names the project virtualizes;
- `tool-versions` defines human-reviewable selections;
- `tool-lock.json` provides immutable resolution when enabled.

The project should also document its expected runner version until runner
compatibility is machine-verifiable.

## VS Code folder workspace

For a repository opened as a single VS Code folder, proposed
`.vscode/settings.json`:

```json
{
  "terminal.integrated.env.linux": {
    "PATH": "${workspaceFolder}/.dugout/bin:${env:PATH}"
  }
}
```

VS Code supports variable substitution for selected terminal environment
settings, including `${workspaceFolder}` and `${env:NAME}`.

After changing the setting, close old terminal instances and create a new
terminal. Existing terminals retain their existing environment.

Verify:

```sh
command -v php
type -a php
php --version
dug which php
```

The first path must be the project shim.

## VS Code multi-root workspace

In a multi-root `.code-workspace` file, use an explicitly scoped folder
variable to avoid ambiguity:

```json
{
  "folders": [
    {
      "name": "hearts",
      "path": "."
    },
    {
      "name": "dugout",
      "path": "../dugout"
    }
  ],
  "settings": {
    "terminal.integrated.env.linux": {
      "PATH": "${workspaceFolder:hearts}/.dugout/bin:${env:PATH}"
    }
  }
}
```

The folder name in `${workspaceFolder:hearts}` must match a workspace folder
name. Explicit naming is preferable to relying on a basename that may change.

This setting routes commands typed in integrated terminals. It does not cause
the Dugout repository to become part of the application repository, and it
does not grant containers access to sibling folders.

## macOS and Windows

The initial runner may target Linux first, but the configuration contract
should reserve platform-specific settings:

```json
{
  "terminal.integrated.env.linux": {
    "PATH": "${workspaceFolder}/.dugout/bin:${env:PATH}"
  },
  "terminal.integrated.env.osx": {
    "PATH": "${workspaceFolder}/.dugout/bin:${env:PATH}"
  }
}
```

Windows support requires a deliberate decision:

- Git Bash or WSL can use POSIX shims;
- native PowerShell requires `.ps1` or executable wrappers;
- Docker Desktop path and ownership semantics differ from Linux;
- a Windows-native runner must preserve arguments without passing through
  fragile shell-string composition.

Do not claim native Windows support until it has contract tests.

## Ordinary terminals with `direnv`

VS Code settings affect VS Code terminals only. For project-aware behavior in
ordinary terminals, `direnv` is the cleanest optional integration.

Proposed `.envrc`:

```sh
PATH_add .dugout/bin
```

The developer explicitly approves the file with:

```sh
direnv allow
```

Verify after entering the project:

```sh
command -v php
```

When leaving the directory, `direnv` restores the previous `PATH`.

The `.envrc` should alter only command lookup. It should not contain registry
tokens, application secrets, or duplicated runner logic.

## Ordinary terminals without `direnv`

Alternatives:

```sh
export PATH="$PWD/.dugout/bin:$PATH"
```

or a future helper:

```sh
eval "$(dug env)"
```

The `dug env` output must be carefully specified and safe to evaluate. Until
then, an explicit `PATH` export is more transparent.

Another option is:

```sh
dug shell
```

That command could start a child shell with the project shim directory
prepended. It must not modify global shell startup files automatically.

## Make

Once `.dugout/bin` is first in `PATH`, ordinary recipes resolve the shims:

```make
.PHONY: php-version frontend-install

php-version:
 php --version

frontend-install:
 npm install
```

For reproducibility in CI or environments where shell activation is uncertain,
Make may invoke the runner explicitly:

```make
php-version:
 dug tool php --version
```

A project should choose one style consistently. Explicit runner calls are
clearer in automation; natural commands are nicer for developers.

Make must not recursively invoke a host command by resetting `PATH`.

## Scripts and shebangs

A script using:

```text
#!/usr/bin/env php
```

will resolve the PHP shim when the shim directory is first in `PATH`.

However, the shim then mounts and runs the project inside a container. This is
correct only when:

- the script belongs to the configured workspace;
- the runner can identify the workspace from the current directory;
- the script path passed by `env` is meaningful through the workspace mount.

This behavior needs an end-to-end contract test before Dugout promises support
for containerized shebang execution.

For project automation, the clearer initial form is:

```sh
php path/to/script.php
```

## VS Code tasks

Tasks can call natural commands:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "PHP version",
      "type": "process",
      "command": "${workspaceFolder}/.dugout/bin/php",
      "args": ["--version"],
      "problemMatcher": []
    }
  ]
}
```

Using a `process` task and a concrete shim path avoids an unnecessary shell and
preserves argument boundaries.

For task portability across environments, an explicit `dug` command is also
acceptable.

## Editor extensions are separate

Changing terminal `PATH` does not guarantee every editor extension uses the
shim. Extensions may:

- read their own executable-path setting;
- start a long-lived language server;
- require host paths in diagnostics;
- expect to inspect the executable filesystem;
- bypass the terminal environment entirely.

Examples of possible configurations:

```json
{
  "php.validate.executablePath": "${workspaceFolder}/.dugout/bin/php"
}
```

Whether a particular extension accepts a container shim must be tested. A
one-shot `docker run` per validation request may be too slow, while a language
server designed as a persistent process may not fit the ephemeral tool model.

Recommended boundary:

- command-line validation, builds, generation, and tests use Dugout tools;
- editor language servers receive a separately tested integration;
- no documentation claims an extension works merely because the terminal does.

## Devcontainer integration

A devcontainer is optional. If present:

- it should expose the same `.dugout/bin` directory in `PATH`;
- the `dug` runner must know whether it is talking to a host Docker daemon;
- host bind-mount paths must remain meaningful to that daemon;
- it must not create `moznet`;
- it must not contain unique tool versions or scripts;
- it should fail clearly if it cannot access required Dugout infrastructure.

The extra host-path translation makes this more complex than direct host
execution. Devcontainer support should follow, not define, the runner contract.

## Workspace trust

Project shims are executable repository content. Opening a repository and
allowing its shim directory to precede system tools means typing `php` executes
code supplied by that repository.

That is intentional but must be visible:

- review shims like any other executable code;
- use VS Code Workspace Trust;
- never enable Dugout shims automatically for an untrusted checkout;
- keep shims minimal enough to audit at a glance;
- verify generated shims before committing them.

## Troubleshooting command resolution

### Host PHP still runs

```sh
type -a php
printf '%s\n' "$PATH"
```

Create a new terminal after changing workspace settings. Ensure
`.dugout/bin/php` is executable.

### Shim is found but `dug` is missing

```sh
command -v dug
dug doctor
```

Install or update the runner using the Dugout installation procedure.

### Correct shim, wrong image version

```sh
dug which php
sed -n '/^php /p' .dugout/tool-versions
dug verify
```

Regenerate the lock file if the manifest intentionally changed.

### Commands work in a terminal but not an extension

Configure and test the extension's executable setting separately. Terminal
`PATH` behavior is not proof of extension integration.

## Source references

- [VS Code variables reference](https://code.visualstudio.com/docs/reference/variables-reference)
- [VS Code workspace settings](https://code.visualstudio.com/docs/configure/settings)
- [VS Code terminal profiles](https://code.visualstudio.com/docs/terminal/profiles)
