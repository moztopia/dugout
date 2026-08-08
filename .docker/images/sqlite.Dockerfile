FROM alpine:3.21

LABEL org.opencontainers.image.title="Dugout SQLite"
LABEL org.opencontainers.image.source="https://github.com/moztopia/dugout"

RUN apk add --no-cache sqlite

WORKDIR /workspace

ENTRYPOINT ["sqlite3"]
