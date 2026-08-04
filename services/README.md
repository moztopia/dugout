# Service-local files

This directory groups machine-local files for Dugout's long-running services.
The service definitions remain in the root `docker-compose.yaml`.

```text
services/
├── adminer/
│   ├── config/
│   └── logs/
├── dozzle/
├── mailpit/
├── pihole/
│   ├── etc-dnsmasq.d/
│   └── etc-pihole/
└── portainer/
    ├── config/
    └── logs/
```

These subdirectories are ignored by Git because they contain runtime output,
machine-specific configuration, or sensitive backups. Persistent application
state lives in the named Docker volumes declared by Compose.

Store a private backup under the owning stateful service, for example:

```text
services/portainer/backups/portainer.db
```

Do not commit database files, exported credentials, certificates, logs, or
other runtime data.

## Shared development endpoints

All enabled services join the Dugout-managed `moznet` network. Application
projects can use these internal endpoints:

| Service | Internal endpoint | Purpose |
| --- | --- | --- |
| Mailpit | `mailpit:1025` | SMTP capture |
| Mailpit | `http://mailpit:8025` | Captured-message UI |
| Dozzle | `http://dozzle:8080` | Container log UI |

The web interfaces publish configurable ports on `127.0.0.1` only. See the
root `.env.example` for enable switches and port settings.
