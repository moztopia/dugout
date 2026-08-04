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
├── nginx-proxy-manager/
│   ├── backups/
│   ├── config/
│   └── logs/
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

Store a private backup under the owning service, for example:

```text
services/nginx-proxy-manager/backups/database.sqlite
```

Do not commit database files, exported credentials, certificates, logs, or
other runtime data.

## Shared development endpoints

All services join the Dugout-managed `moznet` network. Application Compose
projects treat that globally named network as external and can use these
internal endpoints:

| Service | Internal endpoint | Purpose |
| --- | --- | --- |
| Mailpit | `mailpit:1025` | SMTP capture |
| Mailpit | `http://mailpit:8025` | Captured-message UI |
| Dozzle | `http://dozzle:8080` | Container log UI |

The web interfaces intentionally do not publish host ports. Add proxy hosts in
Nginx Proxy Manager when browser access is needed. Use the container name and
internal UI port as the upstream target.
