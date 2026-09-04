# Engineering conventions

A portable standard for Python projects.

It is written to be read once by a person and applied repeatedly by a person
or a tool, so every rule is stated as a rule and every rule says how far a
machine can check it.

## How to read this document

**MUST** and **MUST NOT** are rules.

Departing from one is a defect unless an exception is recorded at the site, in
the form §1 describes.

**SHOULD** and **SHOULD NOT** are defaults.

Departure needs a reason, not a record.

**Judgment** marks a question with no mechanical answer, where the document says
what to weigh and a person decides.

### Enforcement classes

Every rule carries one of four, and the checker's output preserves the
distinction:

| Class | Meaning |
| --- | --- |
| **Proved** | A tool decides it, and a clean result is evidence. |
| **Approximated** | A tool decides it under a stated simplification. |
| **Candidate** | A tool reports suspects and a person decides. |
| **Review** | No tool. |

A checker that reports a **Candidate** finding as a violation is claiming a
guarantee it does not have, and that is worse than not checking.

## How this document is ordered

Sections follow the order in which the conventions bind as a change is made.

The project is configured once, then every word written is prose, then a
source file is read from its comments and imports down through its
declarations to its call sites, then the change is tested, then it is
committed.

Section 2 comes before the code rules because it governs when a rule is
allowed to exist at all.

---

## 1. Authority and precedence

Four sources govern, strongest first.

A lower source may narrow a higher one and may never contradict it.

1. **External published conventions.**
   Conventional Commits, and the `todo-comments` marker vocabulary.
   These are public and shared with people who have never read this document.
2. **This document.**
   It narrows those to a smaller, stricter subset and adds the language-level
   rules they do not cover.
3. **Project-local decisions.**
   A project may specialize a rule for a reason particular to it.
4. **Framework, library, and language semantics.**
   These are not a source of style; they are facts.
   Where a rule and a fact disagree, the fact wins and the rule was
   misapplied.

**MUST.**

Narrowing is allowed and contradiction is not.

Using three of the seven comment markers narrows the vocabulary.

Inventing an eighth contradicts it.

**MUST.**

A project-local exception is recorded at the point of exception.

A deviation that exists only in the code cannot be told apart from a mistake,
and the next conformance pass will "fix" it.

**MUST.**

Report a genuine conflict between sources rather than resolving it silently.

A silent resolution becomes precedent nobody agreed to.

### Normative and demonstrative material

**MUST.**

Every rule binds normative material: shipped code, tests, configuration,
documentation, and commit messages.

**MUST NOT.**

A rule does not bind material whose purpose is to demonstrate the rule being
broken.

A standard, a teaching example, or a checker's own fixture may contain code
that violates a rule deliberately, and correcting it destroys the example.

**MUST.**

Mark demonstrative material so that neither a person nor a tool mistakes it
for an oversight, by one of two mechanisms in order of preference:

1. Keep it out of the scanned tree, inside a fenced block in prose, where no
   checker reads it.
2. Where it must be a real file, put it in a directory the project's
   configuration excludes, and state in that directory what it is for and
   which rule each file breaks.

---

## 2. An observation is not a requirement

**MUST.**

Do not encode an observation as application semantics without first
establishing that the observation is a requirement.

This is the most expensive mistake in the document, because the code it
produces looks correct, passes its tests, and fails silently on data nobody
has seen yet.

### How the mistake happens

Something in the data looks wrong.

The value is examined, a pattern is noticed, and a rule is written to exclude
the pattern.

The rule is then correct on every input anyone has looked at, which is the
problem: it was derived from the sample, so the sample cannot test it.

### The three questions

Answer all three before a rule enters the code.

1. **Is this a requirement, or a property?**
   Did somebody specify it, or did it turn out to be true of the data at hand?
2. **Would the rule still be correct on data nobody has seen?**
   Name an input it would classify wrongly.
3. **What would falsify it?**
   A rule with no falsifying case is a description of the sample.

If the answer to the first is "property" and to the third is "nothing,"
report the observation and do not implement it.

### The inverse is the same error

**MUST NOT.**

Do not treat a counterexample as a rule in the other direction.

Finding that a proposed filter would delete legitimate data defeats the
filter.

It does not establish a requirement that such data be kept under all future
conditions.

### Where the pressure comes from

Almost always a failing check, where the cheapest path to green is a special
case that makes exactly this input pass.

**MUST.**

A change made to turn a check green is a change to the system's meaning and
needs the same justification as any other.

**SHOULD.**

Stop and put the decision to whoever owns it when a failure cannot be resolved
without deciding what the system is supposed to do.

---

## 3. Project configuration

**MUST.**

Every configuration file has one ordering principle, and the principle is
legible from the file itself.

*(Review.)*

**MUST NOT.**

Do not default to alphabetical order.

Alphabetical is the right answer only for a list whose members have no
relationship to each other, such as a finite vocabulary or a lookup table.

The usual principles are identity before dependencies before gates, pipeline
order where the project already states one, and lifecycle order for a service
definition.

**MUST.**

Two files describing the same sequence agree on that sequence.

**MUST.**

Sibling entries in one file share one key order, so a reader can compare them
by position.

**MUST NOT.**

Do not reorder for cosmetic reasons.

Reorder when the existing order is arbitrary, self-contradictory, or
materially harder to follow than an available alternative.

**MUST.**

One documented command runs the project's authoritative verification gate, and
the project's documentation names it.

The convention is that the command exists and is the same one a person and a
pipeline run.

It is not that the command is any particular task runner.

**MUST NOT.**

Do not change tool configuration to make your own changes pass.

A genuine conflict between an intended change and the configured tooling is a
stop-and-report situation.

**This standard sets no directory layout.**

Whether packages sit under `src/`, at the repository root, or in a workspace is
architecture, and a project adopting this standard does not inherit the
layout of the repository the standard came from.

