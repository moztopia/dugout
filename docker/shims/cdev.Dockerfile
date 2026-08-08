FROM alpine:3.21

LABEL org.opencontainers.image.title="Dugout C/C++ Toolchain"
LABEL org.opencontainers.image.source="https://github.com/moztopia/dugout"

RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    make \
    cmake \
    nasm \
    binutils \
    gdb \
    linux-headers \
    && wget -q https://flatassembler.net/fasm-1.73.32.tgz -O /tmp/fasm.tgz \
    && tar -xzf /tmp/fasm.tgz -C /opt \
    && ln -s /opt/fasm/fasm /usr/local/bin/fasm \
    && rm /tmp/fasm.tgz

WORKDIR /workspace
