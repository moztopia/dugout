ARG PHP_VERSION=8.4
ARG COMPOSER_VERSION=2

FROM composer:${COMPOSER_VERSION} AS composer_upstream

FROM php:${PHP_VERSION}-cli-alpine AS php_runtime

LABEL org.opencontainers.image.title="Dugout PHP tool family"
LABEL org.opencontainers.image.description="Single-command PHP and Composer development tools"
LABEL org.opencontainers.image.source="https://github.com/mozrin/dugout"

RUN apk add --no-cache \
        git \
        libzip \
        oniguruma \
        unzip \
    && apk add --no-cache --virtual .build-dependencies \
        $PHPIZE_DEPS \
        libzip-dev \
        oniguruma-dev \
    && docker-php-ext-install mbstring pdo_mysql zip \
    && pecl install redis \
    && docker-php-ext-enable redis \
    && apk del .build-dependencies

WORKDIR /workspace

FROM php_runtime AS php

ENTRYPOINT ["php"]
CMD ["--help"]

FROM php_runtime AS composer

COPY --from=composer_upstream /usr/bin/composer /usr/local/bin/composer

ENTRYPOINT ["composer"]
CMD ["--help"]