---

## 4. Ordering

**Order carries meaning, and equivalent permutations are not interchangeable.**

Three kinds of order exist, and treating one as another is the mistake this
section prevents.

**Semantic order.**

Changing it changes behavior or breaks a contract: keyword arguments against
the callee's signature, a pipeline's stages, a migration sequence, YAML
sequences a consumer reads positionally.

**MUST** preserve it.

**Conventional order.**

Changing it changes nothing at runtime and everything for a reader and a diff:
imports, class fields, configuration sections, documentation sections, a
project's own list of rule families.

**MUST** preserve an established one, and **MUST NOT** impose a new one merely
because another arrangement looks tidier.

**No canonical order.**

Some structures genuinely have none.

**SHOULD** give those a deterministic order anyway, normally alphabetical, so that
additions land in one predictable place and two people adding entries do not
produce a conflict.

A finite vocabulary or a lookup table is the usual case.

### Ordering is not only a Python concern

It reaches configuration, documentation, and data.

**SHOULD** write a structure vertically, one element per line, wherever the
syntax permits and the file's own conventions allow: a TOML array, a YAML
sequence, a list in a manifest.

The reason is the same as in Python.

One element per line makes an addition a one-line diff and a removal a
one-line diff, and it makes an out-of-order entry visible.

**This does not make those files Python**, and it does not import the Python rules
into them.

It is the same readability technique, applied where the syntax offers it.

**MUST configure the formatter that owns the file to keep the vertical form.**

A TOML formatter collapses a multi-line array back onto one line by default,
so the exploded list does not survive one save and the convention is undone by
the tool rather than by a person.

`vendor/taplo/taplo.toml` is that setting, written down.

*(Review.*

No tool decides whether an order is meaningful.*)*

---

## 5. Language and runtime

**MUST.**

Require the lowest language version the project's own constructs need, worked
out from the code rather than from the installed interpreter.

Each of these sets a floor, and there are others:

| Construct | Floor |
| --- | --- |
| `datetime.UTC`, `StrEnum`, `tomllib` | 3.11 |
| `type X = ...`, `@override`, `itertools.batched` | 3.12 |
| a newline inside an f-string replacement field | 3.12 |
| unquoted forward references in annotations | 3.14 |

**MUST.**

Keep the linter's target version in agreement with the manifest.

**SHOULD** let the linter derive it rather than writing it twice.

Ruff reads `project.requires-python`, so leaving `target-version` unset makes the
agreement structural instead of something a reader has to check.

**MUST NOT.**

Do not add `from __future__ import annotations` to work around an older mental
model of annotations.

On a runtime that evaluates annotations lazily, an unquoted forward reference
already works, and the import is a floor the project does not need.

**SHOULD.**

Raise the floor for a stated reason, such as a dependency, a runtime, or a
security window.

---

## 6. Dependencies

**Judgment.**

This standard takes no position on when a project pins.

Pinning trades reproducibility against the cost of staying current, and where
that trade falls depends on the stage the project is in.

**SHOULD.**

Decide it deliberately and write it down, so that an unpinned dependency is a
position rather than an oversight.

**MUST NOT.**

Do not turn a single failing check into a dependency policy.

A test that breaks on an upstream change is evidence about that change, not
evidence that the project needs reproducibility.

**MUST.**

Verify a manifest before reporting a dependency as missing.

A tool needed only to run the gate belongs in a development dependency group
rather than in the runtime dependencies, and its absence from the runtime list
is the correct state rather than an omission.

---

## 7. Prose

Prose is prose wherever it appears.

The same rules govern Markdown, docstrings, comments, commit messages, and
release notes.

A docstring is not held to a looser standard because it lives in a `.py` file.

**MUST** use American English.

*(Candidate.)*

`color`, `analyze`, `behavior`, `catalog`, `canceled`, `license`, `toward`, `normalize`.

**MUST NOT** use contractions.

Write `do not`, `cannot`, `it is`, `there is`.

Possessives are not contractions: `the reader's attention` is correct.

**MUST NOT** punctuate prose with two hyphens.

*(Candidate.)*

A typewriter had no em dash and `--` is what a typist wrote instead; a Unicode
file has one, so write `—`.

The rule is about prose and reaches nothing else.

`--fix` is a flag, `var(--border)` is a CSS property, `-- comment` is SQL, and
`A --> B` is a diagram edge.

**Detection is the space on both sides**, which no syntax that spells itself with
two hyphens has, so a rule that looks for ` -- ` reports prose and only prose.

**MUST** hold to one sentence per paragraph.

*(Approximated.)*

End the sentence, leave a blank line, start the next.

A long paragraph hides the seam where one claim ends and the next begins, and
a one-sentence paragraph makes an unsupported claim obvious.

### What the rules do not reach

- **Quoted speech, text, and data.**
  A quotation is reproduced exactly, contraction included, because expanding
  it misquotes the speaker.
- **Proper names and titles**, including a British spelling inside a name.
- **Test data and fixtures.**
  A string a test asserts is returned byte-identical is data.
- **Identifiers bound by an external API**, which keep the library's spelling.
- **Structured material.**
  A commit subject, a heading, a table cell, a list item, a colon-introduced
  enumeration, and a conventional formula such as a copyright line may each
  hold more than one sentence, because splitting them would move a sentence
  out of the structure holding it.
- **Code.**
  Source is not made of paragraphs, and a control-flow header, a
  signature, and a call are governed by the rules for code.

**A paragraph opening with a bold label is still a paragraph.**

The label names the rule; the sentences after it are prose and are split.

### Pronouns

Prefer the second person or a plural subject.

Where a singular third-person pronoun is unavoidable and the referent's
pronouns are unknown, use `they`.

**MUST NOT.**

