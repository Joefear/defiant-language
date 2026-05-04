"""DGCE Stage 2 Preview stub.

This is not DGCE execution. It is a preview-only entry point for:
intent JSON -> deterministic DL -> parser AST.
"""

from __future__ import annotations

import json
import pprint
import sys

from defiant_generator_v0_1 import GeneratorError, generate_and_validate
from defiant_parser_v0_2_5 import DefiantParseError


def main() -> int:
    if len(sys.argv) != 2:
        print("python dl_stage2_preview.py <intent.json>")
        return 1

    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as handle:
            intent_dict = json.load(handle)
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {path}: {exc.msg}")
        return 1

    try:
        result = generate_and_validate(intent_dict)
    except (GeneratorError, DefiantParseError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(result["dl"], end="")
    print("\n--- AST Preview ---")
    pprint.pprint(result["ast"], sort_dicts=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
