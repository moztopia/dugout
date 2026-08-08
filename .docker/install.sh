#!/bin/sh
# Dugout installer — containerized development tools
# Usage: curl -fsSL https://raw.githubusercontent.com/moztopia/dugout/main/.docker/install.sh | sh
set -eu

REPO="https://raw.githubusercontent.com/moztopia/dugout/main"
INSTALL_DIR="${HOME}/.local/bin/dugout"
SHIMS="node npm npx php composer"

printf '\n  Dugout — installing containerized dev tools\n\n'

mkdir -p "$INSTALL_DIR"

for shim in $SHIMS; do
  curl -fsSL "$REPO/bin/$shim" -o "$INSTALL_DIR/$shim"
  chmod +x "$INSTALL_DIR/$shim"
  printf '  ✓ %s\n' "$shim"
done

# Check PATH
case ":${PATH}:" in
  *":${INSTALL_DIR}:"*) ;;
  *)
    printf '\n  Add this to your shell config:\n'
    printf '  export PATH="$HOME/.local/bin/dugout:$PATH"\n'
    ;;
esac

printf '\n  Done. Open a new terminal and try:\n'
printf '    node --version | npm --version | php --version | composer --version\n\n'
