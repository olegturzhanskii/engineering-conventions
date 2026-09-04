"""
Timezone-aware domain timestamps.
"""

from datetime import (
    datetime,
)
from typing import (
    final,
)


@final
class InvalidTimestampError(
    ValueError,
):
    """
    Raised when a domain timestamp is missing timezone information.
    """


def aware_datetime(
    *,
    value: datetime,
    field_name: str,
) -> datetime:
    """
    Return `value` after validating that it is timezone-aware.
    """

    if not isinstance(
        value,
        datetime,
    ):
        received = type(
            value,
        ).__name__

        raise InvalidTimestampError(
            f"{field_name} requires datetime, got {received}",
        )

    if value.tzinfo is None or value.utcoffset() is None:
        raise InvalidTimestampError(
            f"{field_name} requires a timezone-aware datetime",
        )

    return value
