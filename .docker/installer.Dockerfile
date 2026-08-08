FROM alpine:3.20

LABEL org.opencontainers.image.title="Dugout Installer"
LABEL org.opencontainers.image.source="https://github.com/moztopia/dugout"

COPY bin/ /shims/
COPY .docker/install.sh /install.sh

RUN chmod +x /install.sh /shims/*

ENTRYPOINT ["/install.sh"]
