ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check lint static-check test verify

check: test

lint build verify: static-check

test: static-check
	python3 -m unittest discover -s "$(ROOT)/tests" -p 'test_*.py'

static-check:
	python3 "$(ROOT)/scripts/check-baseline.py"
