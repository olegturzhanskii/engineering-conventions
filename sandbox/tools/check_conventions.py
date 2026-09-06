#!/usr/bin/env python3
# Copyright 2026 Oleg Turzhanskii
# SPDX-License-Identifier: Apache-2.0
"""
Checks the engineering conventions that a formatter and a linter cannot
express.

Findings come in two kinds, and the difference is the point.

A **violation** is proved: the check decides it from the syntax tree or from a
measurement, and a clean run is evidence.

A **candidate** is a suspect that a person or a model must judge.

A clean candidate run is not compliance, and this program never reports one as
though it were.

Usage:

    python check_conventions.py PATH [PATH ...]
    python check_conventions.py --project DIR PATH [PATH ...]
    python check_conventions.py --self-test
    python check_conventions.py --version

Exit status is non-zero when a violation is found.

Candidates are reported and do not change it unless `--strict` is given.
"""

from argparse import (
    ArgumentParser,
)
from ast import (
    AST,
    AsyncFunctionDef,
    Attribute,
    Call,
    ClassDef,
    Dict,
    FunctionDef,
    GeneratorExp,
    If,
    Import,
    ImportFrom,
    List,
    Match,
    Module,
    Name,
    Set,
    Store,
    Subscript,
    Try,
    Tuple,
    get_docstring,
    iter_child_nodes,
    stmt,
    walk,
)
from ast import (
    parse as parse_source,
)
from collections.abc import (
    Mapping,
    Sequence,
)
from collections.abc import (
    Set as AbstractSet,
)
from dataclasses import (
    dataclass,
)
from fnmatch import (
    fnmatch,
)
from itertools import (
    pairwise,
)
from pathlib import (
    Path,
)
from re import (
    compile as compile_pattern,
)
from sys import (
    stderr,
)
from tokenize import (
    COMMENT,
    TokenError,
    generate_tokens,
)
from tomllib import (
    TOMLDecodeError,
    loads,
)
from types import (
    MappingProxyType,
)
from typing import (
    Final,
    final,
)

# NOTE:
# The version of `STANDARD.md` whose rules this program implements.
#
# A vendored copy states which standard it came from, so a project can report conformance and a reviewer can tell a
# stale copy from a local change.
STANDARD_VERSION: Final = "1.0.1"

# NOTE:
# Column boundaries from the standard's width section.
#
# A meaningful symbol must not reach the column after these, and trailing whitespace is not a meaningful symbol, so
# every measurement strips it first.
COMMENT_COLUMNS: Final = 118

PROSE_COLUMNS: Final = 78

# NOTE:
# The `todo-comments` vocabulary and the aliases that specification defines.
#
# Aliases are recognized rather than rejected, because the upstream specification permits them; preferring one
# spelling within a project is a project decision and not something this program decides.
MARKERS: Final = frozenset(
    {
        "FIX",
        "HACK",
        "NOTE",
        "PERF",
        "TEST",
        "TODO",
        "WARN",
    },
)

ALIASES: Final = frozenset(
    {
        "BUG",
        "FAILED",
        "FIXIT",
        "FIXME",
        "INFO",
        "ISSUE",
        "OPTIM",
        "OPTIMIZE",
        "PASSED",
        "PERFORMANCE",
        "TESTING",
        "WARNING",
        "XXX",
    },
)

# NOTE:
# A framework that inspects a signature and calls the function itself owns that signature, so the argument rules do
# not reach it.
#
# There is no caller to protect.
FRAMEWORK_DECORATORS: Final = frozenset(
    {
        "delete",
        "fixture",
        "get",
        "head",
        "options",
        "patch",
        "post",
        "put",
        "websocket",
    },
)

# NOTE:
# Modules used as a namespace, which the import rule exempts.
#
# A project adds its own in `[tool.check-conventions] namespace-modules`; editing this default is the wrong place,
# because the vendored copy must stay diffable against what the standard publishes.
DEFAULT_NAMESPACE_MODULES: Final = frozenset(
    {
        "pytest",
    },
)

# NOTE:
# The two languages this program reads.
#
# Everything else in a repository is left to the tool that owns it, and a file named on the command line is read by
# its suffix rather than by a guess at its content.
MARKDOWN_SUFFIX: Final = ".md"

PYTHON_SUFFIX: Final = ".py"

SUFFIXES: Final = (
    MARKDOWN_SUFFIX,
    PYTHON_SUFFIX,
)

# NOTE:
# Directories skipped when a directory argument is expanded.
#
# They hold generated or third-party files, never the source a project is judged on.
#
# A file named explicitly on the command line is never skipped.
SKIPPED_DIRECTORIES: Final = frozenset(
    {
        ".git",
        ".hg",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".rumdl_cache",
        ".svn",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
        "site-packages",
        "venv",
    },
)

# NOTE:
# Candidate detection for American English, and nothing more than that.
#
# A finite list cannot prove a convention: it is incomplete by construction, misses inflected forms, and says nothing
# about vocabulary invented tomorrow.
#
# These entries and patterns surface suspects for a reader to judge.
BRITISH_WORDS: Final = frozenset(
    {
        "acknowledgement",
        "amongst",
        "analyse",
        "behaviour",
        "catalogue",
        "centre",
        "colour",
        "defence",
        "favour",
        "fibre",
        "judgement",
        "learnt",
        "licence",
        "metre",
        "programme",
        "towards",
        "whilst",
    },
)

# NOTE:
# Morphological suspects, kept deliberately narrow.
#
# `-ise`/`-isation` and a doubled consonant before `-ed`/`-ing` on a verb whose stem ends in a single `l` are the two
# patterns with a usable signal.
#
# Both still produce false positives — `advertise`, `install`, `enroll` — which is exactly why they are candidates.
#
# English words that end in `-ise` or `-ised` without being the British verb suffix.
#
# The pattern below is useless without them: `otherwise` and `exercise` alone accounted for most of its output on a
# real codebase.
#
# The list is incomplete by construction, which is why the pattern reports candidates rather than violations.
NOT_BRITISH_ISE: Final = frozenset(
    {
        "advertise",
        "arise",
        "chastise",
        "circumcise",
        "comprise",
        "compromise",
        "concise",
        "demise",
        "despise",
        "devise",
        "disguise",
        "enterprise",
        "excise",
        "exercise",
        "expertise",
        "franchise",
        "guise",
        "improvise",
        "incise",
        "likewise",
        "merchandise",
        "otherwise",
        "paradise",
        "precise",
        "premise",
        "promise",
        "revise",
        "rise",
        "supervise",
        "surmise",
        "surprise",
        "televise",
        "treatise",
        "wise",
    },
)

BRITISH_PATTERNS: Final = (
    compile_pattern(
        pattern=r"\b\w{4,}(?:ise|ising|ised|isation)\b",
    ),
    compile_pattern(
        pattern=r"\b(?:cancel|label|model|travel|signal|marvel|equal|total|fuel)l(?:ed|ing|er|ist)\b",
    ),
)

CONTRACTION: Final = compile_pattern(
    pattern=r"\b\w+(?:n't|'re|'ve|'ll|'m)\b",
)

# NOTE:
# A quoted span, so that the contraction rule stops at the quotation mark.
#
# §7 does not reach quoted speech, text, or data, because expanding a contraction inside a quotation misquotes
# whoever said it, and reporting one there is a false positive by construction.
QUOTED: Final = compile_pattern(
    pattern=r"\"[^\"]*\"|\u201c[^\u201d]*\u201d",
)

# NOTE:
# An inline code span, so that a prose rule stops at the backtick.
#
# §7 lists code among the things the prose rules do not reach, and a span between backticks is code by construction:
# `--fix`, `it doesn't` as a fixture string, and ` -- ` written to name the very sequence a rule looks for.
#
# A fenced block is handled a level up, by the Markdown check reading a fence for its language rather than its
# content, so this covers only the inline form.
CODE_SPAN: Final = compile_pattern(
    pattern=r"`[^`]*`",
)

# NOTE:
# A typewriter em dash, and only that.
#
# The pattern requires whitespace on both sides, which is what separates prose punctuation from every syntax that also
# spells itself with two hyphens: `--fix` and `--sample-size` are a flag, `var(--border)` is a CSS property,
# `-- comment` is SQL, and `A --> B` is a diagram edge.
#
# None of those has a space before the second hyphen.
#
# A fenced block never reaches this, because the Markdown check reads a fence for its language rather than its
# content, and a quoted span never reaches it either, for the reason §7 gives about quoted material.
DOUBLE_HYPHEN: Final = compile_pattern(
    pattern=r"(?<=\s)--(?=\s)",
)

