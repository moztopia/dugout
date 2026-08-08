ARG REDIS_VERSION=7.4

FROM redis:${REDIS_VERSION}-alpine

LABEL org.opencontainers.image.title="Dugout Redis CLI"
LABEL org.opencontainers.image.source="https://github.com/moztopia/dugout"

ENTRYPOINT ["redis-cli"]
