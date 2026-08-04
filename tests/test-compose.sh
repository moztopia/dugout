#!/bin/sh
set -eu

ROOT_DIR="$(CDPATH='' cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT_DIR}"

docker compose --env-file .env.example config --quiet

disabled_config="$({
  DUGOUT_PORTAINER_ENABLED=0 \
  DUGOUT_ADMINER_ENABLED=0 \
  DUGOUT_MAILPIT_ENABLED=0 \
  DUGOUT_DOZZLE_ENABLED=0 \
    docker compose --env-file .env.example config
})"

disabled_count="$(printf '%s\n' "${disabled_config}" | grep -c 'replicas: 0')"
[ "${disabled_count}" -eq 4 ] || {
  printf '%s\n' 'Expected all four utilities to be disabled.' >&2
  exit 1
}

if printf '%s\n' "${disabled_config}" | grep -Eiq 'traefik|web-proxy'; then
  printf '%s\n' 'Compose configuration still contains proxy wiring.' >&2
  exit 1
fi

loopback_count="$(printf '%s\n' "${disabled_config}" | grep -c 'host_ip: 127.0.0.1')"
[ "${loopback_count}" -eq 5 ] || {
  printf '%s\n' 'Expected all five published ports to bind to loopback.' >&2
  exit 1
}

printf '%s\n' 'Dugout Compose configuration tests pass.'
