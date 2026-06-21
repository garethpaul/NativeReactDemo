ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s\n' "$$path" | sed 's/^ //'); dirname -- "$$path")

.PHONY: build check lint static-check test verify

check: test

lint build verify: static-check

test: static-check
	python3 -m unittest discover -s "$(ROOT)/tests" -p 'test_*.py'

static-check:
	python3 "$(ROOT)/scripts/check-baseline.py"
