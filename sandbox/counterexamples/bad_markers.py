"""
COUNTEREXAMPLE — this file breaks a rule on purpose.

Do not copy it.

Breaks: the comment rules in §9, in three ways that the checker treats
differently.
"""

# An ordinary comment with no marker at all.
TIMEOUT = 30

# FIXIT2: a marker-shaped word that is not in the vocabulary.
BACKOFF = 2

# FIXME: a permitted alias where the project should prefer `FIX:`.
#
# The checker accepts this one, because the standard permits the aliases and
# preferring a spelling within one project is a project decision.
#
# It is here to show a rule that stays with review.
LIMIT = 10

# XXX: the same, where the project should prefer `WARN:`.
RETRIES = 3
