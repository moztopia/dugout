#!/bin/sh
# Dugout installer — installs the dugout CLI
# Usage: curl -fsSL https://github.com/moztopia/dugout/raw/main/.docker/install.sh | sh
set -eu

REPO="https://github.com/moztopia/dugout/raw/main"
INSTALL_DIR="${HOME}/.local/bin/dugout"

printf '\n  Dugout — installing CLI\n\n'

mkdir -p "$INSTALL_DIR"

curl -fsSL "$REPO/dugout" -o "$INSTALL_DIR/dugout"
chmod +x "$INSTALL_DIR/dugout"
printf '  ✓ dugout\n'

# Check PATH
case ":${PATH}:" in
  *":${INSTALL_DIR}:"*) ;;
  *)
    printf '\n  Add this to your shell config:\n'
    printf '  export PATH="$HOME/.local/bin/dugout:$PATH"\n'
    ;;
esac

printf '\n  Done. Now run:\n'
printf '    dugout shims install\n\n'
