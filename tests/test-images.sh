#!/bin/sh
set -eu

IMAGE_PREFIX="${IMAGE_PREFIX:-moztopia/dugout}"
PHP_VERSION="${PHP_VERSION:-8.4}"
COMPOSER_VERSION="${COMPOSER_VERSION:-2}"
NODE_VERSION="${NODE_VERSION:-22}"
NPM_VERSION="${NPM_VERSION:-10}"
DART_VERSION="${DART_VERSION:-3.12.2}"
FLUTTER_VERSION="${FLUTTER_VERSION:-3.44.2}"

PHP_IMAGE="${IMAGE_PREFIX}-php:${PHP_VERSION}"
COMPOSER_IMAGE="${IMAGE_PREFIX}-composer:${COMPOSER_VERSION}-php$(printf '%s' "${PHP_VERSION}" | tr -d '.')"
NODE_IMAGE="${IMAGE_PREFIX}-node:${NODE_VERSION}"
NPM_IMAGE="${IMAGE_PREFIX}-npm:${NPM_VERSION}-node${NODE_VERSION}"
NPX_IMAGE="${IMAGE_PREFIX}-npx:${NPM_VERSION}-node${NODE_VERSION}"
DART_IMAGE="${IMAGE_PREFIX}-dart:${DART_VERSION}"
FLUTTER_IMAGE="${IMAGE_PREFIX}-flutter:${FLUTTER_VERSION}"
OWNERSHIP_DIR="$(mktemp -d /tmp/dugout-image-test.XXXXXX)"

cleanup() {
  rm -r "${OWNERSHIP_DIR}"
}
trap cleanup 0
trap 'exit 1' 1 2 3 15

for image in \
  "${PHP_IMAGE}" \
  "${COMPOSER_IMAGE}" \
  "${NODE_IMAGE}" \
  "${NPM_IMAGE}" \
  "${NPX_IMAGE}" \
  "${DART_IMAGE}" \
  "${FLUTTER_IMAGE}"; do
  docker image inspect "${image}" >/dev/null
done

docker run --rm "${PHP_IMAGE}" --version | grep -q '^PHP 8\.4\.'
php_status=0
docker run --rm "${PHP_IMAGE}" -r 'exit(23);' >/dev/null 2>&1 ||
  php_status=$?
[ "${php_status}" -eq 23 ] ||
  {
    echo "PHP failure status was not preserved." >&2
    exit 1
  }

docker run --rm "${COMPOSER_IMAGE}" --version | grep -q '^Composer version 2\.'
docker run --rm "${NODE_IMAGE}" --version | grep -q '^v22\.'
docker run --rm "${NPM_IMAGE}" --version | grep -q '^10\.'
docker run --rm "${NPX_IMAGE}" --version | grep -q '^10\.'
docker run --rm "${DART_IMAGE}" --version 2>&1 |
  grep -q "Dart SDK version: ${DART_VERSION}"
docker run --rm "${FLUTTER_IMAGE}" --version |
  grep -q "Flutter ${FLUTTER_VERSION}"

flutter_run_status=0
docker run --rm "${FLUTTER_IMAGE}" run >/dev/null 2>&1 ||
  flutter_run_status=$?
[ "${flutter_run_status}" -eq 64 ] ||
  {
    echo "Flutter image did not reject device execution." >&2
    exit 1
  }

docker run --rm \
  --read-only \
  --user "$(id -u):$(id -g)" \
  --workdir /workspace \
  --mount "type=bind,src=${OWNERSHIP_DIR},dst=/workspace" \
  --tmpfs "/tmp:rw,nosuid,nodev,exec" \
  "${PHP_IMAGE}" \
  -r 'file_put_contents("generated.txt", "owned by caller");'

file_owner="$(
  # The generated test path contains only mktemp's safe alphanumeric suffix.
  # shellcheck disable=SC2012
  ls -dn "${OWNERSHIP_DIR}/generated.txt" |
    awk '{ print $3 ":" $4 }'
)"
[ "${file_owner}" = "$(id -u):$(id -g)" ]

echo "All Dugout tool images pass command and version smoke tests."
