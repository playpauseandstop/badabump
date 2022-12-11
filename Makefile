PROJECT = badabump

include python.mk

TOX ?= tox

all: install

.PHONY: clean
clean: clean-python

.PHONY: distclean
distclean: distclean-python

.PHONY: install
install: install-python

.PHONY: lint
lint: lint-python

.PHONY: lint-and-test
lint-and-test: lint test

.PHONY: list-outdated
list-outdated: list-outdated-python

.PHONY: test
test: install clean test-only

.PHONY: test-only
test-only:
	TOXENV=$(TOXENV) $(TOX)

.PHONY: test-%
test-%: install clean
	TOXENV=$(subst test-,,$@) $(TOX)
