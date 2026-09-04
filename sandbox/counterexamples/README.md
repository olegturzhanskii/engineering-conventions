# Counterexamples

**Every file in this directory violates the conventions on purpose.**

They are teaching material.

Correcting them would destroy what they show, which is why `pyproject.toml`
excludes this directory from the project's gate and why this file says so out
loud.

`STANDARD.md` §1, *Normative and demonstrative material*, is the rule that makes
this legitimate: a repository that quietly corrects its own counterexamples
has removed its teaching material to score a clean report.

| File | Rule it breaks | Where the rule is |
| --- | --- | --- |
| `bad_imports.py` | Import the names you use, not the modules that contain them. | §11 |
| `bad_signatures.py` | Private functions positional-only, public keyword-only, never mixed by accident. | §13 |
| `bad_kwargs.py` | Keyword arguments in the order the callee declares them. | §16 |
| `bad_markers.py` | A marker on every ordinary comment, spelled from the vocabulary. | §9 |

`bad_markers.py` carries one more defect than the table names, deliberately: a
permitted alias where the project should prefer the primary spelling.

The checker accepts it, because the standard permits the aliases and
preferring one is a project decision, so that line stays with review.

## Seeing the checker catch them

```sh
make demo-violation
```

The gate does not scan this directory.

Pointing the checker at it directly is how the demonstration works, and it is
also the positive control that proves the checker is running at all.