MARKER_LIKE: Final = compile_pattern(
    pattern=r"#\s*([A-Z][A-Z0-9_]{2,})\s*:",
)

# NOTE:
# Markdown syntax that the width rule reads through rather than counts.
#
# A link is judged by its label and emphasis is judged by the words inside it, which is what a reader sees.
LINK: Final = compile_pattern(
    pattern=r"\[([^\]]*)\]\([^)]*\)",
)

EMPHASIS: Final = compile_pattern(
    pattern=r"[*_`]+",
)

SENTENCE_END: Final = compile_pattern(
    pattern=r"[.!?](?=\s|$)",
)

ORDERED_ITEM: Final = compile_pattern(
    pattern=r"^\d+[.)]\s",
)

# NOTE:
# Line starts that make a line structure rather than prose.
#
# A table row, a block quote, a list item, and a heading carry meaning in their layout, and §7 exempts each of them
# from the paragraph rule for that reason.
MARKDOWN_STRUCTURE: Final = (
    "#",
    "|",
    ">",
    "-",
    "*",
    "+",
)

# NOTE:
# Comment prefixes that belong to another tool.
#
# Their syntax is that tool's to define, so the marker rule does not reach them.
TOOL_COMMENTS: Final = (
    "!",
    "mypy:",
    "noqa",
    "pyright:",
    "ruff:",
    "ty:",
    "type:",
)

VIOLATION: Final = "violation"

CANDIDATE: Final = "candidate"

# NOTE:
# Configuration resolved once in `main`, then read by the checks.
#
# These are rebound deliberately and are therefore not `Final`.
EXCLUDED: tuple[str, ...] = ()

NAMESPACE_MODULES: frozenset[str] = DEFAULT_NAMESPACE_MODULES

PROJECT_ROOT: Path = Path()


@dataclass(
    frozen=True,
    kw_only=True,
    slots=True,
)
@final
class Finding:
    """
    One thing the checker found, and how much weight it carries.

    `kind` is `VIOLATION` when the check proves it and `CANDIDATE` when a
    person must decide.
    """

    path: Path

    line: int

    check: str

    kind: str

    message: str

    def render(
        self,
        *,
        root: Path,
    ) -> str:
        """
        Return the finding with its path relative to `root` where possible.
        """

        try:
            shown = self.path.resolve().relative_to(
                root.resolve(),
            )
        except ValueError:
            shown = self.path

        label = "candidate" if self.kind == CANDIDATE else "violation"

        return f"{shown}:{self.line}: [{self.check}/{label}] {self.message}"


def _violation(
    path: Path,
    line: int,
    check: str,
    message: str,
    /,
) -> Finding:
    """
    Return a proved finding.
    """

    return Finding(
        path=path,
        line=line,
        check=check,
        kind=VIOLATION,
        message=message,
    )


def _candidate(
    path: Path,
    line: int,
    check: str,
    message: str,
    /,
) -> Finding:
    """
    Return a finding a person must judge.
    """

    return Finding(
        path=path,
        line=line,
        check=check,
        kind=CANDIDATE,
        message=message,
    )


def _check_imports(
    path: Path,
    tree: AST,
    source: str,
    /,
) -> tuple[Finding, ...]:
    """
    Reports a plain module import outside the documented exceptions.
    """

    out: list[Finding] = []

    for node in walk(
        node=tree,
    ):
        if not isinstance(
            node,
            Import,
        ):
            continue

        for alias in node.names:
            if alias.asname is not None:
                continue

            if (
                alias.name.split(
                    sep=".",
                )[0]
                in NAMESPACE_MODULES
            ):
                continue

            out.append(
                _violation(
                    path,
                    node.lineno,
                    "imports",
                    f"`import {alias.name}` — import the names used, or record which exception applies",
                ),
            )

    return tuple(
        out,
    )


def _check_signatures(
    path: Path,
    tree: AST,
    source: str,
    /,
) -> tuple[Finding, ...]:
    """
    Reports a callable whose parameters are neither positional-only nor
    keyword-only.

    A private name takes `/`, a public one takes `*`, a framework-injected
    signature takes neither because the framework owns it, and a name the
    language defines is the language's to call.
    """

    out: list[Finding] = []

    for node in walk(
        node=tree,
    ):
        if not isinstance(
            node,
            FunctionDef | AsyncFunctionDef,
        ):
            continue

        # NOTE:
        # A name the language owns is exempt, because the language owns both the name and how the callable is
        # reached, and the two halves of that ownership point opposite ways.
        #
        # `__eq__` is reached through a slot and never by name, so its boundary is positional; `__init__` is called
        # by name all the time, so its boundary is keyword.
        #
        # The single-underscore form is the same case: `_generate_next_value_` and its `enum` siblings are declared
        # positional-or-keyword in typeshed, so writing `/` on one is an override the type checker rejects.
        #
        # Nothing in the syntax tree separates these, so the choice stays with the reader and §13 states it.
        if node.name.startswith(
            "_",
        ) and node.name.endswith(
            "_",
        ):
            continue

        if node.name.startswith(
            "test_",
        ) or _framework_injected(
            node,
        ):
            continue

        plain = tuple(
            argument.arg
            for argument in node.args.args
            if argument.arg
            not in {
                "self",
                "cls",
            }
        )

        if not plain:
            continue

        shape = (
            "positional-only with `/`"
            if node.name.startswith(
                "_",
            )
            else "keyword-only with `*`"
        )

        out.append(
            _violation(
                path,
                node.lineno,
                "signatures",
                f"`{node.name}` has plain parameters {plain}; it should be {shape}",
            ),
        )

    return tuple(
        out,
    )


def _framework_injected(
    node: FunctionDef | AsyncFunctionDef,
    /,
) -> bool:
    """
    Return whether a decorator hands this signature to a framework.
    """

    # NOTE:
    # An `Annotated[...]` parameter is a framework's own declaration: the framework reads the metadata and binds the
    # argument by name, so the calling convention is not the project's to choose.
    for argument in node.args.args + node.args.kwonlyargs:
        annotation = argument.annotation

        if (
            isinstance(
                annotation,
                Subscript,
            )
            and getattr(
                annotation.value,
                "id",
                None,
            )
            == "Annotated"
        ):
            return True

    for decorator in node.decorator_list:
        target = (
            decorator.func
            if isinstance(
                decorator,
                Call,
            )
            else decorator
        )

        if (
            isinstance(
                target,
                Attribute,
            )
            and target.attr in FRAMEWORK_DECORATORS
        ):
            return True

        if (
            isinstance(
                target,
                Name,
            )
            and target.id in FRAMEWORK_DECORATORS
        ):
            return True

    return False


def _check_naming(
    path: Path,
    tree: AST,
    source: str,
    /,
) -> tuple[Finding, ...]:
    """
    Reports a name and an argument convention that disagree.

    A candidate rather than a violation: whether a callable belongs to its
    module's surface is a design question, and the right correction is
    sometimes the name and sometimes the signature.
    """

    out: list[Finding] = []

    # NOTE:
    # A callable defined inside another callable is not its module's surface.
    #
    # It is reached through the reference the enclosing callable hands out — an executor's task, a transport's
    # handler, an observer — and never by name from another module, so the leading-underscore test §13 uses on a
    # module-level name decides nothing here.
    #
    # The convention is the one the reference imposes, and that is positional.
    nested = frozenset(
        id(
            inner,
        )
        for node in walk(
            node=tree,
        )
        if isinstance(
            node,
            FunctionDef | AsyncFunctionDef,
        )
        for inner in walk(
            node=node,
        )
        if isinstance(
            inner,
            FunctionDef | AsyncFunctionDef,
        )
        and inner is not node
    )

    for node in walk(
        node=tree,
    ):
        if not isinstance(
            node,
            FunctionDef | AsyncFunctionDef,
        ):
            continue

        if node.name.startswith(
            "__",
        ) and node.name.endswith(
            "__",
        ):
            continue

        if (
            id(
                node,
            )
            in nested
        ):
            continue

        if _framework_injected(
            node,
        ):
            continue

        positional = tuple(
            argument.arg
            for argument in node.args.posonlyargs
            if argument.arg
            not in {
                "self",
                "cls",
            }
        )

        if positional and not node.name.startswith(
            "_",
        ):
            out.append(
                _candidate(
                    path,
                    node.lineno,
                    "naming",
                    f"`{node.name}` is public and positional-only; rename it or make it keyword-only",
                ),
            )

    return tuple(
        out,
    )