Do not change a pronoun by substitution.

Pronoun number carries verb agreement, so `they do not own` becomes
`he does not own` rather than `he do not own`, and a blanket replacement also
catches pronouns whose antecedent is a document or a collection.

---

## 8. Widths

Four artifacts, two limits, and one boundary rule.

| Artifact | Limit | Last symbol at column |
| --- | --- | --- |
| Markdown prose | 79 | 78 or lower |
| Python docstrings | 79 | 78 or lower |
| Python comments | 119 | 118 or lower |
| Python code | 119 | 118 or lower |

**MUST.**

A meaningful symbol must not occupy column 79 or later in Markdown prose or in
a docstring, and must not occupy column 119 or later in a comment or in code.

**Trailing whitespace is not a meaningful symbol** for this calculation, and it
should be removed anyway.

Measuring raw line length lets a trailing space hide a symbol that has crossed
the boundary.

**MUST NOT.**

Do not collapse these into one width.

Docstrings are prose that a reader meets in a rendered tooltip; comments are
read in the source beside the code they explain, at the code's own width.

A project that holds comments to the docstring limit spends three lines on
what belongs on one.

**Code and comments share the wider limit** because they are read together, in
the source, at the same indentation.

The prose limits do not become the code limit, and the code limit does not
become the prose limit.

### Markdown is measured as rendered

A link is judged by its label: `[the adoption guide](docs/adoption.md)` renders
as four words, and four words is what counts.

Tables, diagrams, fenced blocks, and long identifiers are exempt, because
wrapping them destroys them.

*(Approximated.*

The checker strips link syntax and emphasis markers, and that approximation is
close enough to report on.

It is not a renderer, and the standard does not ask for one.

A line with no break opportunity below the limit is left alone, because that
is the long-identifier case and no wrap exists to ask for.*)*

### Fenced code obeys its own language

Fenced Python obeys the Python conventions in this document.

**MUST** tag a fence that holds Python with `python`.

An untagged fence is prose to every tool that reads the file, and the rules
that would have caught a defect in it never run.

*(Proved, where the fence holds parseable Python.)*

**SHOULD** tag a shell fence `sh` rather than `bash`, unless the example genuinely
needs Bash-specific behavior.

A fence that deliberately shows a nonconforming example says so in the prose
above it.

---

## 9. Comments and markers

**MUST** use the `todo-comments` vocabulary, and nothing outside it.

| Marker | Carries |
| --- | --- |
| `FIX:` | A known defect, and what is wrong. |
| `HACK:` | A workaround for something outside the project's control, and its exit. |
| `NOTE:` | Context the reader needs and cannot infer from the code. |
| `PERF:` | A choice made for performance, and the measurement. |
| `TEST:` | Something about testing this site. |
| `TODO:` | Deferred work, and the condition that revives it. |
| `WARN:` | A hazard: something that looks safe and is not. |

The upstream vocabulary also defines aliases, and they are permitted because
the upstream specification permits them: `FIXME`, `BUG`, `FIXIT`, and `ISSUE` for `FIX`;
`WARNING` and `XXX` for `WARN`; `OPTIM`, `PERFORMANCE`, and `OPTIMIZE` for `PERF`; `INFO` for
`NOTE`; `TESTING`, `PASSED`, and `FAILED` for `TEST`.

**SHOULD** prefer the primary spelling within one project, so that the same idea
does not appear under two names.

**MUST** include the colon, which is what the tooling matches.

**MUST.**

An ordinary comment carries a marker.

A comment that explains something is one of the seven kinds above, and naming
which one lets a reader searching for hazards find them and lets a reader
skimming for context skip them.

A marker heads a block, so only the first line of a contiguous comment block
carries it.

**The rule reaches every comment the project writes**, including those in its
TOML and YAML.

*(Proved in Python, where the checker parses the file.*

*Review elsewhere, because the checker reads only `.py`.*)*

**The exception is a comment whose syntax belongs to another tool.**

A suppression, a shebang, and a linter directive are read by a program that
defines their form, and a marker inside one would break it.

**A program meant to be run directly carries `#!/usr/bin/env python3`** as its first
line, above the module docstring.

**MUST** give that file the executable bit, so the line is not a claim the
repository contradicts.

**MUST NOT.**

The taxonomy is not a reason to add comments.

It governs comments that already justify their existence, and a pass applying
this section that raised the comment count was applied wrongly.

**`NOTE:` is the default and is therefore overused.**

Before writing one, ask whether the comment warns of a hazard, records a
measurement, or defers work, because those markers carry more information and
someone grepping for hazards should find them.

**MUST NOT.**

A docstring takes no marker.

A docstring says what a thing is for; a comment says why the code beneath it
is written the way it is.

**A comment explains why, not what.**

*(Review.)*

---

## 10. Docstrings

**MUST** use this shape, unconditionally:

```python
"""
Content.
"""
```

The opening `"""` is followed immediately by a newline and the closing
`"""` stands alone.

Never `"""Content."""`, and never content glued to the opening quote.

Single-line docstrings are not exempt.

**MUST.**

A docstring documents the contract of a module, class, or callable, in the
vocabulary a domain or product reader would use.

**MUST NOT.**

Do not restate what the code already says, and do not use a docstring as
somewhere to put an implementation explanation that needs a home.

Implementation rationale, invariants, traps, hazards, performance
observations, and suppression reasons belong in comments, where §9's markers
apply.

**MUST** hold to one sentence per paragraph and to the docstring width in §8.

**SHOULD** add an example only where it clarifies an observable contract, grounded
in the real domain, and the example itself obeys every convention here.

**Python inside a docstring is still Python, and the docstring around it is
still prose.**

The example obeys the code conventions, and the docstring obeys the docstring
width, which is the narrower of the two.

**MUST NOT.**

