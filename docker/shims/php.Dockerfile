ARG PHP_VERSION=8.4

FROM php:${PHP_VERSION}-cli-alpine

LABEL org.opencontainers.image.title="Dugout PHP"
LABEL org.opencontainers.image.source="https://github.com/moztopia/dugout"

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

RUN apk add --no-cache git unzip

WORKDIR /workspace
