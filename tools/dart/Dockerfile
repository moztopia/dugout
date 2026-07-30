ARG DART_VERSION=3.12.2

FROM dart:${DART_VERSION} AS dart

LABEL org.opencontainers.image.title="Dugout Dart tool"
LABEL org.opencontainers.image.description="Single-command Dart SDK development tool"
LABEL org.opencontainers.image.source="https://github.com/mozrin/dugout"

WORKDIR /workspace

ENTRYPOINT ["dart"]
CMD ["--help"]
