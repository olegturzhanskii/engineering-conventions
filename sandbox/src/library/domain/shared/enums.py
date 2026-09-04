"""
A shared base for closed sets of domain labels.

A label identifies a state; it does not place that state on a scale, and
nothing in the domain may order two of them.
"""

from enum import (
    StrEnum,
)
from typing import (
    override,
)


# NOTE:
# Not `@final`: every concrete label set in this package extends this class, which is what it is for.
#
# The children need no decorator either, because a `StrEnum` that defines members already cannot be extended.
class UnorderedStrEnum(
    StrEnum,
):
    """
    A closed set of labels that serialize as their own string value.

    Members compare equal to that string, so a stored label round-trips, and
    no member is greater or less than another.
    """

    # WARN:
    # `StrEnum` members inherit `str`'s ordering, so `ACTIVE < RETURNED` succeeds and answers alphabetically.
    #
    # The answer is meaningless and the expression says nothing about that, so the four ordering operations refuse
    # here rather than inherit.
    #
    # `/` is written on each of them because the interpreter reaches a comparison through a slot and never by name:
    # the boundary is positional whether or not it is declared, and declaring it keeps every signature in this
    # package readable under one convention.
    @override
    def __lt__(
        self,
        other: object,
        /,
    ) -> bool:
        return NotImplemented

    @override
    def __le__(
        self,
        other: object,
        /,
    ) -> bool:
        return NotImplemented

    @override
    def __gt__(
        self,
        other: object,
        /,
    ) -> bool:
        return NotImplemented

    @override
    def __ge__(
        self,
        other: object,
        /,
    ) -> bool:
        return NotImplemented
