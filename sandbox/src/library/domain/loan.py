"""
A concrete loan of one book to one patron.

This is an operational record: it tracks who is borrowing what and when it was
returned.

It does not decide borrowing policy, such as loan limits or renewal rules;
those belong to a future lending-policy concept.
"""

from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
)
from enum import (
    auto,
)
from typing import (
    final,
    override,
)

from library.domain.shared.enums import (
    UnorderedStrEnum,
)
from library.domain.shared.identifiers import (
    BookId,
    LoanId,
    PatronId,
)
from library.domain.shared.time import (
    aware_datetime,
)


# WARN:
# Not `@final`: `LoanNotActiveError` and `UnauthorizedReturnError` below both extend this class.
#
# A base exception is where the decorator goes wrong most often, because the question is asked while the class is
# being written and the subclass arrives afterward — sometimes, as here, later in the same file.
class InvalidLoanError(
    ValueError,
):
    """
    Raised when a loan would contain invalid data.
    """


@final
class LoanNotActiveError(
    InvalidLoanError,
):
    """
    Raised when an operation requires an active loan that has already ended.
    """


@final
class UnauthorizedReturnError(
    InvalidLoanError,
):
    """
    Raised when someone other than the borrowing patron returns the book.
    """


class LoanStatus(
    UnorderedStrEnum,
):
    """
    Lifecycle state of a loan.
    """

    ACTIVE = auto()

    RETURNED = auto()


def _aware(
    value: datetime,
    field_name: str,
    /,
) -> datetime:
    try:
        return aware_datetime(
            value=value,
            field_name=field_name,
        )

    except ValueError as exception:
        raise InvalidLoanError(
            str(
                object=exception,
            ),
        ) from exception


# NOTE:
# `eq=False` is what makes the entity identity below reachable.
#
# A dataclass generates a structural `__eq__` by default, and a generated method defined in the class body would
# shadow the one written underneath it.
@dataclass(
    eq=False,
    kw_only=True,
    slots=True,
)
@final
class Loan:
    """
    A book currently or previously on loan to a patron.

    A loan is an entity: it has an identity of its own, so a loan that changes
    status is still the same loan, and two loans are equal exactly when their
    ids match.
    """

    id: LoanId

    book_id: BookId

    patron_id: PatronId

    borrowed_at: datetime

    _status: LoanStatus = field(
        default=LoanStatus.ACTIVE,
        init=False,
    )

    _returned_at: datetime | None = field(
        default=None,
        init=False,
    )

    def __post_init__(
        self,
    ) -> None:
        self.borrowed_at = _aware(
            self.borrowed_at,
            "borrowed_at",
        )

    @property
    def status(
        self,
    ) -> LoanStatus:
        return self._status

    @property
    def returned_at(
        self,
    ) -> datetime | None:
        return self._returned_at

    def return_book(
        self,
        *,
        returning_patron_id: PatronId,
        at: datetime,
    ) -> None:
        """
        Record the book as returned by the borrowing patron.
        """

        if self._status is not LoanStatus.ACTIVE:
            raise LoanNotActiveError(
                f"return_book() requires an active loan, got {self._status}",
            )

        if returning_patron_id != self.patron_id:
            raise UnauthorizedReturnError(
                "only the borrowing patron may return this loan",
            )

        self._status = LoanStatus.RETURNED

        self._returned_at = _aware(
            at,
            "return_book() at",
        )

    @override
    def __eq__(
        self,
        other: object,
        /,
    ) -> bool:
        if not isinstance(
            other,
            Loan,
        ):
            return NotImplemented

        return self.id == other.id

    @override
    def __hash__(
        self,
    ) -> int:
        return hash(
            self.id,
        )


def checkout(
    *,
    book_id: BookId,
    patron_id: PatronId,
    borrowed_at: datetime,
) -> Loan:
    """
    Start a new loan of a book to a patron.
    """

    return Loan(
        id=LoanId.new(),
        book_id=book_id,
        patron_id=patron_id,
        borrowed_at=borrowed_at,
    )