def _check_calls(
    path: Path,
    tree: AST,
    source: str,
    /,
) -> tuple[Finding, ...]:
    """
    Reports bracketed syntax written on one line that the vertical convention
    explodes.

    Covers calls, definitions, class bases, container literals, and
    destructuring targets.

    The exclusions are the ones the language forces: an empty bracket, a sole
    generator argument, a bare tuple value, and a type subscript.
    """

    out: list[Finding] = []

    # NOTE:
    # Type syntax, not a container.
    #
    # `Callable[[str], None]` writes a list inside a subscript's slice and `dict[str, tuple[int, ...]]` writes a
    # tuple there; both are the type subscript §12.5 exempts, and neither is a literal a reader would explode.
    #
    # The exemption reaches inside the slice rather than stopping at it, because the construct that needs it is
    # always nested. A call in the same position is an index being computed rather than a type being written, so it
    # is not listed here and stays checked.
    subscripted = frozenset(
        id(
            inner,
        )
        for node in walk(
            node=tree,
        )
        if isinstance(
            node,
            Subscript,
        )
        for inner in walk(
            node=node.slice,
        )
        if isinstance(
            inner,
            Dict | List | Set | Tuple,
        )
    )

    for node in walk(
        node=tree,
    ):
        start = getattr(
            node,
            "lineno",
            None,
        )

        if start is None or start != getattr(
            node,
            "end_lineno",
            start,
        ):
            continue

        if isinstance(
            node,
            Call,
        ):
            elements = list(
                node.args,
            ) + list(
                node.keywords,
            )

            if len(
                elements,
            ) == 1 and isinstance(
                elements[0],
                GeneratorExp,
            ):
                continue

            label = "a call"

        elif isinstance(
            node,
            FunctionDef | AsyncFunctionDef,
        ):
            arguments = node.args

            elements = (
                arguments.posonlyargs
                + arguments.args
                + arguments.kwonlyargs
                + (
                    [
                        arguments.vararg,
                    ]
                    if arguments.vararg
                    else []
                )
                + (
                    [
                        arguments.kwarg,
                    ]
                    if arguments.kwarg
                    else []
                )
            )

            label = "a definition"

        elif isinstance(
            node,
            ClassDef,
        ):
            elements = list(
                node.bases,
            ) + list(
                node.keywords,
            )

            label = "a class base list"

        elif isinstance(
            node,
            Dict | List | Set,
        ):
            if (
                id(
                    node,
                )
                in subscripted
            ):
                continue

            elements = (
                list(
                    node.keys,
                )
                if isinstance(
                    node,
                    Dict,
                )
                else list(
                    node.elts,
                )
            )

            label = "a literal"

        elif isinstance(
            node,
            Tuple,
        ):
            if (
                id(
                    node,
                )
                in subscripted
            ):
                continue

            target = isinstance(
                node.ctx,
                Store,
            )

            # NOTE:
            # A destructuring target is where the bare-tuple exemption stops.
            #
            # On the right of an assignment, parenthesizing a bare tuple changes what the formatter produces; on the
            # left of one, and in a `for` or a comprehension, the parentheses are pure layout and the vertical form is
            # available for free.
            if not target and not _parenthesized(
                node,
                source,
            ):
                continue

            elements = list(
                node.elts,
            )

            # NOTE:
            # A one-element tuple's comma is mandatory syntax rather than a magic trailing comma, so it cannot signal
            # that the literal should be exploded and the formatter keeps it inline.
            if (
                len(
                    elements,
                )
                == 1
            ):
                continue

            label = "a destructuring target" if target else "a literal"

        else:
            continue

        if not elements:
            continue

        out.append(
            _violation(
                path,
                start,
                "calls",
                f"{label} with {
                    len(
                        elements,
                    )
                } element(s) on one line — one per line, trailing comma",
            ),
        )

    return tuple(
        out,
    )


def _parenthesized(
    node: Tuple,
    source: str,
    /,
) -> bool:
    """
    Return whether a tuple literal carries its own parentheses.

    A bare tuple takes no trailing comma: adding one makes the formatter
    introduce parentheses and explode it, which is a structural change rather
    than a formatting one.

    Matching only the first character is not enough, because a bare tuple
    whose first element is itself parenthesized starts with the same
    character.

    The parentheses must also span the whole literal.
    """

    segment = _source_segment(
        node,
        source,
    )

    if not segment.startswith(
        "(",
    ) or not segment.endswith(
        ")",
    ):
        return False

    depth = 0

    for (
        index,
        character,
    ) in enumerate(
        iterable=segment,
    ):
        if character == "(":
            depth += 1

        elif character == ")":
            depth -= 1

            if (
                depth == 0
                and index
                != len(
                    segment,
                )
                - 1
            ):
                return False

    return depth == 0


def _source_segment(
    node: Tuple,
    source: str,
    /,
) -> str:
    """
    Return the exact source text of a node that fits on one line.
    """

    lines = source.splitlines()

    if node.lineno - 1 >= len(
        lines,
    ):
        return ""

    return lines[node.lineno - 1][node.col_offset : node.end_col_offset]


def _check_blank_lines(
    path: Path,
    tree: AST,
    source: str,
    /,
) -> tuple[Finding, ...]:
    """
    Reports the two halves of the blank-line convention, checked separately.

    Statements in one body are separated by a blank line; a header and its own
    first statement are not; and a following clause header is separated from
    the body above it.
    """

    lines = source.splitlines()

    out: list[Finding] = []

    for node in walk(
        node=tree,
    ):
        for body in _bodies(
            node,
        ):
            out.extend(
                _separation_findings(
                    path,
                    body,
                    lines,
                ),
            )

        out.extend(
            _attachment_findings(
                path,
                node,
                lines,
            ),
        )

        out.extend(
            _clause_findings(
                path,
                node,
                lines,
            ),
        )

    return tuple(
        out,
    )


def _bodies(
    node: AST,
    /,
) -> tuple[tuple[stmt, ...], ...]:
    """
    Return every statement list this node owns.
    """

    found: list[tuple[stmt, ...]] = []

    for name in (
        "body",
        "orelse",
        "finalbody",
    ):
        block = getattr(
            node,
            name,
            None,
        )

        if (
            isinstance(
                block,
                list,
            )
            and block
            and hasattr(
                block[0],
                "lineno",
            )
        ):
            found.append(
                block,
            )

    for child in (
        getattr(
            node,
            "handlers",
            [],
        )
        or []
    ):
        found.append(
            tuple(
                child.body,
            ),
        )

    for child in (
        getattr(
            node,
            "cases",
            [],
        )
        or []
    ):
        found.append(
            tuple(
                child.body,
            ),
        )

    return tuple(
        found,
    )


def _separation_findings(
    path: Path,
    body: Sequence[stmt],
    lines: Sequence[str],
    /,
) -> tuple[Finding, ...]:
    """
    Reports two statements in one body with no blank line between them.
    """

    out: list[Finding] = []

    for (
        previous,
        current,
    ) in pairwise(
        body,
    ):
        # NOTE:
        # An import block is one declaration written across several statements, ordered by the import convention and
        # by the formatter.
        #
        # Separating its members would fight both.
        if isinstance(
            previous,
            Import | ImportFrom,
        ) and isinstance(
            current,
            Import | ImportFrom,
        ):
            continue

        end = getattr(
            previous,
            "end_lineno",
            None,
        )

        start = getattr(
            current,
            "lineno",
            None,
        )

        if end is None or start is None:
            continue

        gap = lines[end : start - 1]

        if any(line.strip() == "" for line in gap):
            continue

        out.append(
            _violation(
                path,
                start,
                "blank-lines",
                "no blank line between this statement and the one above it",
            ),
        )

    return tuple(
        out,
    )


def _attachment_findings(
    path: Path,
    node: AST,
    lines: Sequence[str],
    /,
) -> tuple[Finding, ...]:
    """
    Reports a blank line between a header and its own first statement.
    """

    if not isinstance(
        node,
        If | Try | Match | FunctionDef | AsyncFunctionDef | ClassDef,
    ):
        return ()

    body = getattr(
        node,
        "body",
        [],
    )

    if not body:
        return ()

    header_end = _header_line(
        node,
    )

    first = getattr(
        body[0],
        "lineno",
        None,
    )

    if first is None or first <= header_end + 1:
        return ()

    if not all(
        lines[index].strip() == ""
        for index in range(
            header_end,
            first - 1,
        )
    ):
        return ()

    return (
        _violation(
            path,
            first,
            "blank-lines",
            "blank line between a header and its own first statement",
        ),
    )


