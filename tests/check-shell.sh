#!/bin/sh
set -eu

ROOT_DIR="$(CDPATH='' cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT_DIR}"

set -- \
  bin/dug \
  bin/php \
  bin/composer \
  bin/node \
  bin/npm \
  bin/npx \
  tests/check-shell.sh \
  tests/test-images.sh \
  tests/test-runner.sh

for script do
  sh -n "${script}"
done

if command -v shellcheck >/dev/null 2>&1; then
  for script do
    shellcheck --shell=sh "${script}"
  done
elif command -v docker >/dev/null 2>&1; then
  docker run --rm \
    --volume "${ROOT_DIR}:/mnt:ro" \
    --workdir /mnt \
    koalaman/shellcheck:stable \
    "$@"
else
  echo "ShellCheck or Docker is required." >&2
  exit 127
fi

echo "Dugout shell scripts pass POSIX syntax and ShellCheck."
