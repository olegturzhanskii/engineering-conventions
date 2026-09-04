"""
COUNTEREXAMPLE — this file breaks a rule on purpose.

Do not copy it.

Breaks: keyword arguments appear in the order the callee declares them (§16).
"""


def connect(
    *,
    host: str,
    port: int,
    timeout: float,
) -> str:
    return f"{host}:{port}/{timeout}"


session = connect(
    timeout=5.0,
    host="example",
    port=8080,
)
