"""
Tests for `library.domain.loan`.

Each one states a rule the loan enforces about itself: who may return it, and
that it can only be returned once.
"""

from datetime import (
    UTC,
    datetime,
)
from typing import (
    Final,
)

from pytest import (
    raises,
)

from library.domain.loan import (
    LoanNotActiveError,
    LoanStatus,
    UnauthorizedReturnError,
    checkout,
)
from library.domain.shared.identifiers import (
    BookId,
    IdentifierError,
    PatronId,
)

# NOTE:
# A pure reference instant with no product meaning of its own.
#
# Every assertion below cares only about state transitions, never about this specific date, so the UNIX epoch says
# that plainly where an arbitrary recent date would invite a reader to look for significance that is not there.
NOW: Final = datetime(
    year=1970,
    month=1,
    day=1,
    tzinfo=UTC,
)


def test_returning_a_loan_records_the_returning_patron() -> None:
    patron_id = PatronId.new()

    loan = checkout(
        book_id=BookId.new(),
        patron_id=patron_id,
        borrowed_at=NOW,
    )

    loan.return_book(
        returning_patron_id=patron_id,
        at=NOW,
    )

    assert loan.status is LoanStatus.RETURNED

    assert loan.returned_at == NOW


def test_only_the_borrowing_patron_can_return_the_loan() -> None:
    loan = checkout(
        book_id=BookId.new(),
        patron_id=PatronId.new(),
        borrowed_at=NOW,
    )

    with raises(
        expected_exception=UnauthorizedReturnError,
    ):
        loan.return_book(
            returning_patron_id=PatronId.new(),
            at=NOW,
        )


def test_an_already_returned_loan_cannot_be_returned_again() -> None:
    patron_id = PatronId.new()

    loan = checkout(
        book_id=BookId.new(),
        patron_id=patron_id,
        borrowed_at=NOW,
    )

    loan.return_book(
        returning_patron_id=patron_id,
        at=NOW,
    )

    with raises(
        expected_exception=LoanNotActiveError,
    ):
        loan.return_book(
            returning_patron_id=patron_id,
            at=NOW,
        )


def test_patron_id_rejects_a_non_uuid_value() -> None:
    # WARN:
    # `PatronId.__init__` is typed to accept a `UUID`.
    #
    # Passing a plainly invalid string is an *intentional* type violation — this test exists specifically to prove the
    # runtime check fires — so it is suppressed with `ty`'s own rule name rather than weakened or deleted.
    #
    # Placement matters: for a single-line diagnostic the comment must sit on that exact line, not on a following
    # closing-parenthesis line.
    with raises(
        expected_exception=IdentifierError,
    ):
        PatronId(
            value="not-a-uuid",  # ty: ignore[invalid-argument-type]
        )
