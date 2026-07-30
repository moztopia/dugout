SHELL := /bin/sh
.DEFAULT_GOAL := help

-include .env

DUGOUT_IMAGE_PREFIX ?= moztopia/dugout
DUGOUT_PHP_VERSION ?= 8.4
DUGOUT_COMPOSER_VERSION ?= 2
DUGOUT_NODE_VERSION ?= 22
DUGOUT_NPM_VERSION ?= 10
DUGOUT_DART_VERSION ?= 3.12.2
DUGOUT_FLUTTER_VERSION ?= 3.44.2

IMAGE_PREFIX ?= $(DUGOUT_IMAGE_PREFIX)
PHP_VERSION ?= $(DUGOUT_PHP_VERSION)
COMPOSER_VERSION ?= $(DUGOUT_COMPOSER_VERSION)
NODE_VERSION ?= $(DUGOUT_NODE_VERSION)
NPM_VERSION ?= $(DUGOUT_NPM_VERSION)
DART_VERSION ?= $(DUGOUT_DART_VERSION)
FLUTTER_VERSION ?= $(DUGOUT_FLUTTER_VERSION)

PHP_IMAGE := $(IMAGE_PREFIX)-php:$(PHP_VERSION)
COMPOSER_IMAGE := $(IMAGE_PREFIX)-composer:$(COMPOSER_VERSION)-php$(subst .,,$(PHP_VERSION))
NODE_IMAGE := $(IMAGE_PREFIX)-node:$(NODE_VERSION)
NPM_IMAGE := $(IMAGE_PREFIX)-npm:$(NPM_VERSION)-node$(NODE_VERSION)
NPX_IMAGE := $(IMAGE_PREFIX)-npx:$(NPM_VERSION)-node$(NODE_VERSION)
DART_IMAGE := $(IMAGE_PREFIX)-dart:$(DART_VERSION)
FLUTTER_IMAGE := $(IMAGE_PREFIX)-flutter:$(FLUTTER_VERSION)

.PHONY: help install services-up services-stop services-restart services-status build-tools build-php build-composer build-node build-npm build-npx build-dart build-flutter test test-runner test-images lint

help:
	@printf '%s\n' \
		'Dugout service and tool development' \
		'' \
		'  make install          Install dug under ~/.local' \
		'  make services-up      Create moznet and start shared services' \
		'  make services-stop    Stop shared services without removing moznet' \
		'  make services-restart Restart running shared services' \
		'  make services-status  Show shared service status' \
		'  make build-tools      Build all initial tool images' \
		'  make test             Run runner and image contract tests' \
		'  make lint             Validate project-owned shell scripts' \
		'' \
		'Overrides:' \
		'  IMAGE_PREFIX          Default: moztopia/dugout' \
		'  PHP_VERSION           Default: 8.4' \
		'  COMPOSER_VERSION      Default: 2' \
		'  NODE_VERSION          Default: 22' \
		'  NPM_VERSION           Default: 10' \
		'  DART_VERSION          Default: 3.12.2' \
		'  FLUTTER_VERSION       Default: 3.44.2'

install:
	./bin/dug install

services-up:
	docker compose up --detach

services-stop:
	docker compose stop

services-restart:
	docker compose restart

services-status:
	docker compose ps

build-tools: build-php build-composer build-node build-npm build-npx build-dart build-flutter

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

build-dart:
	docker build \
		--build-arg DART_VERSION=$(DART_VERSION) \
		--file tools/dart/Dockerfile \
		--target dart \
		--tag $(DART_IMAGE) \
		.

build-flutter:
	docker build \
		--build-arg FLUTTER_VERSION=$(FLUTTER_VERSION) \
		--file tools/flutter/Dockerfile \
		--target flutter \
		--tag $(FLUTTER_IMAGE) \
		.

test: lint test-runner test-images

test-runner:
	./tests/test-runner.sh

test-images:
	IMAGE_PREFIX=$(IMAGE_PREFIX) \
	PHP_VERSION=$(PHP_VERSION) \
	COMPOSER_VERSION=$(COMPOSER_VERSION) \
	NODE_VERSION=$(NODE_VERSION) \
	NPM_VERSION=$(NPM_VERSION) \
	DART_VERSION=$(DART_VERSION) \
	FLUTTER_VERSION=$(FLUTTER_VERSION) \
	./tests/test-images.sh

lint:
	./tests/check-shell.sh
