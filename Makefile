.PHONY: \
	clean \
	distclean \
	install \
	lint \
	list-outdated \
	test \
	test-only

PROJECT = badabump

include python.mk

all: install

clean: clean-python

distclean: distclean-python

install: install-python

lint: lint-python

list-outdated: list-outdated-python

test: test-python

test-only: test-python-only
