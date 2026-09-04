# Vendor

The only directory a consuming project copies.

Everything else in this repository is read, not copied.

```text
vendor/
├── ruff/                        linter and formatter configuration
│   ├── ruff.toml                       for a project with a standalone config
│   └── pyproject-fragment.toml         for a project with a single manifest
├── taplo/                       TOML formatter configuration
│   └── taplo.toml                      copied to .taplo.toml at a project root
└── tools/                       programs, standard library only
    ├── check_conventions.py            the eleven checks Ruff cannot express
    └── check_commit_message.py         the Conventional Commits form
```

## Why the split

A directory that holds a `ruff.toml` is governed by that `ruff.toml`, because
Ruff resolves the nearest configuration for each file it scans.

Keeping the templates in a leaf directory with no Python in it means the
template cannot silently govern the checkers that sit beside it.

That is not a hypothetical: it happened here, and the checkers were being
linted by a template with no line length set.

## What each file enforces

| File | Enforces |
| --- | --- |
| `ruff/ruff.toml` | Import order, modern-Python conversions, `zip(strict=)`, `pathlib` over `os.path`, naming, comprehensions, builtin shadowing, and the one-argument-per-line call form. |
| `ruff/pyproject-fragment.toml` | The same rules. Use this **or** `ruff.toml`, never both. |
| `taplo/taplo.toml` | The vertical form of a TOML array, which the formatter collapses by default. |
| `tools/check_conventions.py` | Import form, signatures, name and argument agreement, vertical formatting, blank-line structure, docstring shape, widths, comment markers, keyword order, `Final`, prose, and Markdown. |
| `tools/check_commit_message.py` | The Conventional Commits subject, body, and footer. |

Both programs take paths or text, exit non-zero on a finding, and take no
action of their own.

Neither imports the project it is checking, so neither can be defeated by an
import error in the code under inspection.

## Run the self-test before trusting a clean result

```sh
python3 tools/check_conventions.py --self-test
```

Each check runs against a snippet known to violate it, and the command fails
if the violation is not reported.

A repository-wide scan returning zero is either a fact or a broken pattern,
and from the outside those are the same result.

## The checker exempts two of its own checks, on its own file

Its rule data is demonstrative material: the British-spelling list contains
British spellings, and the self-test snippets contain the violations they
exist to provoke.

So `comments` and `prose` do not run on the checker itself.

Every other check does.

A checker that exempted its whole file would hide exactly the defects it
exists to find, and suppressing findings one at a time would hide the real
ones added later.

## What is deliberately not enforced here

**Rules a tool would have to guess at.**

Whether an enum needs string compatibility, whether a comment explains why
rather than what, whether `match` expresses structure better than an `if`, whether
a paragraph holds one sentence.

A checker that guesses produces false positives, and false positives train
people to ignore the tool.

**Rules a syntax-unaware pattern must not attempt.**

A regular expression matching `Name(` cannot tell a call from a class
definition.

Where a rule is about structure, the tool parses or the rule stays with
review.

**Three Ruff rule sets that look relevant.**

`TD` enforces a different, fixed marker vocabulary that contradicts this one.

`FIX` flags the presence of markers rather than their spelling.

`COM812` is redundant beside the formatter, on Ruff's own advice.

The reasoning is in `ruff/ruff.toml`.
