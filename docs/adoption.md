# Adoption

How a Python project takes on this standard, what it copies, what it only
references, and how it layers its own decisions on top.

## Copy or reference?

**Reference `STANDARD.md` by version; copy `vendor/`.**

The two halves have opposite properties, and treating them the same is the
mistake to avoid.

`STANDARD.md` is an authority.

A copy of an authority drifts: six months later two projects hold two texts,
both called the standard, differing in ways nobody decided.

Naming a version instead gives a reviewer something to check a difference
against — is this a violation, or is this project on an older version?

A copy cannot answer that question.

`vendor/` is executable.

A project's verification gate must not depend on a path outside the project,
its reviewers must see the rules in the project's own diff, and its checks
must keep working when the standard's repository is not reachable.

Vendor it.

The version reference belongs in the project's contributor documentation, in
one line:

```markdown
This project conforms to the engineering conventions standard, v1.1.0.
```

## What each file is for

| File | Copied? | Why |
| --- | --- | --- |
| `STANDARD.md` | **No — reference it** | An authority. A copy drifts silently. |
| `CHANGELOG.md` | No | Read it when moving between versions. |
| `docs/adoption.md` | No | This document. Procedure, not project content. |
| `docs/workflow.md` | No | Read once, when auditing an existing codebase. |
| `vendor/ruff/ruff.toml` | **Yes** | The project's linter must run from the project. |
| `vendor/ruff/pyproject-fragment.toml` | **Alternative** | Use this **or** `ruff.toml`, never both. |
| `vendor/taplo/taplo.toml` | **Yes** | Copy to `.taplo.toml`, or the formatter undoes every vertical array. |
| `vendor/tools/check_conventions.py` | **Yes, optional** | Adds the fourteen checks Ruff cannot express. |
| `vendor/tools/check_commit_message.py` | Optional | Only if commit messages are checked mechanically. |
| `sandbox/` | No | Reference material: a small conforming project to read. |

## The minimal path

Three steps, and a project is enforcing everything a standard linter can
prove.

**1. Take the Ruff configuration.**

```sh
cp vendor/ruff/ruff.toml /path/to/project/ruff.toml
```

A project that keeps all configuration in one manifest pastes
`vendor/ruff/pyproject-fragment.toml` into its `pyproject.toml` instead.

Use one or the other; two Ruff configurations in one project is a bug that
presents as confusion.

**2. Add what is project-local.**

The vendored file deliberately carries no `line-length`, no `src`, and no
exclusions, because none of those follow from the standard.

Add them:

```toml
line-length = 120

src = [
  "src",
  "tests",
]

extend-exclude = [
  "docs",
]
```

**Take the TOML configuration too.**

```sh
cp vendor/taplo/taplo.toml /path/to/project/.taplo.toml
```

Without it, `taplo fmt` collapses every multi-line array back onto one line and
the vertical form in §4 cannot survive a single save.

Taplo searches upward from the working directory rather than from the file it
is given, so an editor that formats on save has to run it from the project
root.

**3. Put it in the gate.**

```make
lint:
	ruff check .

format-check:
	ruff format --check .
```

## The full path

**4. Vendor the checker, and record the commit you copied it from.**

```sh
cp vendor/tools/check_conventions.py /path/to/project/tools/
```

It is standard library only, takes paths, exits non-zero on a finding, and
does nothing else.

It has no dependency on this repository once copied.

**5. Prove the checker runs before trusting a clean result.**

```sh
python3 tools/check_conventions.py --self-test
```

This runs every check against a snippet known to violate it.

A repository-wide scan returning zero is either a fact or a broken pattern,
and the two look identical from the outside.

**6. Add it to the gate, self-test first.**

```make
conventions:
	python3 tools/check_conventions.py --self-test
	python3 tools/check_conventions.py src tests
```

The order matters.

A gate that runs the scan without the control can pass because the scan broke.

The checker also reads notebooks, `SHA256SUMS`, and the workflows, Makefiles,
Dockerfiles, and shell scripts that may download a tool, so name the paths
that hold them as well.

**7. Name the version** in the project's contributor documentation.

## Keep the vendored files byte-identical

**The project's own formatter will rewrite them if you let it.**

A vendored file was formatted at the standard's line length.

A project with a different line length runs `ruff format`, the file is
rewritten, and the diff against upstream is gone — along with the ability to
tell an intentional local change from formatter noise.

Exclude the vendored directory from the project's own formatting and linting,
and say why:

```toml
[tool.ruff]
# WARN:
# `tools/` holds vendored files.
#
# This project's line length differs from the one they were formatted at, so `ruff format` would rewrite them and
# destroy the diff against the version this project claims to follow.
#
# They are checked upstream, not here.
extend-exclude = [
  "tools",
]
```

**Keep the type checker pointed at them.**

Excluding a directory from style enforcement is not a reason to stop checking
it for errors; a type checker found a real defect in the checker itself this
way.

**Record the commit they came from, and prove they still match it.**

A version names a release for a reader, and a commit is what a comparison can
rely on, because a tag can be moved and a commit cannot.

```sh
git -C path/to/standard show COMMIT:vendor/tools/check_conventions.py \
    | diff -u - tools/check_conventions.py
```

Comparing with the commit rather than with a working copy of the standard
keeps uncommitted or later changes there out of the answer.

Run the comparison whenever the copies are refreshed, and before a release.

**Keep the comparison out of the gate.**

It needs the standard's repository, and the gate must keep working when that
repository is not reachable; between refreshes, the project's own history is
what shows that the copies have not changed.

## Layering project configuration

**Add to the vendored files; do not edit their rules.**

A project that needs a rule set the standard does not require — stricter
datetime handling, annotation coverage, a domain-specific banned API — extends
the selection in its own configuration and says why in a comment at that line.

