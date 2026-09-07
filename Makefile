PROJECT = badabump

include python.mk

TOX_VERSION ?= 4.61.2
TOX_UV_VERSION ?= 1.36.0
TOX = $(UVX) --with="tox-uv==$(TOX_UV_VERSION)" tox==$(TOX_VERSION)

all: install

.PHONY: build
build: build-python

.PHONY: clean
clean: clean-python

.PHONY: distclean
distclean: distclean-python

.PHONY: install
install: install-python

.PHONY: lint
lint: lint-python

.PHONY: list-outdated
list-outdated: list-outdated-python

.PHONY: test
test: install clean test-only

.PHONY: test-only
test-only:
	TOXENV=$(TOXENV) $(TOX) $(TOX_ARGS)

.PHONY: test-%
test-%: install clean
	TOXENV=$(subst test-,,$@) $(TOX) $(TOX_ARGS)