Do not reword an existing docstring because different words seem clearer.

Mechanical reformatting is expected.

Rewording is only for wording that is objectively incorrect, meaning it
describes behavior the code does not have.

---

## 11. Imports

**MUST** import the names you use, not the modules that contain them, and always
in the parenthesized form:

```python
from pathlib import (
    Path,
)
```

One name per line, a trailing comma after the last name even when there is
only one, and the closing parenthesis on its own line.

**This applies to the standard library.**

There is no exemption for a module because it ships with Python; the
convention is namespace consistency.

**MUST** resolve a collision with an alias that names the origin.

Two kinds collide, and both bite silently.

A **builtin**: `from re import compile` shadows `compile`, so write
`compile as compile_pattern`.

A **project name**: a module that imports `parse` from `ast` and also defines its own
`parse` produces a redefinition and a type error pointing at the wrong function.

**MUST NOT.**

Do not alias to abbreviate.

An alias exists to disambiguate.

### The exceptions, which are semantic

**The module object is what the code uses.**

Some libraries are designed as a namespace and used as one.

**The import must be deferred.**

Where an import has a precondition, or a cost paid on one path only, it goes
inside the function that needs it.

Deferral is orthogonal to form: a deferred import still imports the name.

**The module attribute is a patch target.**

Test code replacing an attribute on a module needs the module object, and code
reading a mutable module-level singleton needs to read it through the module
so a rebinding is visible.

**MUST NOT** invent a fourth reason.

"It is standard library" and "it is shorter" are not reasons.

---

## 12. Layout

Two rules shape every Python file: one statement occupies its own visual
space, and anything bracketed is written vertically.

### 12.1 One statement, one visual space

**MUST.**

Separate every statement from its neighbor with a blank line, even when two
statements are part of the same conceptual operation.

The rule is syntactic, not semantic.

"These two obviously belong together" is not an exemption, and the whole point
is that a reader should not have to decide where one step ends.

```python
def return_book(
    self,
    *,
    returning_patron_id: PatronId,
) -> None:
    if self._status is not LoanStatus.ACTIVE:
        raise LoanNotActiveError(
            "return_book requires an active loan",
        )

    if returning_patron_id != self.patron_id:
        raise UnauthorizedReturnError(
            "only the borrowing patron may return this loan",
        )

    self._status = LoanStatus.RETURNED
```

**This applies inside class bodies**, to dataclass fields, enum members, and
model fields alike.

### 12.2 The control-flow exception has two parts

They are independent, and one check for both gets them wrong.

**MUST NOT.**

There is no blank line between a control-flow header and *that header's own*
first statement.

The first statement is attached to its header, and that covers `if`, `for`, `while`,
`try`, `with`, `match`, a class header, a class docstring, and a function header.

**MUST.**

There is a blank line before the *next* clause header in the same compound
statement, separating it from the previous clause's body.

That covers `elif`, `else`, `except`, `finally`, and `case`.

```python
try:
    return aware_datetime(
        value=value,
    )

except ValueError as exception:
    raise InvalidLoanError(
        str(
            object=exception,
        ),
    ) from exception
```

**MUST** implement this structurally, on `ast.If`, `ast.Try`, and `ast.Match` nodes.

A ternary's `else` is not a clause header, and any check that matches the word
rather than the node will report it.

### 12.2a Import blocks are one declaration

**MUST NOT.**

Do not separate consecutive import statements with blank lines.

An import block is one declaration written across several statements, ordered
by the import convention and by the formatter, and separating its members
fights both.

### 12.3 Top-level separation

**MUST** leave two blank lines between top-level definitions and one blank line
between methods, which is what the formatter produces.

*(Proved, by the formatter.)*

### 12.4 Vertical formatting

**MUST.**

Every argument, parameter, base class, and bracketed-literal element goes on
its own line with a trailing comma.

This covers a function or method **definition**, a **call**, a class's **base list**, and
a **tuple, list, set, or dict literal**.

It applies to a single argument, and to `self`.

```python
class Loan(
    Base,
):
    def __init__(
        self,
        *,
        id: LoanId,
    ) -> None:
        self._id: Final = id
```

```python
width = len(
    line,
)
```

**It covers a destructuring target**, which is bracketed syntax the same way an
argument list is:

```python
for (
    index,
    character,
) in enumerate(
    iterable=segment,
):
    ...
```

The target's own parentheses are optional, and writing them is what makes the
vertical form available.

That reaches a `for` header, a comprehension's `for` clause, and a tuple on the
left of an assignment.

**This is not "wrap when the line gets long."**

A call with one argument is written the same way as a call with five, so a
reader never has to ask whether a short call was left inline deliberately or
by accident.

The mechanism is the formatter's magic trailing comma, so a project keeps
`skip-magic-trailing-comma = false` and writes the comma; the formatter does the
layout.

### 12.5 Where vertical formatting does not reach

**A call with no arguments.**

`Path()` has nothing to put on a line.

**A single-element tuple.**

Its comma is mandatory syntax rather than a magic trailing comma, so it cannot
signal that the literal should be exploded, and the formatter keeps it inline.

**A sole generator argument**, because the language forbids the comma:

```text
tuple(x for x in y,)   SyntaxError: Generator expression must be parenthesized
```

**A bare, unparenthesized tuple value** on the right of an assignment.

Adding a comma there makes the formatter add parentheses and explode it, which
is a structural change rather than a formatting one.

The same shape on the *left* is a destructuring target and is not exempt,
because parenthesizing a target changes nothing the parser or the formatter
does with the rest of the statement.

**A type subscript.**

`tuple[Record, ...]` is not a call and will never gain a third element, so the
vertical form buys no diff stability and costs three lines in a signature the
reader is scanning for its shape:

```python
batch: tuple[Record, ...]

rows_by_id: dict[int, list[int]] = {}
```

