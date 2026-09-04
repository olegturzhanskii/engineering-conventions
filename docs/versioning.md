# Versioning

One version number, because two would be a second thing to keep in sync and
this repository is not large enough to earn that.

## What the version identifies

`v1.0.0` identifies **the standard**.

`STANDARD.md` §27 states it, `CHANGELOG.md` records how it got there, and
`check_conventions.py --version` prints the version its rules implement.

A project reports conformance by naming that version in its contributor
documentation, in one line.

## What a change costs

| Change | Version |
| --- | --- |
| A rule changed such that conforming code may now be non-conforming | **Major** |
| A rule added, or an existing one made checkable for the first time | **Minor** |
| Wording, an example, or an enforcement file with no rule change | **Patch** |

The test is not which file changed.

It is whether a project that conformed yesterday still conforms today.

## The checker may evolve on its own

A fix to the checker that does not change a rule is a **patch**.

The rules it implements are unchanged, so a project that conformed still
conforms, and re-vendoring is optional rather than required.

`STANDARD_VERSION` inside the checker names the standard whose rules it
implements, not its own release.

That is why two vendored copies at different patch levels can both correctly
report `1.0.0`.

## Telling three differences apart

A reviewer looking at a project that differs from the standard has three
possibilities, and the repository is arranged so they are distinguishable
without asking anyone.

**Project-local specialization.**

It is in the project's own configuration, below a comment marking it as local,
and the vendored files differ from upstream only by additions.

**A genuine violation.**

The checker reports it, and no exception is recorded at the site.

**A version gap.**

The project names an older version than the standard currently publishes, and
`CHANGELOG.md` between those two versions explains the difference.

The first two are answered by reading the project.

The third is answered by reading the changelog, which is the whole reason the
version is named rather than the text copied.
