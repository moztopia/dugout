SHELL := /bin/sh
.DEFAULT_GOAL := help

DUGOUT_IMAGE_PREFIX ?= moztopia/dugout
DUGOUT_PHP_VERSION ?= 8.4
DUGOUT_COMPOSER_VERSION ?= 2
DUGOUT_NODE_VERSION ?= 22
DUGOUT_NPM_VERSION ?= 10

IMAGE_PREFIX ?= $(DUGOUT_IMAGE_PREFIX)
PHP_VERSION ?= $(DUGOUT_PHP_VERSION)
COMPOSER_VERSION ?= $(DUGOUT_COMPOSER_VERSION)
NODE_VERSION ?= $(DUGOUT_NODE_VERSION)
NPM_VERSION ?= $(DUGOUT_NPM_VERSION)

PHP_IMAGE := $(IMAGE_PREFIX)-php:$(PHP_VERSION)
COMPOSER_IMAGE := $(IMAGE_PREFIX)-composer:$(COMPOSER_VERSION)-php$(subst .,,$(PHP_VERSION))
NODE_IMAGE := $(IMAGE_PREFIX)-node:$(NODE_VERSION)
NPM_IMAGE := $(IMAGE_PREFIX)-npm:$(NPM_VERSION)-node$(NODE_VERSION)
NPX_IMAGE := $(IMAGE_PREFIX)-npx:$(NPM_VERSION)-node$(NODE_VERSION)

.PHONY: help up down stop restart status build-tools build-php build-composer build-node build-npm build-npx test test-compose test-barrel test-runner test-images lint lint-shell lint-markdown

help:
	@printf '%s\n' \
		'Dugout service and tool development' \
		'' \
		'  make up               Start the enabled utilities' \
		'  make down             Remove utility containers (keep their data)' \
		'  make stop             Stop the utilities' \
		'  make restart          Restart the utilities' \
		'  make status           Show utility status' \
		'  make test             Run runner and image contract tests' \
		'' \
		'Maintainer build overrides:' \
		'  IMAGE_PREFIX          Default: moztopia/dugout' \
		'  PHP_VERSION           Default: 8.4' \
		'  COMPOSER_VERSION      Default: 2' \
		'  NODE_VERSION          Default: 22' \
		'  NPM_VERSION           Default: 10'

up:
	@test -f .env || { printf '%s\n' 'Missing .env; run: cp .env.example .env'; exit 1; }
	docker compose up --detach

down:
	docker compose down

stop:
	docker compose stop

restart:
	docker compose restart

status:
	docker compose ps

build-tools: build-php build-composer build-node build-npm build-npx

build-php:
	docker build \
		--build-arg PHP_VERSION=$(PHP_VERSION) \
		--build-arg COMPOSER_VERSION=$(COMPOSER_VERSION) \
		--file tools/php/Dockerfile \
		--target php \
		--tag $(PHP_IMAGE) \
		.

build-composer:
	docker build \
		--build-arg PHP_VERSION=$(PHP_VERSION) \
		--build-arg COMPOSER_VERSION=$(COMPOSER_VERSION) \
		--file tools/php/Dockerfile \
		--target composer \
		--tag $(COMPOSER_IMAGE) \
		.

build-node:
	docker build \
		--build-arg NODE_VERSION=$(NODE_VERSION) \
		--file tools/node/Dockerfile \
		--target node \
		--tag $(NODE_IMAGE) \
		.

build-npm:
	docker build \
		--build-arg NODE_VERSION=$(NODE_VERSION) \
		--file tools/node/Dockerfile \
		--target npm \
		--tag $(NPM_IMAGE) \
		.

build-npx:
	docker build \
		--build-arg NODE_VERSION=$(NODE_VERSION) \
		--file tools/node/Dockerfile \
		--target npx \
		--tag $(NPX_IMAGE) \
		.

test: lint test-compose test-barrel test-runner test-images

test-compose:
	./tests/test-compose.sh

test-barrel:
	./tests/test-barrel.sh

test-runner:
	./tests/test-runner.sh

test-images:
	IMAGE_PREFIX=$(IMAGE_PREFIX) \
	PHP_VERSION=$(PHP_VERSION) \
	COMPOSER_VERSION=$(COMPOSER_VERSION) \
	NODE_VERSION=$(NODE_VERSION) \
	NPM_VERSION=$(NPM_VERSION) \
	./tests/test-images.sh

lint: lint-shell lint-markdown

lint-shell:
	./tests/check-shell.sh

lint-markdown:
	DUGOUT_CONFIG=$(CURDIR)/.env.example ./bin/npx --yes markdownlint-cli2 '**/*.md'
