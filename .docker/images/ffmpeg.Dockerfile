FROM alpine:3.21

LABEL org.opencontainers.image.title="Dugout FFmpeg"
LABEL org.opencontainers.image.source="https://github.com/moztopia/dugout"

RUN apk add --no-cache ffmpeg

WORKDIR /workspace