def _header_line(
    node: AST,
    /,
) -> int:
    """
    Return the last physical line of this node's own header.
    """

    body = getattr(
        node,
        "body",
        [],
    )

    first = (
        getattr(
            body[0],
            "lineno",
            None,
        )
        if body
        else None
    )

    candidates = [
        getattr(
            node,
            "lineno",
            1,
        ),
    ]

    for child in iter_child_nodes(
        node=node,
    ):
        end = getattr(
            child,
            "end_lineno",
            None,
        )

        if end is None:
            continue

        if (
            first is not None
            and getattr(
                child,
                "lineno",
                0,
            )
            >= first
        ):
            continue

        candidates.append(
            end,
        )

    return max(
        candidates,
    )


def _clause_findings(
    path: Path,
    node: AST,
    lines: Sequence[str],
    /,
) -> tuple[Finding, ...]:
    """
    Reports a following clause header with no blank line above it.

    Structural on purpose: a ternary's `else` is not a clause header, and a
    check that matches the word reports it.
    """

    out: list[Finding] = []

    clauses: list[tuple[list[stmt], int]] = []

    if isinstance(
        node,
        If,
    ):
        if node.orelse:
            clauses.append(
                (
                    node.body,
                    node.orelse[0].lineno,
                ),
            )

    elif isinstance(
        node,
        Try,
    ):
        previous = node.body

        for handler in node.handlers:
            clauses.append(
                (
                    previous,
                    handler.lineno,
                ),
            )

            previous = handler.body

        for block in (
            node.orelse,
            node.finalbody,
        ):
            if block:
                clauses.append(
                    (
                        previous,
                        block[0].lineno,
                    ),
                )

                previous = block

    for (
        body,
        following,
    ) in clauses:
        if not body:
            continue

        end = getattr(
            body[-1],
            "end_lineno",
            None,
        )

        if end is None:
            continue

        header = following - 1

        if header <= end:
            continue

        if any(
            lines[index].strip() == ""
            for index in range(
                end,
                header,
            )
        ):
            continue

        out.append(
            _violation(
                path,
                header,
                "blank-lines",
                "no blank line between a clause body and the clause header below it",
            ),
        )

    return tuple(
        out,
    )


def _check_docstrings(
    path: Path,
    tree: AST,
    source: str,
    /,
) -> tuple[Finding, ...]:
    """
    Reports a docstring whose quote shape or width breaks the convention.
    """

    lines = source.splitlines()

    out: list[Finding] = []

    for node in walk(
        node=tree,
    ):
        if not isinstance(
            node,
            FunctionDef | AsyncFunctionDef | ClassDef,
        ):
            continue

        if (
            get_docstring(
                node=node,
            )
            is None
        ):
            continue

        out.extend(
            _docstring_findings(
                path,
                node.body[0],
                lines,
            ),
        )

    if (
        isinstance(
            tree,
            Module,
        )
        and get_docstring(
            node=tree,
        )
        is not None
    ):
        out.extend(
            _docstring_findings(
                path,
                tree.body[0],
                lines,
            ),
        )

    return tuple(
        out,
    )


def _docstring_findings(
    path: Path,
    node: AST,
    lines: Sequence[str],
    /,
) -> tuple[Finding, ...]:
    """
    Reports the shape and width of one docstring.
    """

    start = getattr(
        node,
        "lineno",
        1,
    )

    end = getattr(
        node,
        "end_lineno",
        start,
    )

    out: list[Finding] = []

    opening = lines[start - 1].strip()

    quoted = opening.startswith(
        (
            '"""',
            "'''",
        ),
    )

    if (
        quoted
        and len(
            opening,
        )
        > 3
    ):
        out.append(
            _violation(
                path,
                start,
                "docstrings",
                "content on the opening line — the quotes stand alone",
            ),
        )

    if end == start:
        out.append(
            _violation(
                path,
                start,
                "docstrings",
                "a single-line docstring — the quotes stand on their own lines",
            ),
        )

    else:
        closing = lines[end - 1].strip()

        if closing not in {
            '"""',
            "'''",
        }:
            out.append(
                _violation(
                    path,
                    end,
                    "docstrings",
                    "content on the closing line — the quotes stand alone",
                ),
            )

    for index in range(
        start,
        end + 1,
    ):
        width = len(
            lines[index - 1].rstrip(),
        )

        if width > PROSE_COLUMNS:
            out.append(
                _violation(
                    path,
                    index,
                    "widths",
                    f"a docstring line reaches column {width}, past {PROSE_COLUMNS}",
                ),
            )

    return tuple(
        out,
    )


def _check_comments(
    path: Path,
    tree: AST,
    source: str,
    /,
) -> tuple[Finding, ...]:
    """
    Reports comment width, marker spelling, and prose defects in comments.

    Comments are read beside the code at the code's width, so they carry the
    wider limit rather than the docstring one.
    """

    out: list[Finding] = []

    comments = _comment_lines(
        source,
    )

    continuations = _continuation_lines(
        comments,
    )

    for (
        line,
        text,
        comment,
    ) in comments:
        width = len(
            text.rstrip(),
        )

        if width > COMMENT_COLUMNS:
            out.append(
                _violation(
                    path,
                    line,
                    "widths",
                    f"a comment reaches column {width}, past {COMMENT_COLUMNS}",
                ),
            )

        match = MARKER_LIKE.search(
            string=comment,
        )

        if match is not None:
            word = match.group(
                1,
            )

            if word not in MARKERS and word not in ALIASES:
                out.append(
                    _violation(
                        path,
                        line,
                        "markers",
                        f"`{word}:` is outside the marker vocabulary",
                    ),
                )

            continue

        if line in continuations or not _is_ordinary(
            comment,
        ):
            continue

        out.append(
            _violation(
                path,
                line,
                "markers",
                "an ordinary comment carries no marker",
            ),
        )

    return tuple(
        out,
    )


def _continuation_lines(
    comments: Sequence[tuple[int, str, str]],
    /,
) -> frozenset[int]:
    """
    Return the lines that continue a comment block rather than opening one.

    A marker applies to the whole block it heads, so only the first line of a
    block needs to carry it.
    """

    numbers = frozenset(
        line
        for (
            line,
            *_,
        ) in comments
    )

    return frozenset(line for line in numbers if line - 1 in numbers)


def _is_ordinary(
    text: str,
    /,
) -> bool:
    """
    Return whether a comment is ordinary prose rather than tool syntax.

    A suppression, a shebang, and a directive are read by another program, and
    their syntax is that program's to define.
    """

    body = (
        text.lstrip()
        .lstrip(
            "#",
        )
        .strip()
    )

    if not body:
        return False

    return not body.startswith(
        TOOL_COMMENTS,
    )


def _comment_lines(
    source: str,
    /,
) -> tuple[tuple[int, str, str], ...]:
    """
    Return every comment in the source, with its line number.
    """

    from io import (
        StringIO,
    )

    found: list[tuple[int, str, str]] = []

    try:
        for token in generate_tokens(
            readline=StringIO(
                initial_value=source,
            ).readline,
        ):
            if token.type == COMMENT:
                found.append(
                    (
                        token.start[0],
                        token.line.rstrip(
                            "\n",
                        ),
                        token.string,
                    ),
                )

    except (
        TokenError,
        IndentationError,
        SyntaxError,
    ):
        return tuple(
            found,
        )

    return tuple(
        found,
    )


def _check_prose(
    path: Path,
    tree: AST,
    source: str,
    /,
) -> tuple[Finding, ...]:
    """
    Reports prose defects in the docstrings and comments of a Python file.

    Only prose is read.

    An identifier, a string literal, and an import are not prose merely
    because they sit in a `.py` file.
    """

    out: list[Finding] = []

    passages: list[tuple[int, str]] = [
        (
            line,
            comment,
        )
        for (
            line,
            _,
            comment,
        ) in _comment_lines(
            source,
        )
    ]

    lines = source.splitlines()

    for node in walk(
        node=tree,
    ):
        if not isinstance(
            node,
            FunctionDef | AsyncFunctionDef | ClassDef,
        ):
            continue

        if (
            get_docstring(
                node=node,
            )
            is None
        ):
            continue

        first = node.body[0]

        for index in range(
            first.lineno,
            (first.end_lineno or first.lineno) + 1,
        ):
            passages.append(
                (
                    index,
                    lines[index - 1],
                ),
            )

    for (
        line,
        text,
    ) in passages:
        out.extend(
            _prose_findings(
                path,
                line,
                text,
            ),
        )

    return tuple(
        out,
    )


