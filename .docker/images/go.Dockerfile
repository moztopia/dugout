ARG GO_VERSION=1.26

FROM golang:${GO_VERSION}-alpine

LABEL org.opencontainers.image.title="Dugout Go"
LABEL org.opencontainers.image.source="https://github.com/moztopia/dugout"

WORKDIR /workspace
