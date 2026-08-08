ARG NODE_VERSION=24

FROM node:${NODE_VERSION}-alpine

LABEL org.opencontainers.image.title="Dugout Node.js"
LABEL org.opencontainers.image.source="https://github.com/moztopia/dugout"

WORKDIR /workspace