def _stem_of(
    word: str,
    /,
) -> str:
    """
    Return the `-ise` stem of a word, so an inflected form matches the list.

    `exercised` and `exercising` both reduce to `exercise`.
    """

    for suffix in (
        "ising",
        "isation",
        "ised",
        "ise",
    ):
        if word.endswith(
            suffix,
        ):
            return (
                word[
                    : -len(
                        suffix,
                    )
                ]
                + "ise"
            )

    return word


def _quoted_spans(
    text: str,
    /,
) -> tuple[tuple[int, int], ...]:
    """
    Return the half-open spans of `text` that sit inside quotation marks.
    """

    return tuple(
        (
            match.start(),
            match.end(),
        )
        for match in QUOTED.finditer(
            string=text,
        )
    )


def _prose_findings(
    path: Path,
    line: int,
    text: str,
    /,
) -> tuple[Finding, ...]:
    """
    Reports the prose defects in one line of documentation.
    """

    out: list[Finding] = []

    quoted = _quoted_spans(
        text,
    ) + tuple(
        match.span()
        for match in CODE_SPAN.finditer(
            string=text,
        )
    )

    for match in CONTRACTION.finditer(
        string=text,
    ):
        if any(
            start <= match.start() < end
            for (
                start,
                end,
            ) in quoted
        ):
            continue

        out.append(
            _violation(
                path,
                line,
                "prose",
                f"contraction `{match.group()}`",
            ),
        )

    for match in DOUBLE_HYPHEN.finditer(
        string=text,
    ):
        if any(
            start <= match.start() < end
            for (
                start,
                end,
            ) in quoted
        ):
            continue

        out.append(
            _candidate(
                path,
                line,
                "prose",
                "`--` reads as a typewriter em dash; use `—` unless the two hyphens are syntax",
            ),
        )

    lowered = text.lower()

    for word in sorted(
        BRITISH_WORDS,
    ):
        if compile_pattern(
            pattern=rf"\b{word}\b",
        ).search(
            string=lowered,
        ):
            out.append(
                _candidate(
                    path,
                    line,
                    "prose",
                    f"`{word}` reads as British; confirm the American form",
                ),
            )

    for pattern in BRITISH_PATTERNS:
        for match in pattern.finditer(
            string=lowered,
        ):
            word = match.group()

            if (
                _stem_of(
                    word,
                )
                in NOT_BRITISH_ISE
            ):
                continue

            out.append(
                _candidate(
                    path,
                    line,
                    "prose",
                    f"`{word}` matches a British spelling pattern",
                ),
            )

    return tuple(
        out,
    )


def _check_kwargs(
    path: Path,
    tree: AST,
    source: str,
    /,
) -> tuple[Finding, ...]:
    """
    Reports keyword arguments passed in an order the callee does not declare.
    """

    declared: dict[str, tuple[str, ...]] = {}

    duplicated: set[str] = set()

    for node in walk(
        node=tree,
    ):
        if not isinstance(
            node,
            FunctionDef | AsyncFunctionDef,
        ):
            continue

        arguments = node.args

        order = tuple(
            argument.arg
            for argument in arguments.posonlyargs + arguments.args + arguments.kwonlyargs
            if argument.arg
            not in {
                "self",
                "cls",
            }
        )

        if node.name in declared and declared[node.name] != order:
            duplicated.add(
                node.name,
            )

        declared[node.name] = order

    out: list[Finding] = []

    for node in walk(
        node=tree,
    ):
        if not isinstance(
            node,
            Call,
        ):
            continue

        name = (
            node.func.id
            if isinstance(
                node.func,
                Name,
            )
            else node.func.attr
            if isinstance(
                node.func,
                Attribute,
            )
            else None
        )

        if name is None or name in duplicated or name not in declared:
            continue

        passed = [keyword.arg for keyword in node.keywords if keyword.arg]

        if len(
            passed,
        ) < 2 or not set(
            passed,
        ) <= set(
            declared[name],
        ):
            continue

        expected = [argument for argument in declared[name] if argument in passed]

        if passed != expected:
            out.append(
                _violation(
                    path,
                    node.lineno,
                    "kwargs",
                    f"`{name}` called with {passed}; the signature declares {expected}",
                ),
            )

    return tuple(
        out,
    )


def _check_final(
    path: Path,
    tree: AST,
    source: str,
    /,
) -> tuple[Finding, ...]:
    """
    Reports a module-level name annotated `Final` that the module rebinds.
    """

    annotated: dict[str, int] = {}

    for node in getattr(
        tree,
        "body",
        (),
    ):
        target = getattr(
            node,
            "target",
            None,
        )

        annotation = getattr(
            node,
            "annotation",
            None,
        )

        if (
            not isinstance(
                target,
                Name,
            )
            or annotation is None
        ):
            continue

        rendered = getattr(
            annotation,
            "id",
            None,
        ) or getattr(
            annotation,
            "attr",
            None,
        )

        if rendered == "Final" or isinstance(
            annotation,
            Subscript,
        ):
            root = (
                annotation.value
                if isinstance(
                    annotation,
                    Subscript,
                )
                else annotation
            )

            if (
                getattr(
                    root,
                    "id",
                    None,
                )
                == "Final"
            ):
                annotated[target.id] = node.lineno

    out: list[Finding] = []

    for node in walk(
        node=tree,
    ):
        if not isinstance(
            node,
            FunctionDef | AsyncFunctionDef,
        ):
            continue

        for inner in walk(
            node=node,
        ):
            for name in (
                getattr(
                    inner,
                    "names",
                    [],
                )
                if inner.__class__.__name__ == "Global"
                else []
            ):
                if name in annotated:
                    out.append(
                        _violation(
                            path,
                            annotated[name],
                            "final",
                            f"`{name}` is annotated `Final` and is rebound through `global`",
                        ),
                    )

    return tuple(
        out,
    )


def _check_markdown(
    path: Path,
    source: str,
    /,
) -> tuple[Finding, ...]:
    """
    Reports width, fence, and prose defects in a Markdown file.

    Fenced blocks are read for their language rather than their content, and
    tables and headings are measured but never split.
    """

    out: list[Finding] = []

    lines = source.splitlines()

    language: str | None = None

    opened = 0

    fenced: list[str] = []

    paragraph: list[tuple[int, str]] = []

    for (
        number,
        line,
    ) in enumerate(
        iterable=lines,
        start=1,
    ):
        stripped = line.strip()

        if stripped.startswith(
            "```",
        ):
            out.extend(
                _paragraph_findings(
                    path,
                    paragraph,
                ),
            )

            paragraph = []

            if language is None:
                language = stripped[3:].strip()

                opened = number

                fenced = []

            else:
                out.extend(
                    _fence_findings(
                        path,
                        opened,
                        language,
                        fenced,
                    ),
                )

                language = None

            continue

        if language is not None:
            fenced.append(
                line,
            )

            continue

        out.extend(
            _markdown_line_findings(
                path,
                number,
                line,
            ),
        )

        if not stripped:
            out.extend(
                _paragraph_findings(
                    path,
                    paragraph,
                ),
            )

            paragraph = []

        else:
            paragraph.append(
                (
                    number,
                    line,
                ),
            )

    out.extend(
        _paragraph_findings(
            path,
            paragraph,
        ),
    )

    return tuple(
        out,
    )


def _rendered(
    line: str,
    /,
) -> str:
    """
    Return `line` approximately as a reader meets it.

    Link syntax collapses to its label and emphasis markers disappear, which
    is the difference between the width written and the width read.
    """

    return EMPHASIS.sub(
        repl="",
        string=LINK.sub(
            repl=r"\1",
            string=line,
        ),
    ).rstrip()


def _markdown_line_findings(
    path: Path,
    number: int,
    line: str,
    /,
) -> tuple[Finding, ...]:
    """
    Reports the width and the prose of one Markdown line.
    """

    out: list[Finding] = []

    stripped = line.strip()

    rendered = _rendered(
        line,
    )

    width = len(
        rendered,
    )

    # NOTE:
    # A table is exempt by the width rule, and a line with no break opportunity below the limit is the standard's
    # long-identifier case: reporting it would ask for a wrap the language of the line cannot take.
    breakable = " " in rendered[:PROSE_COLUMNS].strip()

    if (
        width > PROSE_COLUMNS
        and breakable
        and not stripped.startswith(
            "|",
        )
    ):
        out.append(
            _violation(
                path,
                number,
                "widths",
                f"a Markdown line reaches column {width}, past {PROSE_COLUMNS}",
            ),
        )

    out.extend(
        _prose_findings(
            path,
            number,
            line,
        ),
    )

    return tuple(
        out,
    )


