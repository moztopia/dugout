FROM python:3.13-alpine

LABEL org.opencontainers.image.title="Dugout Tools"
LABEL org.opencontainers.image.source="https://github.com/moztopia/dugout"

RUN apk add --no-cache curl docker-cli && \
    pip install --no-cache-dir pyyaml

COPY tools/ /opt/dugout/tools/

RUN chmod +x /opt/dugout/tools/dugout/dugout && \
    chmod +x /opt/dugout/tools/barrel/barrel && \
    ln -s /opt/dugout/tools/dugout/dugout /usr/local/bin/dugout && \
    ln -s /opt/dugout/tools/barrel/barrel /usr/local/bin/barrel

ENV PYTHONPATH=/opt/dugout/tools

WORKDIR /workspace