A project that must *disable* a rule the standard requires records that as an
exception, below.

The reason for the discipline is reviewability.

When the vendored file differs from the upstream one only by additions, a
reviewer can diff it against the version the project claims and see the delta
in seconds.

## Configuring the checker

The checker reads an optional table from the nearest `pyproject.toml`, walking
upward from the working directory.

```toml
[tool.check-conventions]
# NOTE:
# Modules this project uses as a namespace, each traceable to one of the four semantic import exceptions the standard
# names.
#
# State the reason here.
namespace-modules = [
  "httpx",
]

# NOTE:
# Paths excluded from the scan.
#
# An exclusion is a recorded exception, and the reason belongs beside it.
exclude = [
  "tests/fixtures/*",
]
```

`--namespace-module MODULE` adds one for a single run, without editing the
manifest.

**The self-test ignores both.**

It runs against the built-in defaults, because it tests the checker rather
than the project.

Without that isolation, a project that exempts a module the control snippet
uses would disable the control and report a failure that is really a
configuration effect.

**An exclusion must hide exactly what it claims to.**

Before recording one, check what it suppresses:

```sh
cp the/excluded/file.py /tmp/probe.py \
    && python3 tools/check_conventions.py /tmp/probe.py
```

If more comes back than the exception describes, the exclusion is too wide.

## Recording a project-specific exception

An exception lives at the site it applies to, never in a central list.

**In code**, a marker comment naming the rule and the reason:

```python
# WARN:
# The configuration argument is positional-only in this library's compiled extension: passing it by keyword raises
# TypeError at runtime.
#
# This departs from the "prefer keywords for external APIs" rule deliberately.
producer = Producer(
    configuration,
)
```

**In configuration**, a per-file ignore with the same explanation:

```toml
[tool.ruff.lint.per-file-ignores]
# WARN:
# Naive datetimes are the subject under test here, not an oversight.
"tests/shared/test_time.py" = [
  "DTZ001",
]
```

A deviation that exists only in the code is indistinguishable from a mistake,
and the next person to run a conformance pass will "fix" it.

## Two ways to run the same check

**Vendored, from inside the project.**

```sh
python3 tools/check_conventions.py --self-test \
    && python3 tools/check_conventions.py src tests
```

This is the development gate: it is fast, it needs nothing outside the
project, and it keeps working when the standard's repository is not reachable.

**External, from the standard's own checkout.**

```sh
python3 /path/to/engineering-conventions/vendor/tools/check_conventions.py \
    --project /path/to/project src tests
```

This is the authoritative conformance check: it runs the version the standard
currently publishes, against a project that has vendored some possibly older
copy.

**Both must agree.**

The external run reads the project's own `[tool.check-conventions]` table and
matches exclusions relative to the project root, so an exclusion behaves the
same either way.

A disagreement means the vendored copy has drifted, and

```sh
python3 tools/check_conventions.py --version
```

says which standard version the vendored copy implements.

## Optional: running the gate from pre-commit

**`pre-commit` is not part of this standard and is not required.**

`make verify` already defines the gate, and a second definition of the same gate
is a second thing to keep in sync.

A project that already uses `pre-commit` can invoke the existing gate rather
than restating it:

```yaml
repos:
  - repo: local
    hooks:
      - id: conventions
        name: engineering conventions
        entry: make conventions
        language: system
        pass_filenames: false
        always_run: true
```

`pass_filenames: false` and `always_run: true` matter.

Without them `pre-commit` passes only the changed files, the positive control
never runs, and the hook can pass because the scan was never given a chance to
fail.

**Do not adopt `pre-commit` to satisfy this standard.**

A hook is opt-in per clone, so it cannot be relied on as a gate, and a project
whose gate lives only in a hook has no gate at all for anyone who has not
installed it.

## Violations and candidates

The checker reports two kinds of finding, and the difference decides what to
do next.

A **violation** is proved from the syntax tree or from a measurement, and it fails
the gate.

A **candidate** is a suspect that a person must judge, and it does not fail the
gate unless `--strict` is given.

The American-English check is the clearest case.

A word list and a morphological pattern can surface likely British spellings;
neither can prove that a document is written in American English, because the
vocabulary is open and the patterns have honest exceptions.

**Do not read a clean candidate run as compliance.**

Read it as "nothing suspicious was noticed," and keep the convention in
review.

## Keeping up to date

The standard is versioned; a project moves deliberately.

1. Read `CHANGELOG.md` from the version the project names to the new one.
2. Re-vendor `vendor/`, keeping the project-local additions, and record the
   commit you copied from.
3. Run the gate, and treat new findings as an audit rather than a cleanup —
   `docs/workflow.md` covers the difference.
4. Update the version line in the project's contributor documentation.

Nothing forces a project to move.

A project that stays on an older version and says so is in a better position
than one that copied the text and no longer knows what it diverged from.

## The one check that does not vendor

Keyword-argument order is checkable inside a file, and `check_conventions.py`
does that.

Order against a **third-party** signature needs the library installed and
importable, so it is a sweep rather than a gate:

```python
from ast import (
    parse,
)
from pathlib import (
    Path,
)

for path in Path(
    "src",
).rglob(
    pattern="*.py",
):
    tree = parse(
        source=path.read_text(
            encoding="utf-8",
        ),
    )

    # TODO:
    # Resolve each call's callee through the file's own imports, then compare the keyword names at that call site
    # against the parameter order `inspect.signature` reports for the resolved object.
    #
    # That last step needs the library installed and importable, which is what keeps this a sweep rather than a gate.
```

Run it when adopting the standard and when upgrading a major dependency.

It is worth running at least once: a project's own calls tend to be consistent
because one person wrote both sides, and calls into a library drift toward
whatever order read nicely on the day.