def _fence_findings(
    path: Path,
    number: int,
    language: str,
    body: Sequence[str],
    /,
) -> tuple[Finding, ...]:
    """
    Reports a fence whose tag does not say what the fence holds.
    """

    out: list[Finding] = []

    if not language:
        # NOTE:
        # An untagged fence is only reported when its content is Python, which is the one tag the standard makes a
        # MUST.
        #
        # Guessing at any other language would invent a rule the standard does not state.
        try:
            parse_source(
                source="\n".join(
                    body,
                ),
            )

        except SyntaxError:
            return ()

        out.append(
            _violation(
                path,
                number,
                "fences",
                "an untagged fence holds Python — tag it `python`",
            ),
        )

    if language == "bash":
        out.append(
            _candidate(
                path,
                number,
                "fences",
                "a `bash` fence — `sh` unless the example needs Bash",
            ),
        )

    return tuple(
        out,
    )


def _paragraph_findings(
    path: Path,
    paragraph: Sequence[tuple[int, str]],
    /,
) -> tuple[Finding, ...]:
    """
    Reports a prose paragraph carrying more than one sentence.

    A candidate rather than a violation: an abbreviation and a decimal point
    both end a sentence as far as any splitter can tell.
    """

    if not paragraph:
        return ()

    (
        number,
        first,
    ) = paragraph[0]

    opening = first.lstrip()

    if opening.startswith(
        MARKDOWN_STRUCTURE,
    ) or ORDERED_ITEM.match(
        string=opening,
    ):
        return ()

    text = " ".join(
        line.strip()
        for (
            _,
            line,
        ) in paragraph
    )

    if text.endswith(
        ":",
    ):
        return ()

    # NOTE:
    # An inline code span is masked before the sentences are counted, for the reason §7 gives: the prose rules do not
    # reach code.
    #
    # `count() ... FINAL` and `system.tables.total_rows` each end a sentence as far as a splitter can tell, and a
    # paragraph naming two of them reads as three sentences while being one.
    #
    # The span becomes a single underscore rather than nothing, so that the words on either side of it stay separate
    # words.
    ends = SENTENCE_END.findall(
        string=CODE_SPAN.sub(
            repl="_",
            string=text,
        ),
    )

    if (
        len(
            ends,
        )
        < 2
    ):
        return ()

    return (
        _candidate(
            path,
            number,
            "paragraphs",
            f"a paragraph of {
                len(
                    ends,
                )
            } sentences — one sentence, one paragraph",
        ),
    )


# NOTE:
# Ordered as the standard orders its sections, so a reader following one finds the other.
CHECKS: Final = MappingProxyType(
    mapping={
        "imports": _check_imports,
        "signatures": _check_signatures,
        "naming": _check_naming,
        "calls": _check_calls,
        "blank-lines": _check_blank_lines,
        "docstrings": _check_docstrings,
        "comments": _check_comments,
        "prose": _check_prose,
        "kwargs": _check_kwargs,
        "final": _check_final,
    },
)

# NOTE:
# Markdown is checked on its own terms, so it gets its own table rather than a branch inside a Python check.
#
# The signature differs for the same reason: there is no syntax tree to pass.
MARKDOWN_CHECKS: Final = MappingProxyType(
    mapping={
        "markdown": _check_markdown,
    },
)

ALL_CHECKS: Final = frozenset(
    {
        *CHECKS,
        *MARKDOWN_CHECKS,
    },
)

# NOTE:
# The two checks that read this file's own rule data as if it were prose.
#
# Every other check runs on this file normally: a checker that exempts itself from the syntax it polices hides exactly
# the defects it exists to find.
SELF_EXEMPT: Final = frozenset(
    {
        "comments",
        "prose",
    },
)

# NOTE:
# One shared empty table for every path on which no configuration is found.
#
# A fresh mapping per failure path would suggest the caller may write to it, which is the opposite of the contract.
EMPTY_CONFIGURATION: Final = MappingProxyType(
    mapping={},
)


def _read_configuration(
    start: Path,
    /,
) -> MappingProxyType[str, object]:
    """
    Return the `[tool.check-conventions]` table from the nearest manifest.

    A malformed manifest yields the defaults rather than a crash, because a
    gate that dies on an unrelated typo is worse than one that runs with the
    defaults.
    """

    for directory in (
        start.resolve(),
        *start.resolve().parents,
    ):
        manifest = directory / "pyproject.toml"

        if not manifest.is_file():
            continue

        try:
            table = loads(
                manifest.read_text(
                    encoding="utf-8",
                ),
            )

        except TOMLDecodeError:
            return EMPTY_CONFIGURATION

        tools = table.get(
            "tool",
        )

        if not isinstance(
            tools,
            dict,
        ):
            return EMPTY_CONFIGURATION

        configured = tools.get(
            "check-conventions",
        )

        return (
            MappingProxyType(
                mapping=configured,
            )
            if isinstance(
                configured,
                dict,
            )
            else EMPTY_CONFIGURATION
        )

    return EMPTY_CONFIGURATION


def _string_list(
    configuration: Mapping[str, object],
    key: str,
    /,
) -> tuple[str, ...]:
    """
    Return `key` as a tuple of strings, ignoring a value of the wrong shape.
    """

    value = configuration.get(
        key,
    )

    if not isinstance(
        value,
        list,
    ):
        return ()

    return tuple(
        item
        for item in value
        if isinstance(
            item,
            str,
        )
    )


def _source_files(
    directory: Path,
    /,
) -> tuple[Path, ...]:
    """
    Return the files under `directory` this program reads, skipping generated
    trees.
    """

    return tuple(
        sorted(
            found
            for suffix in SUFFIXES
            for found in directory.rglob(
                pattern=f"*{suffix}",
            )
            if not SKIPPED_DIRECTORIES
            & set(
                found.parts,
            )
        ),
    )


def _relative(
    path: Path,
    /,
) -> str:
    """
    Return `path` relative to the project root, as a POSIX string.
    """

    try:
        return (
            path.resolve()
            .relative_to(
                PROJECT_ROOT.resolve(),
            )
            .as_posix()
        )

    except ValueError:
        return path.as_posix()


def _run(
    paths: Sequence[Path],
    enabled: AbstractSet[str],
    /,
) -> tuple[Finding, ...]:
    """
    Run the enabled checks over every path and return what they found.
    """

    out: list[Finding] = []

    myself = Path(
        __file__,
    ).resolve()

    for path in sorted(
        paths,
    ):
        applicable = enabled - SELF_EXEMPT if path.resolve() == myself else enabled

        if any(
            fnmatch(
                name=_relative(
                    path,
                ),
                pat=pattern,
            )
            for pattern in EXCLUDED
        ):
            continue

        try:
            source = path.read_text(
                encoding="utf-8",
            )

        except (
            UnicodeDecodeError,
            OSError,
        ) as error:
            failure = type(
                error,
            ).__name__

            out.append(
                _violation(
                    path,
                    0,
                    "unreadable",
                    f"{failure}: {error}",
                ),
            )

            continue

        if path.suffix == MARKDOWN_SUFFIX:
            for (
                name,
                markdown_check,
            ) in MARKDOWN_CHECKS.items():
                if name in applicable:
                    out.extend(
                        markdown_check(
                            path,
                            source,
                        ),
                    )

            continue

        try:
            tree = parse_source(
                source=source,
            )

        except SyntaxError as error:
            out.append(
                _violation(
                    path,
                    error.lineno or 0,
                    "parse",
                    str(
                        object=error,
                    ),
                ),
            )

            continue

        for (
            name,
            check,
        ) in CHECKS.items():
            if name in applicable:
                out.extend(
                    check(
                        path,
                        tree,
                        source,
                    ),
                )

    return tuple(
        out,
    )


