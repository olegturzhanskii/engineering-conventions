"""
COUNTEREXAMPLE — this file breaks a rule on purpose.

Do not copy it.

Breaks: import the names you use, not the modules that contain them (§11).
"""

import json
import os


def load(path):
    with open(os.path.join(path, "config.json")) as handle:
        return json.load(handle)