Split an annotation only when the line exceeds the column limit.

### 12.6 Calls inside f-strings are not exempt

A replacement field is ordinary code and gets the ordinary treatment:

```python
message = f"the file has {
    len(
        lines,
    )
} lines"
```

This is valid from Python 3.12, and the formatter produces exactly this shape
from a written trailing comma.

**MUST NOT** lift a call out of an f-string to avoid the rule.

---

## 13. Signatures

**MUST.**

A public callable the project owns takes keyword-only parameters, even a
single one.

Public means anything other code is expected to call, inside or outside the
project.

```python
def checkout(
    *,
    book_id: BookId,
    patron_id: PatronId,
) -> Loan: ...
```

**SHOULD.**

A private callable, whose name begins with `_`, takes positional-only
parameters, expressed with `/`.

```python
def _normalize(
    text: str,
    /,
) -> str: ...
```

**The exception is a private helper whose parameters need their names.**

Four or five parameters of the same type are unreadable positionally, and a
keyword-only signature there is the better choice.

It still declares its convention explicitly, which is the part that is not
negotiable.

**An existing public signature that is still positional is converged, not
grandfathered**, including every call site.

A convergence pass that leaves the most visible convention half-applied has
converged nothing.

**SHOULD** inventory the affected call sites first, because a handful is a
different risk from dozens, and that difference decides whether to proceed or
to ask.

**MUST.**

The name and the argument convention agree.

A positional-only signature says the caller is close by and the parameter
names are free to change, and a public name says the opposite.

Where the two disagree one of them is wrong, and which one depends on whether
the callable is genuinely part of the module's surface.

**MUST NOT** leave the boundary implicit.

Positional-or-keyword is Python's default rather than a decision, and a
signature that accepts the default has declared nothing.

**A callable whose only parameter is `self` or `cls` has no boundary to declare**, and
takes neither marker.

**A name the language or a framework dictates is not private for having an
underscore.**

`__eq__` is reached through a slot and never by name, `__init__` is routinely
called with keywords, and a framework's `_meta` is the framework's spelling.

**MUST** read the contract rather than the leading character.

**A callable defined inside another callable is not its module's surface.**

It is reached through the reference the enclosing callable hands out — an
executor's task, a transport's handler, an observer — and never by name from
another module.

The leading-underscore test decides nothing there, because the name is local
either way, and the convention is the one the reference imposes.

**SHOULD** leave such a callable positional-only, and **MUST NOT** rename it to carry
an underscore instead, which would claim a module surface it does not have.

**MUST NOT** mix the two arbitrarily.

A signature with a positional-only group and a keyword-only group claims that
some arguments are structural and some are configuration.

Where that claim is true, mark it; where it is not, pick one.

### Framework-injected signatures

Where a framework inspects a signature and calls the function itself, the
signature is a declaration and there is no caller to protect.

Route handlers, test functions receiving fixtures, and dependency-injected
constructors keep the framework's idiom.

**MUST** read the framework's dispatch source rather than inferring its calling
convention from a signature.

A dispatcher commonly passes its primary context object positionally while
passing named captures as keywords, which means one parameter can become
keyword-only safely and the other cannot.

### External callables

**MUST** respect the signature the callable actually has.

*(Review.)*

**MUST** verify empirically, against both the runtime and the type checker, which
can disagree.

A real case: a hash constructor accepts a keyword at runtime that its bundled
stub names differently, so the call runs and the type checker rejects it.

The type-checker-correct name is the one to use.

**SHOULD** use keywords where the callable genuinely accepts them.

**MUST NOT** invent a keyword name.

`config`, `options`, and `settings` are guesses.

**MUST NOT** generalize from one callable to its neighbors.

Within one class, most methods accept keywords and one does not.

Two mappings in the standard library disagree about the same method name:

```text
{"a": 1}.get(key="a")       TypeError: dict.get() takes no keyword arguments
os.environ.get(key="PATH")  ok
```

`dict.get` is positional-only at the C level and in its stub; `os.environ` is a
`MutableMapping` whose `get` is ordinary Python.

The name is identical, the receiver is not, and only introspection separates
them.

#### The example, reproducible from the standard library

```text
csv.writer(handle)                    ok
csv.writer(csvfile=handle)            TypeError: writer expected at least 1 argument, got 0
csv.writer(handle, dialect="excel")   ok
```

The keyword name is the one the documentation shows, the error names neither
the parameter nor the real problem, and every other argument does take a
keyword.

The same object's `writerow` is positional-only as well, and `inspect.signature`
reports `(row, /)` for it, so introspection answers this one where a guess does
not.

Many single-purpose builtins are positional-only at the C level: `isinstance`,
`hash`, `type`, `len`, `frozenset`, `sorted`, `hasattr`, and `Path(*args)` among them.

**Some conversions are impossible**, not merely undesirable: with
`f(first, *args, **kwargs)` you cannot make `first` a keyword while passing the
rest positionally, so leave the whole call positional.

**MUST** mark a positional call that the convention would otherwise convert with a
`WARN:` comment, so the next pass does not undo it.

### Test doubles

**MUST.**

A double mirrors the real callable's signature, parameter names included.

Once a caller passes a keyword, the real names are part of the contract, and a
double with convenient names fails with an unexpected-keyword error one file
away from the change that caused it.

---

## 14. Types at the boundary

**SHOULD** accept the broadest abstraction the operation genuinely works with, and
return the most precise representation the contract commits to.

A parameter's type is a promise about what the caller may pass, so widening it
costs the callee nothing and frees every caller.

A return type is a promise about what the caller receives, so narrowing it
tells the caller what they may rely on.