# NOTE:
# Each control is a snippet known to break the check it names, keyed by the construct it exercises.
#
# One control per check would prove only that the check can fire at all.
#
# A check that covers several constructs gets one control per construct, because a rule can silently stop reaching a
# construct the codebase happens not to contain.
#
# `_self_test` reads the check name out of each entry and reports any check in `CHECKS` that no control exercises, so
# a check added without one is visible rather than silently untested.
CONTROLS: Final = MappingProxyType(
    mapping={
        "imports/module": (
            "imports",
            "import os\n",
        ),
        "signatures/public": (
            "signatures",
            "def render(template, context):\n    return template\n",
        ),
        "naming/public-positional": (
            "naming",
            "def render(template, /):\n    return template\n",
        ),
        "calls/one-line": (
            "calls",
            "x = len([1])\n",
        ),
        "calls/destructuring-target": (
            "calls",
            "for index, character in pairs:\n    pass\n",
        ),
        "calls/inside-f-string": (
            "calls",
            """message = f"{len(lines)}"\n""",
        ),
        "blank-lines/statements": (
            "blank-lines",
            "def f():\n    a = 1\n    b = 2\n    return a + b\n",
        ),
        "docstrings/shape": (
            "docstrings",
            '''def f():\n    """One line."""\n\n    return 1\n''',
        ),
        "docstrings/width": (
            "docstrings",
            f'''def f():\n    """\n    {"w" * PROSE_COLUMNS}\n    """\n\n    return 1\n''',
        ),
        "comments/marker": (
            "comments",
            "# FIXIT2: not in the vocabulary\n",
        ),
        "comments/width": (
            "comments",
            f"# NOTE: {'w' * COMMENT_COLUMNS}\n",
        ),
        "prose/contraction": (
            "prose",
            '''def f():\n    """\n    It doesn't fit.\n    """\n\n    return 1\n''',
        ),
        "prose/double-hyphen": (
            "prose",
            '''def f():\n    """\n    One clause -- and the next.\n    """\n\n    return 1\n''',
        ),
        "kwargs/order": (
            "kwargs",
            "def f(*, a, b):\n    return a\n\n\nf(b=2, a=1)\n",
        ),
        "final/rebound": (
            "final",
            "from typing import Final\n\nX: Final = 1\n\n\ndef f():\n    global X\n\n    X = 2\n",
        ),
        "markdown/width": (
            "markdown",
            f"# Title\n\n{'word ' * 20}\n",
        ),
        "markdown/untagged-python": (
            "markdown",
            "# Title\n\n```\nx = len(\n    lines,\n)\n```\n",
        ),
        "markdown/bash-fence": (
            "markdown",
            "# Title\n\n```bash\necho hello\n```\n",
        ),
        "markdown/contraction": (
            "markdown",
            "# Title\n\nIt doesn't fit.\n",
        ),
        "markdown/paragraph": (
            "markdown",
            "# Title\n\nOne claim here. A second claim here.\n",
        ),
    },
)


def _self_test() -> int:
    """
    Prove every check can fail, then prove the exemptions work.

    The controls run against the defaults rather than the host project's
    configuration.

    A project that exempts a module the control snippet uses would otherwise
    switch the control off, and the run would report a failure that is really
    a configuration effect.
    """

    from tempfile import (
        NamedTemporaryFile,
    )

    global EXCLUDED, NAMESPACE_MODULES, PROJECT_ROOT

    saved = (
        EXCLUDED,
        NAMESPACE_MODULES,
        PROJECT_ROOT,
    )

    (
        EXCLUDED,
        NAMESPACE_MODULES,
        PROJECT_ROOT,
    ) = (
        (),
        DEFAULT_NAMESPACE_MODULES,
        Path(),
    )

    failures = 0

    exercised = frozenset(
        check
        for (
            check,
            _,
        ) in CONTROLS.values()
    )

    for name in sorted(
        ALL_CHECKS,
    ):
        if name in exercised:
            continue

        print(
            f"  FAIL  {name}: no control snippet",
        )

        failures += 1

    for (
        label,
        (
            name,
            snippet,
        ),
    ) in CONTROLS.items():
        suffix = MARKDOWN_SUFFIX if name in MARKDOWN_CHECKS else PYTHON_SUFFIX

        with NamedTemporaryFile(
            mode="w",
            suffix=suffix,
            delete=False,
        ) as handle:
            handle.write(
                snippet,
            )

            probe = Path(
                handle.name,
            )

        # NOTE:
        # One check runs, so any finding came from it.
        #
        # A check may label its findings by rule rather than by check name — `comments` reports both `markers` and
        # `widths` — so matching on the label would test the label.
        found = tuple(
            item
            for item in _run(
                (probe,),
                frozenset(
                    {
                        name,
                    },
                ),
            )
            if item.check
            not in {
                "parse",
                "unreadable",
            }
        )

        probe.unlink()

        if found:
            print(
                f"  ok    {label}: control reported",
            )

        else:
            print(
                f"  FAIL  {label}: control NOT reported",
            )

            failures += 1

    failures += _exemption_controls()

    (
        EXCLUDED,
        NAMESPACE_MODULES,
        PROJECT_ROOT,
    ) = saved

    return failures


