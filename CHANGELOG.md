# Changelog

Versions are what a project names when it says which standard it conforms to.

The format is [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses [semantic versioning](https://semver.org/spec/v2.0.0.html)
with the following meaning.

**Major**: a rule changed such that conforming code may now be non-conforming.

**Minor**: a rule was added, or an existing one was made checkable.

**Patch**: wording, an example, or an enforcement file with no rule change.

## [1.0.1]

### Changed

- §7's structured-material list now reads "a commit or tag subject" where it
  read "a commit subject."
  An annotated tag's first line is a subject in exactly the sense the bullet's
  own rationale describes — splitting it would move a sentence out of the
  structure holding it — and the enumeration simply had not named it.
  Nothing else about the prose rules moves: a commit body, a tag annotation's
  body, and release notes remain prose, and one sentence per paragraph
  continues to govern all three.

### Why this is a patch

A project that conformed to 1.0.0 still conforms.

The change broadens an exemption rather than adding or tightening a rule, so
no conforming project becomes non-conforming, and nothing became checkable —
the checker cannot inspect a tag message at all.

A reviewer could reasonably have argued for a minor bump on the grounds that
the rule's reach changed; this repository's own test in `docs/versioning.md` is
whether a project that conformed yesterday still conforms today, and it does.

## [1.0.0]

The initial release.

### Added

- `STANDARD.md`: twenty-seven numbered sections covering authority, ordering,
  configuration, language and runtime, dependencies, prose, widths, comments,
  docstrings, imports, layout, signatures, boundary types, mutability, call
  sites, modern Python, enums, declarations, control flow, tests,
  suppressions, mechanical change, evidence, and commits.
  Every rule is marked MUST, SHOULD, or judgment, and carries the class of
  enforcement it can actually receive.
- §7 holds prose to American English, no contractions, one sentence per
  paragraph, and the em dash rather than the two hyphens a typewriter had.
  The rules reach prose only, and stop at quoted speech and at an inline code
  span, both of which §7 lists among the things prose rules do not reach.
- §8 separates the docstring width from the comment width, because a docstring
  is read as a rendered tooltip and a comment is read beside the code at the
  code's own width.
- §13 gives a callable's boundary marker a rule rather than a default: a
  public name takes `*`, a private one takes `/`, a name the language or a
  framework owns takes neither, and a callable defined inside another callable
  is not its module's surface at all — it is reached through the reference the
  enclosing callable hands out, and the convention is the one that reference
  imposes.
  For a callable the project does not own, the signature is verified against
  both the runtime and the type checker, which can disagree; two reproducible
  pairs are given, one from `csv` and one where `dict.get` rejects a keyword that
  `os.environ.get` accepts under the same method name.
- §14 and §15 separate an annotation from a runtime conversion, and prefer the
  representation that allocates less where two satisfy the same contract.
- §21 requires a test to be written with the code, forbids weakening one to
  make it pass, forbids depending on state it does not create, and gives the
  canonical placeholder for a fixture value that carries no meaning — with the
  requirement to verify that placeholder against the system under test, since
  a value is inert only relative to the system reading it.
- `vendor/ruff/`: the Ruff configuration the standard implies, as a standalone
  file and as a manifest fragment, documenting both the rule families selected
  and the three that look relevant and are not.
- `vendor/taplo/taplo.toml`: the TOML formatter configuration, because the
  vertical form of an array does not survive a default `taplo fmt`.
- `vendor/tools/check_conventions.py`: eleven checks for the rules a formatter
  cannot express, Markdown among them, separating proved violations from
  candidates that need review.
  Twenty-nine controls run under `--self-test`: twenty snippets, one per
  construct a check covers, and nine exemption controls written so that a rule
  which stopped reaching a construct and a rule which reported everything both
  fail.
- `vendor/tools/check_commit_message.py`: the Conventional Commits subject,
  body, and footer form.
- `docs/adoption.md`, `docs/versioning.md`, and `docs/workflow.md`.
- `LICENSE` and `NOTICE`: Apache-2.0, chosen over a shorter permissive license
  for §4(b), which requires a modified file to say that it was modified.
- `sandbox/`: a complete miniature project that has adopted the standard, with
  its own manifest and gate, a vendored copy of the checker, recorded
  exceptions, and a `counterexamples/` directory the gate deliberately excludes.
