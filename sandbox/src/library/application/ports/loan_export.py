"""
The port the export use case needs.

A `Protocol`, not a base class, so an adapter satisfies it by having the right
shape rather than by inheriting.
"""

from collections.abc import (
    Sequence,
)
from typing import (
    Protocol,
    runtime_checkable,
)

from library.domain.loan import (
    Loan,
)


# NOTE:
# Not `@final`, and the rule that would otherwise ask for it does not reach a `Protocol`.
#
# Nothing inherits from this class here, which is the usual trigger, but closing a protocol would forbid the one thing
# a protocol is declared for.
@runtime_checkable
class LoanExport(
    Protocol,
):
    """
    Writes a set of loans somewhere outside the application.

    The application states what it needs here and never learns which adapter
    supplies it.
    """

    # NOTE:
    # Keyword-only because a port is the widest surface in the project.
    #
    # Every adapter written from now on repeats this signature, and a positional one would make the parameter order
    # part of the contract that all of them share.
    def write(
        self,
        *,
        loans: Sequence[Loan],
    ) -> int:
        """
        Write `loans` and return how many rows were written.
        """

        ...
