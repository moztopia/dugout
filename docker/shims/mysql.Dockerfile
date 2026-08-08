ARG MYSQL_VERSION=8.4

FROM mysql:${MYSQL_VERSION}

LABEL org.opencontainers.image.title="Dugout MySQL Client"
LABEL org.opencontainers.image.source="https://github.com/moztopia/dugout"

ENTRYPOINT ["mysql"]
