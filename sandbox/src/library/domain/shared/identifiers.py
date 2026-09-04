"""
Small, type-safe identifiers shared across the library domain.
"""

from dataclasses import (
    dataclass,
)
from typing import (
    Self,
    final,
    override,
)
from uuid import (
    UUID,
    uuid4,
)


@final
class IdentifierError(
    ValueError,
):
    """
    Raised when an identifier has an invalid value.
    """


def _uuid(
    value: UUID | str,
    owner: str,
    /,
) -> UUID:
    if isinstance(
        value,
        UUID,
    ):
        return value

    if isinstance(
        value,
        str,
    ):
        try:
            return UUID(
                hex=value,
            )
        except ValueError as exception:
            raise IdentifierError(
                f"{owner} requires a valid UUID, got {value!r}",
            ) from exception

    received = type(
        value,
    ).__name__

    raise IdentifierError(
        f"{owner} requires a UUID or UUID string, got {received}",
    )


# NOTE:
# Not `@final`: every concrete identifier below extends this class, which is the only reason it exists.
#
# Two of its methods are `@final` even so.
#
# A class open to extension does not make every member of it open to being overridden, and these two are the identity
# contract rather than a default.
@dataclass(
    frozen=True,
    slots=True,
)
class _UuidIdentifier:
    """
    A nominal identifier carrying one UUID.

    Each concrete subclass is a distinct type, so a `BookId` is never
    interchangeable with a `PatronId` even though both hold a UUID.
    """

    value: UUID

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "value",
            _uuid(
                self.value,
                type(
                    self,
                ).__name__,
            ),
        )

    @classmethod
    @final
    def new(
        cls,
    ) -> Self:
        return cls(
            uuid4(),
        )

    @override
    @final
    def __str__(
        self,
    ) -> str:
        return str(
            object=self.value,
        )


@dataclass(
    frozen=True,
    kw_only=True,
    slots=True,
)
@final
class BookId(
    _UuidIdentifier,
):
    """
    Identifies one catalog book, independent of any specific copy.
    """


@dataclass(
    frozen=True,
    kw_only=True,
    slots=True,
)
@final
class LoanId(
    _UuidIdentifier,
):
    """
    Identifies one loan of a book to a patron.
    """


@dataclass(
    frozen=True,
    kw_only=True,
    slots=True,
)
@final
class PatronId(
    _UuidIdentifier,
):
    """
    Identifies one library patron.
    """