def _exemption_controls() -> int:
    """
    Prove that the exemptions work and are absent without configuration.
    """

    from tempfile import (
        TemporaryDirectory,
    )

    global EXCLUDED, NAMESPACE_MODULES, PROJECT_ROOT

    failures = 0

    with TemporaryDirectory() as directory:
        probe = (
            Path(
                directory,
            )
            / "probe.py"
        )

        probe.write_text(
            data="import socket\n",
            encoding="utf-8",
        )

        reported = bool(
            _run(
                (probe,),
                frozenset(
                    {
                        "imports",
                    },
                ),
            ),
        )

        NAMESPACE_MODULES = DEFAULT_NAMESPACE_MODULES | frozenset(
            {
                "socket",
            },
        )

        exempted = bool(
            _run(
                (probe,),
                frozenset(
                    {
                        "imports",
                    },
                ),
            ),
        )

        NAMESPACE_MODULES = DEFAULT_NAMESPACE_MODULES

        PROJECT_ROOT = Path(
            directory,
        )

        EXCLUDED = ("probe.py",)

        excluded = bool(
            _run(
                (probe,),
                frozenset(
                    {
                        "imports",
                    },
                ),
            ),
        )

        EXCLUDED = ()

        PROJECT_ROOT = Path()

        if reported and not exempted and not excluded:
            print(
                "  ok    exemptions: module and path exclusions honored",
            )

        else:
            print(
                f"  FAIL  exemptions: default={reported}, module={exempted}, path={excluded}",
            )

            failures += 1

        widths = (
            Path(
                directory,
            )
            / "widths.py"
        )

        # NOTE:
        # One file, one column, two verdicts.
        #
        # The two width limits are the convention most likely to be quietly collapsed into one, and a scan reporting
        # nothing looks the same whether the limits are separate or whether the wider one swallowed the narrower.
        #
        # This probe sits between them: a docstring line here is over its limit and a comment of the same width is
        # under its own, so the run must report exactly one of the two.
        filler = "w" * (PROSE_COLUMNS + 20)

        quotes = '"""'

        widths.write_text(
            data=f"{quotes}\n{filler}\n{quotes}\n\n# NOTE: {filler[8:]}\n",
            encoding="utf-8",
        )

        measured = _run(
            (widths,),
            frozenset(
                {
                    "comments",
                    "docstrings",
                },
            ),
        )

        docstring_reported = any(item.line == 2 for item in measured)

        comment_reported = any(item.line == 5 for item in measured)

        if docstring_reported and not comment_reported:
            print(
                "  ok    widths: the docstring limit and the comment limit are separate",
            )

        else:
            print(
                f"  FAIL  widths: docstring={docstring_reported}, comment={comment_reported}",
            )

            failures += 1

        quoting = (
            Path(
                directory,
            )
            / "quoting.md"
        )

        # NOTE:
        # One file, two contractions, one verdict.
        #
        # §7 does not reach quoted speech, so a rule that reported both would be proving something the standard does
        # not say, and a rule that reported neither would have stopped working.
        quoting.write_text(
            data="# Title\n\nIt does not fit, and \"it doesn't\" is the quotation.\n\nIt doesn't fit.\n",
            encoding="utf-8",
        )

        quoted = _run(
            (quoting,),
            frozenset(
                {
                    "markdown",
                },
            ),
        )

        inside = any(item.line == 3 for item in quoted)

        outside = any(item.line == 5 for item in quoted)

        if outside and not inside:
            print(
                "  ok    quoting: a contraction inside quotation marks is left alone",
            )

        else:
            print(
                f"  FAIL  quoting: inside={inside}, outside={outside}",
            )

            failures += 1

        typing = (
            Path(
                directory,
            )
            / "typing.py"
        )

        # NOTE:
        # One file, a list in each of two positions, one verdict.
        #
        # `Callable[[str], None]` is type syntax that happens to be spelled with a list, and §12.5 exempts a type
        # subscript; `len([1])` is a container literal in an argument. A rule that reported both would explode every
        # callback annotation in a codebase, and one that reported neither would have stopped working.
        typing.write_text(
            data="from collections.abc import Callable\n\nx: Callable[[str], None] = f\n\ny = len([1])\n",
            encoding="utf-8",
        )

        annotated = _run(
            (typing,),
            frozenset(
                {
                    "calls",
                },
            ),
        )

        subscript_reported = any(item.line == 3 for item in annotated)

        literal_reported = any(item.line == 5 for item in annotated)

        if literal_reported and not subscript_reported:
            print(
                "  ok    subscripts: a list inside a type subscript is not a container literal",
            )

        else:
            print(
                f"  FAIL  subscripts: subscript={subscript_reported}, literal={literal_reported}",
            )

            failures += 1

        hooks = (
            Path(
                directory,
            )
            / "hooks.py"
        )

        # NOTE:
        # One file, two underscored names, one verdict.
        #
        # `_generate_next_value_` is the language's, declared positional-or-keyword in typeshed, and writing `/` on it
        # is an override a type checker rejects; `_normalize` is the project's and must declare its boundary.
        hooks.write_text(
            data=(
                "class E:\n    def _generate_next_value_(name, start, count, last):\n        return name\n"
                "\n\ndef _normalize(text, locale):\n    return text\n"
            ),
            encoding="utf-8",
        )

        underscored = _run(
            (hooks,),
            frozenset(
                {
                    "signatures",
                },
            ),
        )

        hook_reported = any(item.line == 2 for item in underscored)

        helper_reported = any(item.line == 6 for item in underscored)

        if helper_reported and not hook_reported:
            print(
                "  ok    hooks: a name the language owns is not the project's to mark",
            )

        else:
            print(
                f"  FAIL  hooks: hook={hook_reported}, helper={helper_reported}",
            )

            failures += 1

        counting = (
            Path(
                directory,
            )
            / "counting.md"
        )

        # NOTE:
        # One file, two paragraphs, one verdict.
        #
        # The first names two dotted identifiers and is one sentence; a splitter that reads their periods counts
        # three.
        #
        # The second is genuinely two sentences.
        counting.write_text(
            data=(
                "# Title\n"
                "\n"
                "The number comes from `count() ... FINAL` rather than `system.tables.total_rows`.\n"
                "\n"
                "It is one number. It is read twice.\n"
            ),
            encoding="utf-8",
        )

        counted = _run(
            (counting,),
            frozenset(
                {
                    "markdown",
                },
            ),
        )

        code_counted = any(item.line == 3 and item.check == "paragraphs" for item in counted)

        prose_counted = any(item.line == 5 and item.check == "paragraphs" for item in counted)

        if prose_counted and not code_counted:
            print(
                "  ok    sentences: a period inside a code span does not end a sentence",
            )

        else:
            print(
                f"  FAIL  sentences: code={code_counted}, prose={prose_counted}",
            )

            failures += 1

        spans = (
            Path(
                directory,
            )
            / "spans.md"
        )

        # NOTE:
        # One file, the same two hyphens in both positions, one verdict.
        #
        # §7 does not reach code, and a span between backticks is code — which is exactly how a document that
        # documents the rule has to write the sequence the rule looks for.
        #
        # A rule that reported both would make the standard unable to state itself; one that reported neither would
        # have stopped working.
        spans.write_text(
            data="# Title\n\nA rule that looks for ` -- ` reports prose.\n\nOne clause -- and the next.\n",
            encoding="utf-8",
        )

        spanned = _run(
            (spans,),
            frozenset(
                {
                    "markdown",
                },
            ),
        )

        in_code = any(item.line == 3 for item in spanned)

        in_prose = any(item.line == 5 for item in spanned)

        if in_prose and not in_code:
            print(
                "  ok    code spans: a prose rule stops at the backtick",
            )

        else:
            print(
                f"  FAIL  code spans: in_code={in_code}, in_prose={in_prose}",
            )

            failures += 1

        surface = (
            Path(
                directory,
            )
            / "surface.py"
        )

        # NOTE:
        # One file, the same name and the same marker, two verdicts.
        #
        # `submit` is module surface reached by name, so a public name over a positional-only signature is the
        # disagreement §13 describes.
        #
        # The `submit` nested inside it is reached only through the reference the enclosing function hands to the
        # executor, and positional is the convention that reference imposes.
        #
        # A rule that reported both would flag every callback in a codebase and train a reader to ignore it; one that
        # reported neither would have stopped detecting the case it exists for.
        surface.write_text(
            data=("def submit(task, /):\n    def submit(item, /):\n        return item\n\n    return submit(task)\n"),
            encoding="utf-8",
        )

        surfaces = _run(
            (surface,),
            frozenset(
                {
                    "naming",
                },
            ),
        )

        module_level_reported = any(item.line == 1 for item in surfaces)

        nested_reported = any(item.line == 2 for item in surfaces)

        if module_level_reported and not nested_reported:
            print(
                "  ok    surface: a callable defined inside another is not the module's surface",
            )

        else:
            print(
                f"  FAIL  surface: module_level={module_level_reported}, nested={nested_reported}",
            )

            failures += 1

        binary = (
            Path(
                directory,
            )
            / "binary.py"
        )

        binary.write_bytes(
            data=b"\xa4\xa4\xa4\n",
        )

        unreadable = tuple(
            item
            for item in _run(
                (binary,),
                frozenset(
                    CHECKS,
                ),
            )
            if item.check == "unreadable"
        )

        if unreadable:
            print(
                "  ok    unreadable: reported rather than crashing",
            )

        else:
            print(
                "  FAIL  unreadable: a file that cannot be decoded was not reported",
            )

            failures += 1

    return failures


def main() -> int:
    """
    Parse the arguments, run the checks, and report what they found.
    """

    parser = ArgumentParser(
        description="Check the engineering conventions a formatter cannot express.",
    )

    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
    )

    parser.add_argument(
        "--only",
        action="append",
        choices=sorted(
            ALL_CHECKS,
        ),
    )

    parser.add_argument(
        "--project",
        default=None,
        type=Path,
        help="audit DIR from outside it",
        metavar="DIR",
    )

    parser.add_argument(
        "--self-test",
        action="store_true",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero on candidates as well as violations",
    )

    parser.add_argument(
        "--version",
        action="store_true",
    )

    arguments = parser.parse_args()

    if arguments.version:
        print(
            STANDARD_VERSION,
        )

        return 0

    global EXCLUDED, NAMESPACE_MODULES, PROJECT_ROOT

    root = (arguments.project or Path.cwd()).resolve()

    if not root.is_dir():
        parser.error(
            message=f"--project {root} is not a directory",
        )

    configuration = _read_configuration(
        root,
    )

    NAMESPACE_MODULES = DEFAULT_NAMESPACE_MODULES | frozenset(
        _string_list(
            configuration,
            "namespace-modules",
        ),
    )

    EXCLUDED = _string_list(
        configuration,
        "exclude",
    )

    PROJECT_ROOT = root

    if arguments.self_test:
        return 1 if _self_test() else 0

    if not arguments.paths:
        parser.error(
            message="give at least one path, or --self-test",
        )

    targets = tuple(path if path.is_absolute() else root / path for path in arguments.paths)

    files = tuple(
        found
        for path in targets
        for found in (
            (path,)
            if path.is_file()
            else _source_files(
                path,
            )
        )
    )

    findings = _run(
        files,
        frozenset(
            arguments.only or ALL_CHECKS,
        ),
    )

    violations = [item for item in findings if item.kind == VIOLATION]

    candidates = [item for item in findings if item.kind == CANDIDATE]

    for item in violations + candidates:
        print(
            item.render(
                root=root,
            ),
        )

    print(
        f"\nengineering conventions v{STANDARD_VERSION}: "
        f"{
            len(
                violations,
            )
        } violation(s), {
            len(
                candidates,
            )
        } candidate(s) across {
            len(
                files,
            )
        } file(s) in {root}",
        file=stderr,
    )

    if candidates:
        print(
            "candidates are suspects for review, not proof of a defect or of compliance",
            file=stderr,
        )

    if violations:
        return 1

    return 1 if candidates and arguments.strict else 0


if __name__ == "__main__":
    raise SystemExit(
        main(),
    )
