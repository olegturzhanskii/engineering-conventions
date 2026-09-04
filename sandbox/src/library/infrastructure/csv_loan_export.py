"""
A `LoanExport` adapter that writes comma-separated rows to a file.

One row per loan, under a fixed header, in the column order the header names.
"""

from collections.abc import (
    Sequence,
)
from csv import (
    writer,
)
from pathlib import (
    Path,
)
from typing import (
    Final,
    final,
)

from library.domain.loan import (
    Loan,
)

_HEADER: Final = (
    "loan_id",
    "book_id",
    "patron_id",
    "status",
    "returned_at",
)


@final
class CsvLoanExport:
    """
    Writes loans to a file, one row each, with a header.

    Satisfies `LoanExport` structurally.

    It does not import the port, because an adapter with the right shape needs
    no declaration to prove it, and the dependency would point the wrong way.
    """

    def __init__(
        self,
        *,
        path: Path,
    ) -> None:
        self._path: Final = path

    def write(
        self,
        *,
        loans: Sequence[Loan],
    ) -> int:
        with self._path.open(
            mode="w",
            encoding="utf-8",
            newline="",
        ) as handle:
            # WARN:
            # The file argument is passed positionally, and it has to be.
            #
            # `csv.writer` is implemented in C and its first parameter positional-only: `writer(csvfile=handle)`
            # raises `TypeError: writer expected at least 1 argument, got 0`, which names neither the parameter nor
            # the real problem.
            #
            # Every other argument does take a keyword, so `dialect=` below is written the way the convention prefers.
            #
            # The rule is per callable, not per library.
            rows = writer(
                handle,
                dialect="excel",
            )

            # WARN:
            # `writerow` is positional-only as well, for the same reason as `writer` above: `writerow(row=...)` raises
            # `TypeError: writer.writerow() takes no keyword arguments`.
            #
            # Unlike `writer`, this one does introspect: `inspect.signature` reports `(row, /)`.
            rows.writerow(
                _HEADER,
            )

            for loan in loans:
                rows.writerow(
                    _row(
                        loan,
                    ),
                )

        return len(
            loans,
        )


def _row(
    loan: Loan,
    /,
) -> tuple[str, str, str, str, str]:
    returned_at = loan.returned_at

    return (
        str(
            loan.id,
        ),
        str(
            loan.book_id,
        ),
        str(
            loan.patron_id,
        ),
        str(
            loan.status,
        ),
        returned_at.isoformat() if returned_at is not None else "",
    )
