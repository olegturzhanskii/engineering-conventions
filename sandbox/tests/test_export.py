"""
The application layer and its adapter.

`TestExportTheLoans` uses a double that mirrors the port exactly, and
`TestCsvLoanExport` exercises the real adapter against a real file, because
the lesson that adapter carries is about a real library's real signature.
"""

from collections.abc import (
    Sequence,
)
from datetime import (
    UTC,
    datetime,
)
from pathlib import (
    Path,
)
from typing import (
    Final,
    final,
)

from pytest import (
    raises,
)

from library.application.use_cases.export_the_loans import (
    NothingToExportError,
    export_the_loans,
)
from library.domain.loan import (
    Loan,
    checkout,
)
from library.domain.shared.identifiers import (
    BookId,
    PatronId,
)
from library.infrastructure.csv_loan_export import (
    CsvLoanExport,
)

NOW: Final = datetime(
    year=1970,
    month=1,
    day=1,
    tzinfo=UTC,
)


# WARN:
# `write` below mirrors the port down to the parameter name.
#
# A double given a more convenient signature passes here and the real adapter fails in production, one file away from
# the test that was supposed to cover it.
@final
class _RecordingExport:
    """
    A `LoanExport` that keeps what it was given instead of writing it.
    """

    def __init__(
        self,
    ) -> None:
        self.written: tuple[Loan, ...] = ()

    def write(
        self,
        *,
        loans: Sequence[Loan],
    ) -> int:
        self.written = tuple(
            loans,
        )

        return len(
            loans,
        )


def _loan(
    patron_id: PatronId,
    /,
) -> Loan:
    return checkout(
        book_id=BookId.new(),
        patron_id=patron_id,
        borrowed_at=NOW,
    )


@final
class TestExportTheLoans:
    def test_every_loan_reaches_the_adapter(
        self,
    ) -> None:
        destination = _RecordingExport()

        loans = (
            _loan(
                PatronId.new(),
            ),
        )

        assert (
            export_the_loans(
                loans=loans,
                destination=destination,
            )
            == 1
        )

        assert destination.written == loans

    def test_an_empty_selection_is_an_error_not_an_empty_file(
        self,
    ) -> None:
        patron_id = PatronId.new()

        loans = (
            _loan(
                patron_id,
            ),
        )

        with raises(
            expected_exception=NothingToExportError,
        ):
            export_the_loans(
                loans=loans,
                destination=_RecordingExport(),
                only_returned=True,
            )


@final
class TestCsvLoanExport:
    def test_a_header_and_one_row_per_loan(
        self,
        *,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "loans.csv"

        loans = (
            _loan(
                PatronId.new(),
            ),
            _loan(
                PatronId.new(),
            ),
        )

        assert (
            CsvLoanExport(
                path=path,
            ).write(
                loans=loans,
            )
            == 2
        )

        lines = path.read_text(
            encoding="utf-8",
        ).splitlines()

        assert lines[0].startswith(
            "loan_id,",
        )

        assert (
            len(
                lines,
            )
            == 3
        )
