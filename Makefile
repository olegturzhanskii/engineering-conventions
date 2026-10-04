.DEFAULT_GOAL := help

# NOTE:
# Every third-party tool runs through the project's own locked environment.
#
# A bare `ruff` or `pytest` resolves to whatever the shell happens to offer, and a run against a global Ruff and ty
# below the floors this manifest declares reports green while proving nothing.
#
# `--locked` also fails when `uv.lock` no longer describes the manifest, so the gate cannot pass on a lock that is out
# of date.
RUN := uv run --locked

# NOTE:
# The checker runs through `$(RUN)` for the interpreter, not for a package.
#
# It imports nothing outside the standard library, which is the claim `docs/adoption.md` makes to an adopter, but it
# does need the language version the manifest requires, and a bare `python3` can be older than that.

.PHONY: help setup format format-check lint typecheck conventions external drift test sandbox verify

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-16s %s\n", $$1, $$2}'

setup: ## Create the environment this gate runs in
	uv sync --locked

format: ## Apply formatting
	$(RUN) ruff format .

format-check: ## Check formatting without changing files
	$(RUN) ruff format --check .

lint: ## Run the linter
	$(RUN) ruff check .

typecheck: ## Run the type checker
	$(RUN) ty check

conventions: ## Run the checker on this repository, positive control first
	$(RUN) python3 vendor/tools/check_conventions.py --self-test
	$(RUN) python3 vendor/tools/check_conventions.py \
		STANDARD.md README.md CHANGELOG.md docs vendor Makefile \
		sandbox/README.md sandbox/counterexamples/README.md sandbox/src sandbox/tests sandbox/Makefile

external: ## Audit another project from here: make external P=/path D="src tests"
	$(RUN) python3 vendor/tools/check_conventions.py --self-test
	$(RUN) python3 vendor/tools/check_conventions.py --project $(P) $(D)

drift: ## The vendored copies must match what this repository publishes
	@diff -u vendor/tools/check_conventions.py sandbox/tools/check_conventions.py \
		&& echo "  sandbox's vendored checker matches vendor/tools"
	@diff -u vendor/taplo/taplo.toml .taplo.toml \
		&& diff -u vendor/taplo/taplo.toml sandbox/.taplo.toml \
		&& echo "  both .taplo.toml copies match vendor/taplo"

test: ## Run the sandbox tests
	$(RUN) pytest

sandbox: ## Prove the checker catches every deliberate counterexample
	@expected=$$(ls sandbox/counterexamples/*.py | wc -l | tr -d " "); \
	reported=$$($(RUN) python3 vendor/tools/check_conventions.py sandbox/counterexamples 2>/dev/null \
		| sed -n "s|^\(sandbox/counterexamples/[^:]*\):.*|\1|p" | sort -u | wc -l | tr -d " "); \
	if [ "$$reported" = "$$expected" ]; then \
		echo "  ok  every counterexample is still caught ($$reported/$$expected)"; \
	else \
		echo "  FAIL: $$reported of $$expected counterexamples reported"; exit 1; \
	fi

verify: format-check lint typecheck conventions drift sandbox test ## Everything the gate can prove, in one shot