| Position | Prefer | Not |
| --- | --- | --- |
| parameter, sequence | `Sequence[T]` | `list[T]`, `tuple[T, ...]` |
| parameter, set | `AbstractSet[T]` | `set[T]`, `frozenset[T]` |
| parameter, mapping | `Mapping[K, V]` | `dict[K, V]` |
| return, sequence | `tuple[T, ...]` | `Sequence[T]` |
| return, set | `frozenset[T]` | `AbstractSet[T]` |
| return, mapping | `MappingProxyType[K, V]` | `Mapping[K, V]` |

**MUST** import these from `collections.abc`, not from `typing`.

**MUST** import `collections.abc.Set` as `AbstractSet`, because the bare name collides
with the builtin `set` and reads as the concrete type.

**A parameter the callee mutates is the exception**, and it says so by accepting
the concrete mutable type.

**Hiding the concrete return type is the other exception**, and it is rare: it
belongs where the representation is genuinely not part of the contract and the
callee intends to change it later.

**A value the caller does not own is the third exception.**

Where a library materializes a mutable container, or requires one, an
immutable type declared locally is decoration: `MappingProxyType` is a view
rather than a freeze, and wrapping a value the next call discards allocates a
proxy while guaranteeing nothing.

**MUST** put the guarantee where the value is owned, which is normally the
type that copies it, and record the reasoning once at that boundary rather
than at every occurrence.

**An annotation is not a conversion.**

Narrowing a return type costs nothing at run time.

`tuple(x)`, `dict(x)`, `frozenset(x)`, and `MappingProxyType(x)` may each allocate.

Change the annotation when it tells the caller something true, and add the
call only when the contract needs the representation it builds.

*(Review.)*

No checker can decide whether an annotation is the broadest one the operation
genuinely works with, because that is a claim about the operation.

A tool can list every conversion in a codebase, which is worth doing before a
review; the reading is the review.

---

## 15. Mutability

**SHOULD** choose the immutable representation whenever the data is only read.

Mutability is a claim that something changes.

Where nothing changes, the claim is false, and a reader has to prove that for
themselves before they can rely on the value.

| Read-only data | Prefer | Not |
| --- | --- | --- |
| a fixed collection of items | `tuple` | `list` |
| a fixed set of members | `frozenset` | `set` |
| a fixed lookup table | `MappingProxyType` | `dict` |

**This reaches locals**, where `Final` is unnecessary because the binding does not
outlive the call.

A local list that is built once and then only read is still a list that says
it will change.

**MUST NOT** replace a mutable representation that earns its place.

An accumulator, a working set the algorithm mutates, and a cache are all
mutable for a reason, and freezing them is a defect rather than a tightening.

**Where two representations satisfy the same contract, prefer the one that
allocates less.**

This section has two reasons, and that is the stronger one.

The first is that a type should not miscommunicate whether a value is owned or
may change; the second is that materializing a value the contract does not
require is work nobody asked for.

**SHOULD** prefer a view or a lazy representation over a copy where the
contract allows one: a slice, a `memoryview`, an iterator consumed once.

**MUST NOT** hand back a view where the caller needs contents and a lifetime
independent of the source, because materializing is then the contract rather
than an expense.

*(Review.*

Whether mutation is required is a question about the algorithm.*)*

---

## 16. Call sites

**MUST.**

Keyword arguments appear in the order the callee declares them.

Keyword order is semantically free, which is exactly why it drifts, and
reading a call against its signature is easy only when the two agree.

For a dataclass without an explicit `__init__`, field order is signature order.

**MUST NOT** invent an order for an external callable whose documentation is
silent.

Say so, and leave the call as it stands.

*(Proved* for a callee defined in the same file.

*Approximated* for an imported callee, which needs the library importable.*)*

---

## 17. Modern Python

**SHOULD** use the construct the language provides for the problem at hand.

**The absence of a construct from a codebase is not an argument against it.**

The question is never whether the project already does this; it is whether
this code is an instance of the problem the construct was introduced to solve.

**The distinction that matters is scope of consequence.**

- **A mechanical conversion** expresses the same semantics in the form the
  language now provides: `X | None` over `Optional[X]`, `list[str]` over `List[str]`,
  `datetime.UTC` over `timezone.utc`, an f-string over `%`, a `Path` method over an
  `os.path` call, `zip(..., strict=True)` over a silent truncation.
  Apply it.
- **A design decision** changes the shape a future reader must follow:
  restructuring control flow, splitting one signature into several,
  introducing a new abstraction.
  Report it.

**MUST NOT** rewrite code with a regular expression when the rule is about
structure.

A pattern matching `Name(` cannot tell a call from a class definition, and
turning a base class into a keyword argument is a syntax-level break that
produces a hundred type errors at once.

**SHOULD** declare a generic with the syntax the language now provides.

`def f[T](...)` and `class C[T]` say what a module-level `TypeVar` said, in the
scope where it actually applies, so an explicit `TypeVar`, `ParamSpec`, or `Generic`
base is worth keeping only where it expresses something the new form cannot.

### Type aliases

**SHOULD** declare a name that stands for a type with `type`.

`type X = ...` creates a lazily evaluated alias, which is what distinguishes a
declared alias from an assignment that happens to hold a type object.

An `X = Callable[...]` assignment in existing code is not evidence against the
construct; it is an alias written before the construct existed.

---

## 18. Enums

**SHOULD** prefer a plain `Enum`.

Reach for `StrEnum` or `IntEnum` only where members must compare equal to a
string or an integer, for a wire format, a database column, or an external
API.

Mixin enums leak: once a member is a string, every string operation on it
silently succeeds.

**SHOULD** name the argument when constructing from a value:

```python
Status(
    value=raw,
)
```

The unqualified form reads as a cast; the keyword says a stored value is being
looked up in a closed set, which is what the call does.

**MUST NOT** apply this with a regular expression, because `Status(` matches the
class definition as well as the call.

