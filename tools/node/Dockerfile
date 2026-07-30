ARG NODE_VERSION=22

FROM node:${NODE_VERSION}-bookworm-slim AS node_runtime

LABEL org.opencontainers.image.title="Dugout Node.js tool family"
LABEL org.opencontainers.image.description="Single-command Node.js, npm, and npx development tools"
LABEL org.opencontainers.image.source="https://github.com/mozrin/dugout"

WORKDIR /workspace

FROM node_runtime AS node

ENTRYPOINT ["node"]
CMD ["--help"]

FROM node_runtime AS npm

ENTRYPOINT ["npm"]
CMD ["--help"]

FROM node_runtime AS npx

ENTRYPOINT ["npx"]
CMD ["--help"]
