"""
COUNTEREXAMPLE — this file breaks a rule on purpose.

Do not copy it.

Breaks: a callable is positional-only if private and keyword-only if public,
and neither is left implicit (§13).
"""


def render(template, context):
    return template.format(**context)


def _normalize(text, locale):
    return text.strip().lower()
