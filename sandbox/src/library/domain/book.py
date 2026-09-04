"""
A catalog book: a stable work identity independent of any physical or digital
copy a patron might borrow.
"""

from dataclasses import (
    dataclass,
)
from typing import (
    final,
)

from library.domain.shared.identifiers import (
    BookId,
)


@final
class InvalidBookError(
    ValueError,
):
    """
    Raised when book data is invalid.
    """


def _non_empty(
    value: str,
    field_name: str,
    /,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value.strip()
    ):
        raise InvalidBookError(
            f"{field_name} requires a non-empty string",
        )

    return value.strip()


@dataclass(
    frozen=True,
    kw_only=True,
    slots=True,
)
@final
class Book:
    """
    A catalog entry for one distinct work.

    A book is a value: it has no identity beyond the data recorded about it,
    so two books with the same title and author are the same book.
    """

    id: BookId

    title: str

    author: str

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "title",
            _non_empty(
                self.title,
                "title",
            ),
        )

        object.__setattr__(
            self,
            "author",
            _non_empty(
                self.author,
                "author",
            ),
        )


def catalog_book(
    *,
    title: str,
    author: str,
) -> Book:
    """
    Add a new, distinct work to the catalog.
    """

    return Book(
        id=BookId.new(),
        title=title,
        author=author,
    )
