ARG POSTGRES_VERSION=17

FROM postgres:${POSTGRES_VERSION}-alpine

LABEL org.opencontainers.image.title="Dugout PostgreSQL Client"
LABEL org.opencontainers.image.source="https://github.com/moztopia/dugout"

ENTRYPOINT ["psql"]
