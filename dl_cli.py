from __future__ import annotations

import json
import sys

from defiant_generator_v0_1 import GeneratorError, generate_and_validate
from defiant_parser_v0_3_0 import DefiantParseError


def main() -> int:
    if len(sys.argv) != 2:
        print("python dl_cli.py <intent.json>")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
