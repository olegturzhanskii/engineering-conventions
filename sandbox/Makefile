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

.PHONY: help setup format format-check lint typecheck conventions test verify demo-violation

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

conventions: ## Run the portable checker, positive control first
	$(RUN) python3 tools/check_conventions.py --self-test
	$(RUN) python3 tools/check_conventions.py README.md counterexamples/README.md src tests Makefile

test: ## Run the tests
	$(RUN) pytest

verify: format-check lint typecheck conventions test ## Everything the gate can prove, in one shot

demo-violation: ## Show the checker catching a deliberate violation
	@echo "counterexamples/ is excluded from the gate. Pointed at directly, the checker reports:"
	@$(RUN) python3 tools/check_conventions.py counterexamples || true