*(Review.)*

---

## 19. Declarations

### `@final`

**SHOULD** apply `@final` to every project-owned class that nothing inherits from.

*(Review.)*

Treat it as the rigorous default rather than as an optimization or a taste.

A class left unmarked tells a reader that inheriting from it may be an
intended extension point, and for most classes that is simply untrue.

**MUST** audit the whole inheritance tree before marking one, rather than the file
in hand.

**MUST NOT.**

A class cannot be `@final` if anything inherits from it anywhere in the
codebase.

The common failure is marking a base exception final while writing it and
adding a subclass later, in another file, without returning to remove the
decorator.

**MUST NOT** mark a class whose purpose is to be extended, even when it currently
has no children.

**MUST NOT** mark an enum subclass.

Once an enum defines members the language already forbids subclassing, so the
decorator adds nothing a reader does not have for free.

**A class that is extended can still have final methods.**

Being open to extension is not the same as every member being open to being
overridden, and `@final` on a method is what separates the two.

### `Final`

**SHOULD** apply `Final` to a project-owned binding intended never to be rebound,
including one assigned in `__init__`:

```python
def __init__(
    self,
    *,
    root: Path,
) -> None:
    self._root: Final = root
```

**MUST NOT** mark a binding the program rebinds.

A module-level name reassigned through `global`, or an attribute initialized to
`None` and given a real value later, is mutable across its lifetime and is not
`Final`.

**`Final` constrains the name, not the object.**

Half a guarantee: the name cannot be rebound, and the set it names can still
be added to.

```python
_REQUIRED: Final[set[str]] = {
    "a",
    "b",
}
```

The whole one:

```python
_REQUIRED: Final[frozenset[str]] = frozenset(
    {
        "a",
        "b",
    },
)
```

**SHOULD** choose the immutable representation where the value is semantically
read-only: `frozenset` for a set, `tuple` for a sequence, `MappingProxyType` for a
mapping.

The same reasoning reaches local data.

An ephemeral local does not need `Final`, but a local collection that is only
read should not be a mutable `list` out of habit.

**MUST NOT** freeze a working set the module itself mutates, which is a defect
rather than a tightening.

**MUST NOT** annotate an ordinary local merely to say it is not rebound.

A local's lifetime is the call, so `Final` there tells a reader what the next
ten lines already tell them.

**SHOULD** annotate a local where the reader benefits from the intended type and
inference cannot establish it.

An empty container is the ordinary case, and `out: list[Finding] = []` is the
form.

An anti-corruption boundary is the other, where the annotation states the
representation the project intends rather than the one that arrived.

The same test decides an explicit `Final[T]`: write the parameter where it says
something the right-hand side does not.

### `@override`

**SHOULD** apply `@override` to every method that overrides one inherited from an
actual base in the MRO, and not to one that merely shares a name with
something structurally similar.

---

## 20. Control flow

**Judgment.**

Use `match` where the structure is the point.

A `match` earns its place when it dispatches on the shape or state of one
subject across several cases, especially with destructuring or an
exhaustiveness claim.

An `if`/`elif` chain of two branches is not a candidate, and neither is a
sequence of unrelated guard clauses that happen to be adjacent.

A codebase built on early returns will have no candidates at all, which is a
good outcome rather than a gap.

**Judgment.**

Use `@overload` where the public contract genuinely has more than one shape.

The signal is a return type that depends on an argument, not a function that
has branches.

Branches are internal; overloads are a promise to callers.

---

## 21. Tests

**MUST** write tests with the code, never after.

A suite written afterward tends to assert what the code does.

**MUST NOT** weaken a test to make it pass.

A narrowed assertion, a removed case, or a widened tolerance turns a failing
test into a passing non-test.

**MUST NOT** manufacture a test's precondition to make it green.

Where a test depends on state it does not create, the defect is the
dependency.

**SHOULD** use the UNIX epoch for a date that is a pure reference instant with no
meaning of its own:

```python
NOW: Final = datetime(
    year=1970,
    month=1,
    day=1,
    tzinfo=UTC,
)
```

An arbitrary specific-looking date misleads a reader into thinking the value
matters.

**MUST** confirm per occurrence that the value really is arbitrary before changing
it.

A date that is a deadline, a historical fixture, or part of what is being
tested stays exactly as it is.

### A value that means nothing must not look like it means something

The date rule above is one case of a general one.

A fixture carries two kinds of value: the ones the test is about, and the ones
it needed in order to run.

The second kind is read as the first unless it announces itself, and a reader
who stops to work out why *this* name, *this* sentence, or *this* identifier was
chosen has been sent somewhere the test never meant to point.

**SHOULD** use a placeholder a reader recognizes on sight:

| Kind | Canonical form |
| --- | --- |
| A reference instant with no meaning | The UNIX epoch |
| An identifier, key, or label | `foo`, `bar`, `baz`, `qux` |
| A value that must not resolve | A name that says so, in the vocabulary the system reads: `nonexistent`, `nonexistent-user`, `no-such-file` |
| A host, domain, or address | The names RFC 2606 reserves: `example.com`, `.invalid`, `.test` |

**MUST** verify the placeholder against the system under test rather than assuming
it is inert.

A value is inert only relative to the system reading it, and the metasyntactic
set is not inert everywhere: `bar` is an ordinary English word, so a project
that parses or indexes natural language finds meaning in the one place the
fixture is read, and `test` names a real database on a default PostgreSQL
installation.

The reserved names are the counter-case worth copying, because they were
defined to be inert and can be relied on to stay that way.

**MUST NOT** let a fixture keep provenance it does not need.

A person's name, a product, or a seed from the run that happened to produce
the file are each a fact about the day the test was written rather than about
the behavior.

**Where a project already publishes a canonical example**, in a user interface or
in its documentation, a test that shows a different one has two answers to the
same question.

