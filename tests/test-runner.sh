#!/bin/sh
set -eu

ROOT_DIR="$(CDPATH='' cd "$(dirname "$0")/.." && pwd)"
TEST_DIR="$(mktemp -d /tmp/dugout-runner-test.XXXXXX)"

cleanup() {
  rm -r "${TEST_DIR}"
}
trap cleanup 0
trap 'exit 1' 1 2 3 15

mkdir -p \
  "${TEST_DIR}/bin" \
  "${TEST_DIR}/project/.dugout" \
  "${TEST_DIR}/project/nested/directory"

cp "${ROOT_DIR}/share/dugout/catalog" "${TEST_DIR}/catalog"

cat > "${TEST_DIR}/project/.dugout/tool-versions" <<'EOF'
php 8.4
node 22
EOF

cat > "${TEST_DIR}/bin/docker" <<'EOF'
#!/bin/sh
set -eu

case "${1:-}" in
  info)
    exit 0
    ;;
  image)
    exit 0
    ;;
  network)
    exit 0
    ;;
  run)
    shift
    for argument in "$@"; do
      printf '<%s>\n' "${argument}"
    done
    exit 0
    ;;
esac

exit 1
EOF
chmod 0755 "${TEST_DIR}/bin/docker"

export PATH="${TEST_DIR}/bin:${PATH}"
export DUGOUT_CATALOG="${TEST_DIR}/catalog"
export DUGOUT_IMAGE_PREFIX="example.test/moztopia/dugout"
export XDG_CACHE_HOME="${TEST_DIR}/cache"

cd "${TEST_DIR}/project/nested/directory"

output="$("${ROOT_DIR}/bin/node" script.js "argument with spaces")"

printf '%s\n' "${output}" |
  grep -Fqx '</workspace/nested/directory>'
printf '%s\n' "${output}" |
  grep -Fqx '<example.test/moztopia/dugout-node:22>'
printf '%s\n' "${output}" |
  grep -Fqx '<argument with spaces>'

if printf '%s\n' "${output}" | grep -Eq '<(-p|--publish|--privileged)>'; then
  echo "Runner added a forbidden Docker option." >&2
  exit 1
fi

"${ROOT_DIR}/bin/dug" verify >/dev/null
"${ROOT_DIR}/bin/dug" which php |
  grep -Fq 'example.test/moztopia/dugout-php:8.4'

rm "${TEST_DIR}/project/.dugout/tool-versions"
export DUGOUT_PROJECT_ROOT="${TEST_DIR}/project"
export DUGOUT_NODE_VERSION="24"

output="$("${ROOT_DIR}/bin/node" --version)"
printf '%s\n' "${output}" |
  grep -Fqx '<example.test/moztopia/dugout-node:24>'

mkdir -p "${TEST_DIR}/install-config"
DUGOUT_INSTALL_PREFIX="${TEST_DIR}/install" \
  XDG_CONFIG_HOME="${TEST_DIR}/install-config" \
  "${ROOT_DIR}/bin/dug" install >/dev/null

for installed_file in \
  bin/dug \
  bin/php \
  bin/composer \
  bin/node \
  bin/npm \
  bin/npx \
  share/dugout/catalog; do
  [ -f "${TEST_DIR}/install/${installed_file}" ]
done

[ -f "${TEST_DIR}/install-config/dugout/.env.example" ]
[ -f "${TEST_DIR}/install-config/dugout/.env" ]

cat > "${TEST_DIR}/bad.env" <<'EOF'
DUGOUT_UNKNOWN_SETTING=value
EOF

if DUGOUT_CONFIG="${TEST_DIR}/bad.env" \
  "${ROOT_DIR}/bin/dug" list >/dev/null 2>&1; then
  echo "Runner accepted an unknown configuration key." >&2
  exit 1
fi

echo "Dugout runner tests pass."
