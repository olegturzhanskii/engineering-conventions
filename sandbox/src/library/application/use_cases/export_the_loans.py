"""
Export a set of loans through whatever adapter the caller supplies.

The use case knows the port and nothing about the adapter, which is what lets
the same code write a CSV file, a table, or a test double.
"""

from collections.abc import (
    Sequence,
)
from typing import (
    final,
)

from library.application.ports.loan_export import (
    LoanExport,
)
from library.domain.loan import (
    Loan,
    LoanStatus,
)


@final
class NothingToExportError(
    ValueError,
):
    """
    Raised when the caller asks to export an empty selection.
    """


def export_the_loans(
    *,
    loans: Sequence[Loan],
    destination: LoanExport,
    only_returned: bool = False,
) -> int:
    """
    Write `loans` through `destination` and return how many rows were written.

    An empty selection is refused rather than exported, because a file with a
    header and no rows is indistinguishable from a successful export of
    nothing.
    """

    selected = _select(
        loans,
        only_returned=only_returned,
    )

    if not selected:
        raise NothingToExportError(
            "no loans matched the selection",
        )

    return destination.write(
        loans=selected,
    )


# NOTE:
# The one signature in this package that declares both boundaries.
#
# `loans` is what the helper is about and `only_returned` is how it behaves, which is the claim a mixed signature
# makes; where that claim is not true, one of the two markers is the whole signature.
def _select(
    loans: Sequence[Loan],
    /,
    *,
    only_returned: bool,
) -> tuple[Loan, ...]:
    """
    Return the loans the caller asked to export.
    """

    if not only_returned:
        return tuple(
            loans,
        )

    return tuple(loan for loan in loans if loan.status is LoanStatus.RETURNED)