**SHOULD** converge on the published one, so that changing the example changes it
everywhere.

*(Review.)*

Whether a value carries meaning is a fact about the test, not about the value,
so nothing mechanical decides it.

What a tool can do is find the candidates: a date literal, a personal name, a
string that appears once.

---

## 22. Suppressions

A suppression is a local exception to a mechanical rule, so it obeys §1: the
reason is visible where the departure happens.

**MUST** use the checker's own native syntax and its actual rule name.

A suppression written in another tool's dialect silently suppresses nothing,
and the diagnostic keeps being reported as if the comment were not there.

**MUST** place it on the correct span.

For a violation confined to one line, the comment goes on that line; a comment
on the following closing-parenthesis line does nothing.

**MUST** confirm it took effect.

Re-run the checker and verify both that the diagnostic is gone and that no
unused-suppression diagnostic has appeared about the comment itself.

**MUST** explain a suppression that is not self-evident, in a marker comment above
it saying why the code is right and the checker is wrong.

**MUST NOT** suppress a diagnostic you have not understood.

A suppression is for an intentional, understood mismatch between what the code
does and what static analysis can prove, most often a test that deliberately
passes an invalid input to prove a runtime guard fires.

**MUST NOT** use a suppression to defer work.

That is a `TODO:`, and the diagnostic stays visible until it is done.

**A framework-typing gap is not a suppression.**

Where a checker cannot see through a framework's dynamic machinery, the
diagnostics are a tooling limitation to report as a category, not to silence
line by line.

**A file-wide suppression is a design signal.**

Either the rule is wrong for this project, which belongs in configuration with
a reason, or the file is wrong, which belongs in the file.

---

## 23. Mechanical change

A convention that reaches hundreds of sites is applied by a program, and the
program is the part most likely to be wrong.

**MUST** work on the syntax tree.

A pattern that matches `Name(` cannot tell a call from a class definition, and
rewriting structure with one produces a break that looks like a formatting
change.

**MUST** prove the transformation preserves meaning.

Compare the tree before and against the tree after, ignoring positions, and
reject the file if they differ.

A transformation that only adds a trailing comma, a blank line, or a line
break cannot change the tree, so any difference is a defect in the program.

**MUST** validate each edit rather than the batch.

One bad insertion in a file otherwise correct should cost that insertion, not
the file.

### What to automate

Trailing-comma insertion, blank-line separation, import restructuring, and
docstring reshaping are mechanical: the rule is syntactic and the outcome is
decidable.

### What to do by hand

`@final` placement needs the whole inheritance tree and the design intent.

`@override` placement needs real inheritance distinguished from a shared name.

Keyword conversion for an external call needs the runtime signature and the
type checker's view, per callable.

Whether mutation is required, whether a comment earns its place, and whether a
docstring describes a contract are all judgments a program cannot make.

**MUST NOT** automate a judgment by approximating it.

An approximation that runs everywhere is worse than a rule a person applies
where it matters.

---

## 24. Evidence

**MUST.**

A check that can fail open is not a check.

A pattern invalid for the tool reading it, a resolution strategy that skips
what it cannot resolve, and a check that reads a different layer than the
claim all present as a clean result.

**MUST** give every automated check a positive control: a case it is known to
catch, run beside the real one.

**MUST NOT** report a clean result from a scan you have not proven runs.

A repository-wide search returning zero is either a fact or a broken pattern,
and the two are indistinguishable from the outside.

**MUST** verify at the layer the claim is about.

A claim about what a reader sees is not established by inspecting the buffer
behind the rendering.

**MUST** report what happened.

If a check was skipped, say so.

A qualified result is worth more than a confident one.

**MUST NOT** claim a guarantee an implementation does not provide.

A candidate detector reports candidates.

Presenting its clean run as proof of the convention is the same error as a
check that fails open, arrived at from the other direction.

---

## 25. Git and commits

**MUST** follow Conventional Commits:

```text
<type>(<optional scope>): <description>

<optional body>

<optional footer>
```

| Type | Use |
| --- | --- |
| `build` | Build system, tooling, or dependency versions. |
| `chore` | Maintenance: the initial commit, ignore-file changes. |
| `docs` | Documentation only. |
| `feat` | Adds, adjusts, or removes a feature of the API or UI. |
| `fix` | Resolves a bug in behavior a `feat` introduced. |
| `ops` | Infrastructure, deployment, CI/CD, monitoring, backups. |
| `perf` | A refactor whose specific purpose is performance. |
| `refactor` | Rewrites or restructures code without changing behavior. |
| `style` | Formatting only, with no effect on behavior. |
| `test` | Adds missing tests or corrects existing ones. |

**MUST.**

The scope is optional and names a part of the system, never an issue
identifier.

**MUST.**

The description is imperative and present tense, not capitalized, and does not
end with a period.

Write `add retry to the fetch path`, not `Added retries.`

**MUST** declare a breaking change in the footer, beginning `BREAKING CHANGE:`,
which is also where issue references belong.

**The subject is a structured field, not a paragraph.**

The one-sentence rule does not apply to it and it takes no terminal period.

---

## 26. Adopting this standard

**Reference this document by version and copy only the enforcement.**

1. Name the version in the project's contributor documentation.
2. Vendor `vendor/` into the project, so the rules a tool can check are checked,
   and so the project's own review sees them.
3. Layer project-local configuration on top rather than editing the vendored
   files: code width, source roots, exclusions, and any additional rule sets.
4. Record project-local specializations next to what they specialize.

`docs/adoption.md` gives the minimal path, the full path, and the exact files.

---

## 27. Version

This is the standard at **v1.0.0**.

Changes are recorded in `CHANGELOG.md`, and a project states the version it
conforms to so that a reviewer can tell a violation from a version gap.
