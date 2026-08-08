ARG MARIADB_VERSION=11.4

FROM mariadb:${MARIADB_VERSION}

LABEL org.opencontainers.image.title="Dugout MariaDB Client"
LABEL org.opencontainers.image.source="https://github.com/moztopia/dugout"

ENTRYPOINT ["mariadb"]
