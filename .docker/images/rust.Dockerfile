FROM rust:alpine

LABEL org.opencontainers.image.title="Dugout Rust"
LABEL org.opencontainers.image.source="https://github.com/moztopia/dugout"

RUN apk add --no-cache musl-dev

WORKDIR /workspace
